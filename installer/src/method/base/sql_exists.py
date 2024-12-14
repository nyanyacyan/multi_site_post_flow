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
from .sql_base import SqliteBase
from .decorators import Decorators
from const_str import Extension
from constSqliteTable import TableSchemas
from const_sql_comment import SqlitePromptExists

decoInstance = Decorators(debugMode=True)


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************
# 存在を確認 handler


class SqliteExistsHandler:
    def __init__(self, debugMode=True):

        # logger
        self.getLogger = Logger(__name__, debugMode=debugMode)
        self.logger = self.getLogger.getLogger()

        # インスタンス化
        self.networkError = NetworkHandler(debugMode=debugMode)
        self.path = BaseToPath(debugMode=debugMode)
        self.sql_base = SqliteBase(debugMode=debugMode)

        self.currentDate = datetime.now().strftime("%y%m%d")
        self.tablePattern = TableSchemas.TABLE_PATTERN.value


# ----------------------------------------------------------------------------------

#! --------------------
# DBファイル
#! --------------------

# ----------------------------------------------------------------------------------
# DBを使う前に整っているのかを確認

    def db_start_check(self, db_file_name: str, table_pattern_info: Dict):
        self._db_file_exists(db_file_name=db_file_name, table_pattern_info=table_pattern_info)

        self._table_exists(db_file_name=db_file_name, table_pattern_info=table_pattern_info)

        self._all_table_col_exists(db_file_name=db_file_name, table_pattern_info=table_pattern_info)


# ----------------------------------------------------------------------------------

#! --------------------
# DBファイル
#! --------------------

# ----------------------------------------------------------------------------------
# DBファイル確認

    def _db_file_exists(self, db_file_name: str, table_pattern_info: Dict):
        db_file_path = self.sql_base._db_path(db_file_name=db_file_name)
        if not db_file_path.exists():
            self.logger.warning(
                f"DBファイル({db_file_name})がないため作成: {db_file_path}"
            )
            # TODO ここにテーブル作成処理
            self._all_table_create(db_file_name=db_file_name, table_pattern_info=table_pattern_info)

        else:
            self.logger.info(f"DBファイル({db_file_name})を発見: {db_file_path}")
            return None


# ----------------------------------------------------------------------------------

#! --------------------
# table
#! --------------------

# ----------------------------------------------------------------------------------
# TODO テーブル確認

    def _table_exists(self, db_file_name: str, table_pattern_info: Dict):
        result = self._result_table_check(db_file_name=db_file_name, table_pattern_info=table_pattern_info)

        # テーブルが無い場合
        if result is None:
            self._all_table_create(db_file_name=db_file_name, table_pattern_info=table_pattern_info)

        if result == False:
            raise ValueError('指定のtableと乖離があります（乖離情報は別途上記に記載）')

        return self.logger.info(f'table状態は整ってます: {table_pattern_info}')



# ----------------------------------------------------------------------------------
# tableの名前を取得

    def _get_table_names(self, db_file_name: str):
        sql_prompt = SqlitePromptExists.TABLES_EXISTS.value
        current_table_names = self.sql_base.sql_process(
            db_file_name=db_file_name, sql_prompt=sql_prompt, fetch="all"
        )

        # SQLのレスポンスは[('GAME_CLUB',), ('MA_CLUB',), ('RRMT_CLUB',)]ため変換
        current_table_name_list = [row[0] for row in current_table_names]
        self.logger.info(f"\ncurrent_table_names: {current_table_name_list}")
        return current_table_name_list


# ----------------------------------------------------------------------------------
# すべてのtable_patternにあるテーブルを作成する

    def _all_table_create(self, db_file_name: str, table_pattern_info: Dict):
        # 新しくテーブルを作成する
        self.logger.info(f'すべてのテーブルを作成開始: {table_pattern_info}')
        for tableName, cols_info in table_pattern_info.items():
            self._table_and_col_create(
                tableName=tableName, cols_info=cols_info, db_file_name=db_file_name
            )
        return None


# ----------------------------------------------------------------------------------
# tableを作成

    def _table_and_col_create(self, tableName: str, cols_info: Dict, db_file_name: str):
        # cols_info を SQL(str) の形式に変換
        str_cols_info = ", ".join(
            [f"{col} {dtype}" for col, dtype in cols_info.items()]
        )

        sql_prompt = SqlitePromptExists.TABLES_CREATE.value.format(
            tableName=tableName, cols_info=str_cols_info
        )
        self.sql_base.sql_process(db_file_name=db_file_name, sql_prompt=sql_prompt)
        self.logger.info(f"{tableName} tableを作成完了")
        return None


# ----------------------------------------------------------------------------------
# tableの整合チェック

    def _result_table_check(self, db_file_name: str, table_pattern_info: Dict):
        # すべてのテーブル名を取得
        current_table_name_list = self._get_table_names(db_file_name=db_file_name)

        if not current_table_name_list:
            self.logger.warning(f'table がないため新しく作成: {current_table_name_list}')
            return None

        # table_pattern_infoからtable_nameだけを取り出す
        check_table_name_list = [table_name for table_name in table_pattern_info.keys()]

        # resultとmsgを受け取って返す
        result, msg = self._current_element_check(
            current_list=current_table_name_list, check_list=check_table_name_list
        )

        if result:
            self.logger.info(f"table 整合OK: {msg}")
        else:
            self.logger.error(f"table 相違あり: {msg}")
        return result


# ----------------------------------------------------------------------------------

#! --------------------
# Column
#! --------------------

# ----------------------------------------------------------------------------------
# すべてのテーブルに入っているcolumnをチェック

    def _all_table_col_exists(self, table_pattern_info: Dict, db_file_name: str):
        false_tables_col_info = []
        table_name_list = []
        for table_name, check_col_list in table_pattern_info.items():
            current_col_name_list = self._get_column_name(tableName=table_name, db_file_name=db_file_name)
            result, msg = self._current_element_check(current_list=current_col_name_list, check_list=check_col_list)

            # table_name_listに追加
            table_name_list.append(table_name)

            # columnに相違がある場合、リストに追加
            if not result:
                false_tables_col_info.append(f"{table_name}: {msg}\n")

        if false_tables_col_info:
            self.logger.error(f"以下のテーブルにカラム相違があります:\n{''.join(false_tables_col_info)}")
            raise ValueError("カラム整合性に問題があります。")

        if not false_tables_col_info:
            self.logger.info(f'すべてのtableに入ってるColumnは正常です{table_name_list}')


# ----------------------------------------------------------------------------------
# table_cols_infoを取得 [columnのID, column名, columnのtype, notnullの制約, PrimaryKeyの成約]を持ったcolumns

    def _get_table_cols_info(self, tableName: str, db_file_name: str):
        sql_prompt = SqlitePromptExists.COLUMNS_EXISTS.value.format(tableName)
        table_cols_info = self.sql_base.sql_process(db_file_name=db_file_name, sql_prompt=sql_prompt, fetch="all")
        self.logger.info(f"table_cols_info: {table_cols_info}")
        return table_cols_info


# ----------------------------------------------------------------------------------
# table_cols_infoからcol_name_listを生成

    def _get_column_name(self, tableName: str, db_file_name: str):
        table_cols_info = self._get_table_cols_info(
            tableName=tableName, db_file_name=db_file_name
        )
        col_name_list = [col_info["name"] for col_info in table_cols_info]
        self.logger.info(f"col_name_list: {col_name_list}")
        return col_name_list


# ----------------------------------------------------------------------------------
# columnの整合チェック

    def _current_element_check(self, current_list: List, check_list: List):
        # 不足しているカラム
        missing_element = [col for col in check_list if col not in current_list]

        # 余分なカラム（期待されていないカラム）
        extra_element = [col for col in current_list if col not in check_list]

        if missing_element:
            return False, f"不足している要素があります: {', '.join(missing_element)}"
        elif extra_element:
            return False, f"不必要な要素があります: {', '.join(extra_element)}"
        else:
            return True, f"columnチェックOK"


# ----------------------------------------------------------------------------------

