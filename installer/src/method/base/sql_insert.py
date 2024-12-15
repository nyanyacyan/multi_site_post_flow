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
from .utils import Logger
from .path import BaseToPath
from .errorHandlers import NetworkHandler
from .decorators import Decorators
from .sql_base import SqliteBase
from .sql_exists import SqliteExistsHandler
from const_str import Extension
from constSqliteTable import TableSchemas
from const_sql_comment import SqlitePrompt

decoInstance = Decorators(debugMode=True)


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************
# 一連の流れ

class SqliteInsert:
    def __init__(self, debugMode=True):

        # logger
        self.getLogger = Logger(__name__, debugMode=debugMode)
        self.logger = self.getLogger.getLogger()


        # インスタンス化
        self.networkError = NetworkHandler(debugMode=debugMode)
        self.path = BaseToPath(debugMode=debugMode)
        self.currentDate = datetime.now().strftime('%y%m%d')
        self.tablePattern = TableSchemas.TABLE_PATTERN.value
        self.sql_base = SqliteBase(debugMode=debugMode)
        self.sql_exists = SqliteExistsHandler(debugMode=debugMode)

# ----------------------------------------------------------------------------------
# SQLiteへ入れ込む
# TODO DBファイルにテーブルが有るかどうかを確認→基本は1サイトにつき１つのDBファイル
# TODO 流れの確認→PathからDBファイルの確認→テーブルがあるか確認→入れ込み

    @decoInstance.funcBase
    def _insert_data(self, insert_data: Dict, table_name: str):
        # 基本の立ち上げ
        self.sql_base.sql_process()

        # valuesのカウントをしてその分「？」を追加して結合
        placeholders = self._get_placeholders(values=values)

        # データをSQLiteに入れ込む
        sql_prompt = SqlitePrompt.INSERT.value.format(table_name=table_name, column_names=)
        self.logger.debug(f'sql: {sql}')

        # 最終はIDを返すようにしてる
        insertId = self.sql_process(db_path, sql=sql, values=values, fetch=None)

        self.logger.debug(f"{tableName} の行データ: {insertId}")
        self.logger.info(f"【success】{tableName} テーブルにデータを追加に成功")

        # SQLiteにデータが入ったか確認
        sqlCheck = f"SELECT * FROM {tableName}"
        allData = self.SQLPromptBase(sql=sqlCheck, fetch='all')
        self.logger.debug(f"{tableName} の全データ: {allData}")
        return insertId


# ----------------------------------------------------------------------------------
# placeholderを作成

    def _get_placeholders(self, values: tuple):
        placeholders = ', '.join(['?' for _ in values])
        self.logger.warning(f"\nplaceholders: {placeholders}")


# ----------------------------------------------------------------------------------
