# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import time, asyncio
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
    def __init__(self, chrome: WebDriver, db_file_name: str, table_pattern_info: Dict, debugMode=True):
        # logger
        self.getLogger = Logger(__name__, debugMode=debugMode)
        self.logger = self.getLogger.getLogger()

        self.chrome = chrome

        # インスタンス
        self.element = ElementManager(chrome=chrome, debugMode=debugMode)
        self.wait = Wait(chrome=self.chrome, debugMode=debugMode)
        self.selenium = SeleniumBasicOperations(chrome=self.chrome, debugMode=debugMode)

        # 必要情報
        self.db_file_name = FileName.DB_FILE_NAME.value
        self.table_pattern_info = TableSchemas.TABLE_PATTERN.value
        self.currentDate = datetime.now().strftime("%y%m%d")




# ----------------------------------------------------------------------------------
# Cookieの情報をDBから取得

    def _get_cookie_in_db(self, table_name: str, filter_keys: Dict):
        # DBよりテーブルデータ（filter_keysによって絞り込まれた行）をすべて取得してくる
        with SqliteRead(db_file_name=self.db_file_name, table_pattern_info=self.table_pattern_info) as sqlite_read:
            table_all_data = sqlite_read._read_data(table_name=table_name, filter_keys=filter_keys)

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

    def _cookie_login(self, homeUrl: str, table_name: str, filter_keys: Dict):
        # Cookieの必要な情報をDBから取得する
        cookie_info = self._get_cookie_in_db(table_name=table_name, filter_keys=filter_keys)

        # 一度サイトを開く
        self.selenium.openSite(url=homeUrl)

        # Cookieをbrowserに追加
        self.chrome.add_cookie(cookie_dict=cookie_info)

        # 一度サイトを開く
        self.selenium.openSite(url=homeUrl)

# ----------------------------------------------------------------------------------

