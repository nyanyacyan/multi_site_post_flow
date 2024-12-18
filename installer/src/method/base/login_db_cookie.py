# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import time, requests
from datetime import datetime
from typing import Dict, List
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.common.exceptions import TimeoutException

# 自作モジュール
from .utils import Logger
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
                "secure": cookie['secure'],
                "httpOnly": cookie['httpOnly'],
                "sameSite": cookie['sameSite'],
                "expiry": cookie['expires'],  # ここのkeyはそのサイトに合わせる必要がある
            }
        except KeyError as e:
            raise KeyError(f"必要なCookieのキーが見つかりません: {e}")
        self.logger.debug(f'cookie_info: {cookie_info}')
        return cookie_info


# ----------------------------------------------------------------------------------
# Cookieを使ってログイン

    def _cookie_login(self, home_url: str, table_name: str):
        # Cookieの必要な情報をDBから取得する
        cookie_info = self._get_cookie_in_db(table_name=table_name)

        # 一度サイトを開く
        self.selenium.openSite(url=home_url)

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
            session.cookie.set(
                name=cookie['name'],
                value=cookie['value'],
                domain=cookie['domain'],
                path=cookie['path'],
            )
            self.logger.debug(f"Cookieの中身:\nname={cookie['name']}\nvalue={cookie['value']}\ndomain={cookie['domain']}, path={cookie['path']}")
            return session
        else:
            self.logger.error(f"cookiesがありません")
            return None


# ----------------------------------------------------------------------------------


    def loginCheck(self, url: str):
        if url == self.chrome.current_url:
            self.logger.info(f"{__name__}: ログインに成功")
            return True
        else:
            self.logger.error(f"{__name__}: ログインに失敗")
            return False


# ----------------------------------------------------------------------------------
# sessionログイン

    def sessionLogin(self, cookies: dict, url: str):
        session = self.sessionSetting(cookies=cookies)
        session.get(self.homeUrl)
        return self.loginCheck(url=url)


# ----------------------------------------------------------------------------------
