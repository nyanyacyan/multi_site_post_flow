# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import time
from typing import Dict, List
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.common.exceptions import TimeoutException

# 自作モジュール
from .utils import Logger
from .elementManager import ElementManager
from .driverWait import Wait
from .decorators import Decorators
from .driverDeco import jsCompleteWaitDeco, InputDeco, ClickDeco
from .SQLite import SQLite


from constSqliteTable import TableSchemas
from const_element import LoginInfo
from const_str import StatusName

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
        self.sqlite = SQLite(debugMode=debugMode)


# ----------------------------------------------------------------------------------
# Cookieログイン
# reCAPTCHA OK → 調整必要 → 待機時間を180秒

    def flow_cookie_save(self, login_url: str, loginInfo: dict, tableName: str, columnsName: tuple, timeout: int =180, captcha: bool = False):
        # ログインの実施
        self.flowLoginID(login_url=login_url, loginInfo=loginInfo, timeout=timeout, captcha=captcha)

        # Cookieの取得
        cookie = self._getCookie()

        # テーブルにCookie情報を入れ込む
        self.insertCookieData(cookie=cookie, tableName=tableName, columnsName=columnsName)

        table_data_cols = self.sqlite.columnsExists(tableName=tableName)

        if 'name' in table_data_cols:
            self.logger.info(f"DBの入力完了: {table_data_cols}")
            return True
        else:
            self.logger.error(f"DBの保存に失敗: {table_data_cols}")
            return False


# ----------------------------------------------------------------------------------
# IDログイン
# reCAPTCHA OK

    def flowLoginID(self, login_url: str, loginInfo: dict, timeout: int, captcha: bool = False, max_count: int = 3):
        self.logger.debug(f'loginInfo: {loginInfo}')

        # サイトを開いてCookieを追加
        self.openSite(login_url=login_url)

        self.inputId(by=loginInfo['ID_BY'], value=loginInfo['ID_VALUE'], inputText=loginInfo['ID_TEXT'])

        self.inputPass(by=loginInfo['PASS_BY'], value=loginInfo['PASS_VALUE'], inputText=loginInfo['PASS_TEXT'])

        # if captcha == True:
        #     # display:noneを解除
        #     self.element.unlockDisplayNone()

        #     recapcha = self.element.getElement(by=loginInfo['RECAPTCHA_CHECKBOX_BY'], value=loginInfo['RECAPTCHA_CHECKBOX_VALUE'])
        #     status = recapcha.get_attribute(StatusName.RECAPTCHA_CHECKBOX.value)
        #     self.logger.debug(f'status: {status}')

        #     retry_count = 0
        #     while retry_count < max_count:
        #         if status == True:
        #             self.logger.debug(f'reCAPTCHA処理は成功してます: {status}')
        #             break
        #         else:
        #             self.logger.error(f'まだreCAPTCHA処理が終わってません: {status}')
        #             retry_count += 1
        #             time.sleep(60)
        #             continue

        #     if retry_count == max_count and status != True:
        #         self.logger.error(f'reCAPTCHA処理がタイムアウトしました。最大リトライ回数に達しました。: {status}')
        #         raise TimeoutError('reCAPTCHA処理がタイムアウトしました。最大リトライ回数に達しました。')


        self.clickLoginBtn(by=loginInfo['BTN_BY'], value=loginInfo['BTN_VALUE'])

        # 検索ページなどが出てくる対策
        # PCのスペックに合わせて設定
        self.wait.jsPageChecker(chrome=self.chrome, timeout=10)

        # reCAPTCHA対策を完了確認
        return self.login_element_check(by=loginInfo['LOGIN_AFTER_ELEMENT_BY'], value=loginInfo['LOGIN_AFTER_ELEMENT_VALUE'], timeout=timeout)


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


    def actionBeforeLogin(self, url: str, loginInfo: dict, delay: int=2, maxRetries: int = 3):
        # 特定のサイトにアクセス
        self.openSite(url=url)

        retries = 0
        while retries < maxRetries:
            try:
                self.clickLoginBtn(by=loginInfo['bypassIdBy'], value=loginInfo['bypassIdValue'])
                element = self.wait.canWaitInput(by=loginInfo['idBy'], value=loginInfo['idValue'])
                time.sleep(delay)

                if element:
                    # ここから通常のIDログイン
                    self.flowLoginID(url=url, loginInfo=loginInfo, delay=delay)
                    break

            except TimeoutException:
                self.logger.warning(f"要素が見つからなかったため、再試行します。リトライ回数: {retries + 1}/{maxRetries}")
                retries += 1
                # self.clickLoginBtn(by=loginInfo['bypassIdBy'], value=loginInfo['bypassIdValue'])
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

    @decoInstance.funcBase
    def canValueInCookie(self, cookie: Dict):
        if not cookie.get('name') or not cookie.get('value'):
            self.logger.warning(f"cookieに必要な情報が記載されてません {cookie}")
            return None
        else:
            return cookie


# ----------------------------------------------------------------------------------
# 有効期限をクリアしたmethod
# DBよりcookie情報を取得する

    @decoInstance.funcBase
    def insertCookieData(self, cookie: Dict, tableName: str, columnsNames: tuple = TableSchemas.BASE_COOKIES_TABLE_COLUMNS.value):
        cookieName = cookie['name']
        cookieValue = cookie.get('value')
        cookieDomain = cookie.get('domain')
        cookiePath = cookie.get('path')
        cookieExpires = cookie.get('expiry')
        cookieMaxAge = cookie.get('max-age')  # expiresよりも優先される、〇〇秒間、持たせる権限
        cookieCreateTime = int(time.time())

        # 値をtuple化
        values = (cookieName, cookieValue, cookieDomain, cookiePath, cookieExpires, cookieMaxAge, cookieCreateTime)
        self.logger.info(f"values:\n{values}")

        # テーブルの存在確認
        # TODO DBの名称をtitleにする
        # TODO 複数のDBを作成するのではなく、1つにしてバックアップするように変更→ない場合には作成する
        # TODO DBがあるかどうかを確認する→テーブルがあるか確認をする

        # データを入れ込む
        self.sqlite.insertData(tableName=tableName, cols=columnsNames, values=values)
        return cookie


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


    def flow_cookie_save_cap(self, login_url, loginInfo, cap_after_element_by, cap_after_element_path, tableName, columnsName, cap_timeout = 180):
        return super().flow_cookie_save_cap(login_url, loginInfo, cap_after_element_by, cap_after_element_path, tableName, columnsName, cap_timeout)


# ----------------------------------------------------------------------------------
