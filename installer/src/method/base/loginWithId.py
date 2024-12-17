# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import time, asyncio
from typing import Dict, List
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.common.exceptions import TimeoutException

# 自作モジュール
from .utils import Logger
from .elementManager import ElementManager
from .driverWait import Wait
from .decorators import Decorators
from .driverDeco import jsCompleteWaitDeco, InputDeco, ClickDeco
from .sql_exists import SqliteExistsHandler
from .sql_io_manager import SqliteInsert, SqliteUpdate, SqliteRead, SqliteBuckup


from constSqliteTable import TableSchemas
from const_element import LoginInfo
from const_str import StatusName, FileName

decoInstance = Decorators(debugMode=True)
decoJsInstance = jsCompleteWaitDeco(debugMode=True)
decoInstanceInput = InputDeco(debugMode=True)
decoInstanceClick = ClickDeco(debugMode=True)


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************


class SingleSiteIDLogin:
    def __init__(self, chrome: WebDriver, debugMode=True):
        # logger
        self.getLogger = Logger(__name__, debugMode=debugMode)
        self.logger = self.getLogger.getLogger()

        self.chrome = chrome

        # インスタンス
        self.element = ElementManager(chrome=chrome, debugMode=debugMode)
        self.wait = Wait(chrome=self.chrome, debugMode=debugMode)

        self.db_file_name=FileName.DB_FILE_NAME.value
        self.table_pattern_info=TableSchemas.TABLE_PATTERN.value
        self.logger.debug(f'\nself.db_file_name: {self.db_file_name}\nself.table_pattern_info: {self.table_pattern_info}')


# ----------------------------------------------------------------------------------
# Cookieログイン
# reCAPTCHA OK → 調整必要 → 待機時間を180秒

    @decoInstance.funcBase
    async def flow_cookie_save(self, login_url: str, login_info: dict, table_name: str, timeout: int =180):
        # DBファイルの初期化確認
        with SqliteExistsHandler(db_file_name=self.db_file_name, table_pattern_info=self.table_pattern_info) as sqlite_exists:
            sqlite_exists.flow_db_start_check()

        # ログインの実施
        self.flowLoginID(login_url=login_url, login_info=login_info, timeout=timeout)

        # Cookieの取得
        cookie = self._getCookie()

        # CookieデータがDBの項目に入れられるように整理する
        sorted_cookie = self._sort_cookie(cookie=cookie)
        self.logger.info(f'sorted_cookie: {sorted_cookie}')

        # ここに指定のテーブルのnameによって分岐
        with SqliteRead(db_file_name=self.db_file_name, table_pattern_info=self.table_pattern_info) as sqlite_read:
            table_all_data = sqlite_read._read_data(table_name=table_name)

        # テーブルデータから行ごとにデータを抽出
        rows = [row for row in table_all_data]
        self.logger.debug(f'rows: {[dict(row) for row in rows]}')

        # テーブルにデータがない場合をチェック
        if not rows:
            self.logger.warning(f"{table_name} テーブルに既存のデータがありません")
            table_cookie_name = None
        else:
            table_cookie_name = rows[0]['name']  # 'name' キーが存在しない場合を考慮

        # Cookieデータをリストとして渡す
        cookie_data_list = sorted_cookie if isinstance(sorted_cookie, list) else [sorted_cookie]

        # Cookie情報が入っているかどうかで分岐
        if table_cookie_name:
            # 入っている場合にはアップデートを実施
            filter_keys = {"name": table_cookie_name}
            with SqliteUpdate(db_file_name=self.db_file_name, table_pattern_info=self.table_pattern_info) as sqlite_update:
                sqlite_update._update_data(update_data_list=cookie_data_list, table_name=table_name, filter_keys=filter_keys)
            self.logger.info(f"{table_name} のCookieデータを更新しました")

        else:
            # テーブルに情報がまだ入ってないため挿入
            with SqliteInsert(db_file_name=self.db_file_name, table_pattern_info=self.table_pattern_info) as sqlite_insert:
                sqlite_insert._insert_data(insert_data_list=cookie_data_list, table_name=table_name)
            self.logger.info(f"{table_name} に新しくCookieデータを挿入しました")

        # バックアップの実施
        sqlite_backup = SqliteBuckup(db_file_name=self.db_file_name)
        sqlite_backup._data_buck_up()



# ----------------------------------------------------------------------------------
# IDログイン
# reCAPTCHA OK

    def flowLoginID(self, login_url: str, login_info: dict, timeout: int):
        self.logger.debug(f'login_info: {login_info}')

        # サイトを開いてCookieを追加
        self.openSite(login_url=login_url)

        self.inputId(by=login_info['ID_BY'], value=login_info['ID_VALUE'], inputText=login_info['ID_TEXT'])

        self.inputPass(by=login_info['PASS_BY'], value=login_info['PASS_VALUE'], inputText=login_info['PASS_TEXT'])

        # クリックを繰り返しPOPUPがなくなるまで繰り返す
        self.click_login_btn_in_recaptcha(by=login_info['BTN_BY'], value=login_info['BTN_VALUE'])

        # 検索ページなどが出てくる対策
        # PCのスペックに合わせて設定
        self.wait.jsPageChecker(chrome=self.chrome, timeout=10)

        # reCAPTCHA対策を完了確認
        return self.login_element_check(by=login_info['LOGIN_AFTER_ELEMENT_BY'], value=login_info['LOGIN_AFTER_ELEMENT_VALUE'], timeout=timeout)


# ----------------------------------------------------------------------------------



    @decoJsInstance.jsCompleteWait
    def openSite(self, login_url: str):
        return self.chrome.get(url=login_url)


# ----------------------------------------------------------------------------------


    def currentUrl(self):
        try:
            currentUrl = self.chrome.current_url
            self.logger.debug(f"currentUrl: {currentUrl}")
        except Exception as e:
            self.logger.error(f"なにかしらのエラー{e}")
        return currentUrl


# ----------------------------------------------------------------------------------
# IDの取得

    @decoInstanceInput.inputWait
    def inputId(self, by: str, value: str, inputText: str):
        return self.element.clickClearInput(by=by, value=value, inputText=inputText)


# ----------------------------------------------------------------------------------
# passの入力

    @decoInstanceInput.inputWait
    def inputPass(self, by: str, value: str, inputText: str):
        return self.element.clickClearInput(by=by, value=value, inputText=inputText)


# ----------------------------------------------------------------------------------
# ログインボタン押下

    def clickLoginBtn(self, by: str, value: str):
        self.logger.debug(f'value: {value}')
        return self.element.clickElement(by=by, value=value)


# ----------------------------------------------------------------------------------
# ログインボタン押下
# reCAPTCHA

    def click_login_btn_in_recaptcha(self, by: str, value: str):
        self.logger.debug(f'value: {value}')
        return self.element.recaptcha_click_element(by=by, value=value)


# ----------------------------------------------------------------------------------

    def loginUrlCheck(self, url: str):
        self.logger.debug(f"\nurl: {url}\ncurrentUrl: {self.currentUrl()}")
        if url == self.currentUrl():
            self.logger.info(f"{__name__}: ログインに成功")
            self.wait.loadPageWait(chrome=self.chrome, timeout=10)
            return True
        else:
            self.logger.error(f"{__name__}: ログインに失敗")
            return False


# ----------------------------------------------------------------------------------


    def login_element_check(self, by: str, value: str, timeout: int):
        try:
            self.wait.loadPageWait(by=by, value=value, timeout=timeout)
            self.logger.info(f"{__name__}: ログインに成功")
            return True

        except TimeoutException:
            self.logger.error(f"{__name__}: reCAPTCHAの処理時間に {timeout} 秒以上 かかってしまいましたためtimeout")
            return False


# ----------------------------------------------------------------------------------


    def actionBeforeLogin(self, url: str, login_info: dict, delay: int=2, maxRetries: int = 3):
        # 特定のサイトにアクセス
        self.openSite(url=url)

        retries = 0
        while retries < maxRetries:
            try:
                self.clickLoginBtn(by=login_info['bypassIdBy'], value=login_info['bypassIdValue'])
                element = self.wait.canWaitInput(by=login_info['idBy'], value=login_info['idValue'])
                time.sleep(delay)

                if element:
                    # ここから通常のIDログイン
                    self.flowLoginID(url=url, login_info=login_info, delay=delay)
                    break

            except TimeoutException:
                self.logger.warning(f"要素が見つからなかったため、再試行します。リトライ回数: {retries + 1}/{maxRetries}")
                retries += 1
                # self.clickLoginBtn(by=login_info['bypassIdBy'], value=login_info['bypassIdValue'])
                time.sleep(delay)  # リトライの間に少し待機して再試行する

        if retries == maxRetries:
            self.logger.error("指定回数のリトライを行いましたが、要素にアクセスできませんでした")


# ----------------------------------------------------------------------------------


    def bypassOpenSite(self):
        return self.chrome.get(self.homeUrl)


# ----------------------------------------------------------------------------------


    def _getCookie(self):
        cookies = self.chrome.get_cookies()
        cookie = cookies[0]
        self.logger.debug(f"\ncookies(元データ→リスト): {cookies}\ncookie（元データリストの1つ目の辞書）: {cookie}")
        checked_cookie = self.canValueInCookie(cookie=cookie)
        return checked_cookie


# ----------------------------------------------------------------------------------
# Cookieの値が入っているか確認


    def canValueInCookie(self, cookie: Dict):
        if not cookie.get('name') or not cookie.get('value'):
            self.logger.warning(f"cookieに必要な情報が記載されてません {cookie}")
            return None
        else:
            return cookie


# ----------------------------------------------------------------------------------
# CookieデータをDBにいれられるように整理

    # @decoInstance.funcBase
    def _sort_cookie(self, cookie: Dict):
        db_cookie_info = {
            'name': cookie['name'],
            'value': cookie.get('value'),
            'domain': cookie.get('domain'),
            'path': cookie.get('path'),
            'expires': cookie.get('expiry'),
            'maxAge': cookie.get('max-age'),  # expiresよりも優先される、〇〇秒間、持たせる権限
            'createTime': int(time.time())
        }
        self.logger.debug(f'db_cookie_info: {db_cookie_info}')

        return db_cookie_info


# ----------------------------------------------------------------------------------
# **********************************************************************************


class MultiSiteIDLogin(SingleSiteIDLogin):
    def __init__(self, chrome, debugMode=True):
        super().__init__(chrome, debugMode)


# ----------------------------------------------------------------------------------


    def _set_pattern(self, site_name: str):
        login_pattern_dict = LoginInfo.SITE_PATTERNS.value
        login_info = login_pattern_dict[site_name]
        self.logger.info(f"login_info: {login_info}")

        return login_info


# ----------------------------------------------------------------------------------


    def flow_cookie_save_cap(self, login_url, login_info, cap_after_element_by, cap_after_element_path, tableName, columnsName, cap_timeout = 180):
        return super().flow_cookie_save_cap(login_url, login_info, cap_after_element_by, cap_after_element_path, tableName, columnsName, cap_timeout)


# ----------------------------------------------------------------------------------
