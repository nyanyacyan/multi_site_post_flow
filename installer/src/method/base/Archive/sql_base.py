# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# テストOK
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import os, sqlite3
from typing import Any
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Tuple, Literal, Union


# 自作モジュール
from ..utils import Logger
from ..path import BaseToPath
from ..errorHandlers import NetworkHandler
from ..decorators import Decorators
from const_str import Extension
from constSqliteTable import TableSchemas
from const_sql_comment import SqlitePrompt

decoInstance = Decorators(debugMode=True)


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************
# 一連の流れ


class SqliteBase:
    def __init__(self, debugMode=True):

        # logger
        self.getLogger = Logger(__name__, debugMode=debugMode)
        self.logger = self.getLogger.getLogger()

        # インスタンス化
        self.networkError = NetworkHandler(debugMode=debugMode)
        self.path = BaseToPath(debugMode=debugMode)
        self.currentDate = datetime.now().strftime("%y%m%d")
        self.tablePattern = TableSchemas.TABLE_PATTERN.value


# ----------------------------------------------------------------------------------
# 実行の基底Method→sql_promptを渡す＋fetchを選択する

    @decoInstance.sqliteErrorHandler
    def sql_process(
        self, db_file_name: str, sql_prompt: str, values: tuple = (), fetch: str = None
    ):
        cursor = self._cursor(db_file_name)
        if not conn:
            return None

        try:
            cursor = self._execute_SQL(conn=conn, sql_prompt=sql_prompt, values=values)

            if fetch == "one":
                self.logger.debug(f"[one] c.fetchone()が実行されました")
                return cursor.fetchone()

            elif fetch == "all":
                self.logger.debug(f"[all] c.fetchall()が実行されました")
                return cursor.fetchall()

            # データ抽出以外の処理を実施した場合
            else:
                conn.commit()
                self.logger.info(f"コミットの実施をしました")
                return None

        finally:
            self.logger.debug("connを閉じました")
            conn.close()

# ----------------------------------------------------------------------------------
# DBファイルのPath

    def _db_path(self, db_file_name: str, extension: str = Extension.DB.value):
        db_dir_path = self.path.getResultDBDirPath()
        self.logger.debug(f"db_dir_path: {db_dir_path}")
        dbFilePath = db_dir_path / f"{db_file_name}{extension}"
        self.logger.debug(f"dbFilePath: {dbFilePath}")
        return dbFilePath

# ----------------------------------------------------------------------------------
# DBバックアップのPath

    def _db_buck_up_path(self, db_file_name: str, extension: str = Extension.DB.value):
        db_dir_path = self.path.getResultDBBuckUpDirPath()
        self.logger.debug(f"db_dir_path: {db_dir_path}")
        dbFilePath = db_dir_path / f"{db_file_name}{self.currentDate}{extension}"
        self.logger.debug(f"dbFilePath: {dbFilePath}")
        return dbFilePath

# ----------------------------------------------------------------------------------
# dbファイルと接続を開始

    @decoInstance.sqliteErrorHandler
    def _db_connect(self, db_file_name: str) -> sqlite3.Connection:
        db_path = self._db_path(db_file_name=db_file_name)
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # 行を辞書形式で取得できるようにする
        return conn

# ----------------------------------------------------------------------------------
# 実行するSQL文にて定義して実行まで行う

    @decoInstance.sqliteErrorHandler
    def _execute_SQL(
        self, conn: sqlite3.Connection, sql_prompt: str, values: tuple = ()
    ) -> sqlite3.Cursor:
        cursor = (
            conn.cursor()
        )  # DBとの接続オブジェクトを受け取って通信ができるようにする
        cursor.execute(sql_prompt, values)  # 実行するSQL文にて定義して実行まで行う
        return cursor

# ----------------------------------------------------------------------------------

    @decoInstance.sqliteErrorHandler
    def _cursor(self, conn: sqlite3.Connection, db_file_name: str) -> sqlite3.Cursor:
        cursor = (conn.cursor())  # DBとの接続オブジェクトを受け取って通信ができるようにする
        return cursor

# ----------------------------------------------------------------------------------
# 実行するSQL文にて定義して実行まで行う

    @decoInstance.sqliteErrorHandler
    def _execute_SQL(self, cursor: sqlite3.Cursor, sql_prompt: str, values: tuple = ()) -> sqlite3.Cursor:
        return cursor.execute(sql_prompt, values)  # 実行するSQL文にて定義して実行まで行う

# ----------------------------------------------------------------------------------
# トランザクションの開始]

    def _transaction_start(self, conn: sqlite3.Connection, db_file_name) -> sqlite3.Cursor:
        return conn.execute(SqlitePrompt.TRANSACTION.value)  # 実行するSQL文にて定義して実行まで行う


# ----------------------------------------------------------------------------------
