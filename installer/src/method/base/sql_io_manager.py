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
    def _insert_data(self, db_file_name: str, insert_data: Dict, table_name: str):
        db_file_path = self._db_file_path(db_file_name=db_file_name)

        # DBファイルへの接続開始
        conn = sqlite3.connect(db_file_path)
        conn.row_factory = sqlite3.Row  # 行を辞書形式で取得

        # 命令文を遅れる準備
        cursor = conn.cursor()

        try:
            # トランザクションの開始
            conn.execute(SqlitePrompt.TRANSACTION.value)

            # insert_dataからcolumnとプレースホルダーに分ける
            insert_data_keys, placeholders, insert_data_values= self._get_cols_values_placeholders(insert_data=insert_data)

            # 命令文の構築
            insert_sql_prompt = SqlitePrompt.INSERT.value.format(table_name=table_name, table_column_names=insert_data_keys, placeholders=placeholders)
            self.logger.debug(f'insert_sql_prompt: {insert_sql_prompt}')

            # 処理の実行
            cursor.execute(insert_sql_prompt, insert_data_values)

            # 存在の確認
            select_prompt = SqlitePrompt.SELECT_LAST_ROW.value.format(table_name=table_name)
            cursor.execute(sql=select_prompt)

            # 1行取得する
            table_last_row = cursor.fetchone()
            self.logger.debug(f'\ninput_last_row: {table_last_row}\ninsert_data_values: {insert_data_values}')

            current_table_last_values = table_last_row[1:] # table_last_row[1:]は一番最初はIDのためそれ以降を確認
            if current_table_last_values == insert_data_values:
                self.logger.info(f"テーブル: {table_name} にデータ挿入成功: {insert_data}")
            else:
                self.logger.error(f"整合性チェック失敗: {current_table_last_values} != {insert_data_values}")

            conn.commit()
            self.logger.info('データを入力させることを確定（コミット）を実施')

        except Exception as e:
            conn.rollback()
            self.logger.error(f'DBへのinsertを実施中にエラーが発生（ロールバック実施）: {e}')

        finally:
            conn.close()


# ----------------------------------------------------------------------------------
# placeholderを作成

    def _get_cols_values_placeholders(self, insert_data: Dict):
        insert_data_keys = ', '.join(insert_data.keys())  # 出力: 'name, email' SQLで受け取れる文字列集合にするため
        placeholders = ', '.join(["?"] * len(insert_data))
        insert_data_values = tuple(insert_data.values())  # 値はtuple
        return insert_data_keys, placeholders, insert_data_values


# ----------------------------------------------------------------------------------

    def _db_file_path(self, db_file_name: str):
        return self.sql_base._db_path(db_file_name=db_file_name)
