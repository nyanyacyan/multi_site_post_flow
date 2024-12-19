# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import time, requests, cloudscraper
from datetime import datetime
from typing import Dict, List
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.common.exceptions import TimeoutException

# 自作モジュール
from .utils import Logger
from .loginWithId import SingleSiteIDLogin
from .elementManager import ElementManager
from .driverWait import Wait
from .sql_io_manager import SqliteInsert, SqliteUpdate, SqliteRead, SqliteBuckup
from .seleniumBase import SeleniumBasicOperations

from constSqliteTable import TableSchemas
from const_element import LoginInfo
from const_str import StatusName, FileName




# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************


class SingleLoginDBCookie:
    def __init__(self, chrome: WebDriver, db_file_name: str, debugMode=True):
        # logger
        self.getLogger = Logger(__name__, debugMode=debugMode)
        self.logger = self.getLogger.getLogger()

        self.chrome = chrome

        # インスタンス
        self.element = ElementManager(chrome=chrome, debugMode=debugMode)
        self.wait = Wait(chrome=self.chrome, debugMode=debugMode)
        self.selenium = SeleniumBasicOperations(chrome=self.chrome, debugMode=debugMode)


        # 必要情報
        self.db_file_name = db_file_name
        self.table_pattern_info = TableSchemas.TABLE_PATTERN.value
        self.currentDate = datetime.now().strftime("%y%m%d")

        self.id_login = SingleSiteIDLogin(chrome=self.chrome, db_file_name=db_file_name, table_pattern_info=self.table_pattern_info, debugMode=debugMode)


# ----------------------------------------------------------------------------------
# Cookieの情報をDBから取得

    def _get_cookie_in_db(self, table_name: str):
        # DBよりテーブルデータ（filter_keysによって絞り込まれた行）をすべて取得してくる
        with SqliteRead(db_file_name=self.db_file_name, table_pattern_info=self.table_pattern_info) as sqlite_read:
            table_all_data = sqlite_read._read_data(table_name=table_name)

        # テーブルデータから行ごとにデータを抽出
        rows = [row for row in table_all_data]
        self.logger.debug(f'rows: {[dict(row) for row in rows]}')

        cookie = rows[0]
        self.logger.debug(f'cookie: {cookie}')

        try:
            # ここはサイトによって加工が必要（Cookieログインに必要なデータを渡すようにする）
            cookie_info = {
                'name': cookie['name'],
                'value': cookie['value'],
                'domain': cookie['domain'],
                "path": cookie['path'],
                "secure": bool(cookie['secure']),
                "httpOnly": bool(cookie['httpOnly']),
                "sameSite": cookie['sameSite'],
                "expiry": cookie['expires'],  # ここのkeyはそのサイトに合わせる必要がある
            }
        except KeyError as e:
            raise KeyError(f"必要なCookieのキーが見つかりません: {e}")
        self.logger.debug(f'cookie_info: {cookie_info}')
        return cookie_info


# ----------------------------------------------------------------------------------
# Cookieを使ってログイン

    def _cookie_login(self, home_url: str, cookie_info: Dict):

        # 一度サイトを開く
        self.selenium.openSite(url=home_url)
        self.logger.debug(f'cookie_info: {cookie_info}')

        # Cookieをbrowserに追加
        self.chrome.add_cookie(cookie_dict=cookie_info)

        # 一度サイトを開く
        self.selenium.openSite(url=home_url)

        # アクセスしたいサイトにアクセスできたかどうかを確認する（コンプリートまで）
        self.wait.changeUrlWait(target_url=home_url, timeout=10)


# ----------------------------------------------------------------------------------


    @property
    def session(self):
        # sessionを定義（セッションの箱を作ってるイメージ）
        return requests.Session()



# ----------------------------------------------------------------------------------


    def sessionSetting(self, cookie: Dict):
        self.logger.warning(f"cookies: {cookie}")
        if cookie:
            session = self.session

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.204 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Referer": "https://gameclub.jp/"
            }
            session.headers.update(headers)

            session.cookies.set(
                name=cookie['name'],
                value=cookie['value'],
                domain=cookie['domain'],
                path=cookie['path'],
                secure=cookie.get('secure', False),
                expires=cookie.get('expiry')  # 必要であれば追加
            )

            self.logger.debug(f"Cookieの中身:\nname={cookie['name']}\nvalue={cookie['value']}\ndomain={cookie['domain']}, path={cookie['path']}")
            return session
        else:
            self.logger.error(f"cookiesがありません")
            return None


# ----------------------------------------------------------------------------------


    def loginCheck(self, home_url: str):
        if home_url == self.chrome.current_url:
            self.logger.info(f"{__name__}: ログインに成功")
            return True
        else:
            self.logger.error(f"{__name__}: ログインに失敗")
            return False


# ----------------------------------------------------------------------------------
# sessionログイン

    def sessionLogin(self, cookie: dict, home_url: str):

        session = self.sessionSetting(cookie=cookie)

        response = session.get(home_url)
        self.logger.debug(f'response.status_code: {response.status_code}')
        if response.status_code == 200:
            print("ログイン成功")
            print("Response content:", response.text[:500])  # 応答の一部を表示
        else:
            print(f"ログイン失敗: Status code {response.status_code}")
            print(f"home_url: {home_url}\ncookie: {cookie}")
            print("Response Body:", response.text)
        return self.loginCheck(home_url=home_url)


# ----------------------------------------------------------------------------------
# Cookieを使ってログイン

    def _session_login(self, home_url: str):
        # Cookieの必要な情報をDBから取得する
        

        self.sessionLogin(cookie=cookie_info, home_url=home_url)

        self.selenium.openSite(url=home_url)


        # アクセスしたいサイトにアクセスできたかどうかを確認する（コンプリートまで）
        self.wait.changeUrlWait(target_url=home_url, timeout=10)


# ----------------------------------------------------------------------------------
