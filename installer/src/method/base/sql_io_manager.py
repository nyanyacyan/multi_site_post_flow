# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# テストOK
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import os, sqlite3, traceback
from typing import Any
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Tuple, Literal, Union



# 自作モジュール
from .utils import Logger
from .path import BaseToPath
from .errorHandlers import NetworkHandler
from .decorators import Decorators
from .Archive.sql_base import SqliteBase
from .sql_exists import SqliteExistsHandler
from const_str import Extension
from constSqliteTable import TableSchemas
from const_sql_comment import SqlitePrompt

decoInstance = Decorators(debugMode=True)


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************
# 一連の流れ

class SqliteInsert:
    def __init__(self, db_file_name: str, table_pattern_info: Dict, debugMode=True):

        # logger
        self.getLogger = Logger(__name__, debugMode=debugMode)
        self.logger = self.getLogger.getLogger()

        # インスタンス化
        self.networkError = NetworkHandler(debugMode=debugMode)
        self.path = BaseToPath(debugMode=debugMode)
        self.sql_base = SqliteBase(debugMode=debugMode)

        # 必要情報
        self.table_pattern_info = table_pattern_info  # スキーマ情報を保持
        self.currentDate = datetime.now().strftime("%y%m%d")
        self.db_file_name = db_file_name
        self.conn = None  # 接続オブジェクトを保持するために空の箱を用意

        # db_path
        self.db_path = self.sql_base._db_path(db_file_name=self.db_file_name)

# ----------------------------------------------------------------------------------
# with構文を使ったときに最初に実行される処理

    def __enter__(self):
        # DBファイルに接続開始
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        return self


# ----------------------------------------------------------------------------------
# with構文を使ったときに最後に実行される処理

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if exc_type:
            self.conn.rollback()
            self.logger.error(f'SQL実行中にエラーが発生（ロールバック実施）: {exc_value}')
            self.logger.debug(''.join(traceback.format_tb(exc_traceback)))

        else:
            self.conn.commit()
            self.logger.info('コミット（確定）を実施しました')

        self.conn.close()  # 接続を閉じる


# ----------------------------------------------------------------------------------
# SQLiteへ入れ込む

    @decoInstance.funcBase
    def _insert_data(self, insert_data_list: list, table_name: str):
        cursor = self.conn.cursor()

        # トランザクションの開始
        self.conn.execute(SqlitePrompt.TRANSACTION.value)

        for insert_data in insert_data_list:

            # insert_dataからcolumnとプレースホルダーに分ける
            insert_data_keys, placeholders, insert_data_values= self._get_cols_values_placeholders(insert_data=insert_data)

            # 命令文の構築
            insert_sql_prompt = SqlitePrompt.INSERT.value.format(table_name=table_name, table_column_names=insert_data_keys, placeholders=placeholders)
            self.logger.debug(f'insert_sql_prompt: {insert_sql_prompt}')

            # 処理の実行
            cursor.execute(insert_sql_prompt, insert_data_values)

        self.conn.commit()
        self.logger.info('データを入力させることを確定（コミット）を実施')
        self.logger.info(f"{len(insert_data_list)} 件のデータを {table_name} に挿入しました")




# ----------------------------------------------------------------------------------
# placeholderを作成

    def _get_cols_values_placeholders(self, insert_data: Dict):
        insert_data_keys = ', '.join(insert_data.keys())  # 出力: 'name, email' SQLで受け取れる文字列集合にするため
        placeholders = ', '.join(["?"] * len(insert_data))
        insert_data_values = tuple(insert_data.values())  # 値はtuple
        return insert_data_keys, placeholders, insert_data_values


# ----------------------------------------------------------------------------------
