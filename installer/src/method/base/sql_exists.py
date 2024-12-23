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
from .Archive.sql_base import SqliteBase
from .decorators import Decorators
from const_str import Extension, FileName
from constSqliteTable import TableSchemas
from const_sql_comment import SqlitePrompt

decoInstance = Decorators(debugMode=True)


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************
# 存在を確認 handler


class SqliteExistsHandler:
    def __init__(self, db_file_name: str, table_pattern_info: Dict, debugMode=True):

        # logger
        self.getLogger = Logger(
            moduleName=FileName.LOG_FILE_NAME.value, debugMode=debugMode
        )
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
            self.logger.error(
                f"SQL実行中にエラーが発生（ロールバック実施）: {exc_value}"
            )
            self.logger.debug("".join(traceback.format_tb(exc_traceback)))

        else:
            self.conn.commit()
            self.logger.info("コミット（確定）を実施しました")

        self.conn.close()  # 接続を閉じる

    # ----------------------------------------------------------------------------------

    #! --------------------
    # flow
    #! --------------------

    # ----------------------------------------------------------------------------------
    # DBを使う前に整っているのかを確認
    #! with構文を使って実行がひつよう

    def flow_db_start_check(self):
        try:
            # 1. DBファイルの存在確認
            self.logger.info("DB初期化処理を開始します")
            self._db_file_exists()

            # 2. テーブルの存在確認
            self._table_exists()

            # 3. 各テーブルのカラム整合性確認
            self._all_table_col_exists()

            self.logger.info("DB初期化処理が正常に完了しました")

        except Exception as e:
            self.logger.error(f"DB初期化処理中にエラー発生: {e}")
            self.logger.error(traceback.format_exc())
            raise

    # ----------------------------------------------------------------------------------

    #! --------------------
    # DBファイル
    #! --------------------

    # ----------------------------------------------------------------------------------
    # DBファイル確認

    def _db_file_exists(self):
        if not Path(self.db_path).exists():
            self.logger.warning(f"DBファイル({self.db_path})がないため作成")
            self._all_table_create()
        else:
            self.logger.info(f"DBファイル({self.db_path})を発見")

    # ----------------------------------------------------------------------------------

    #! --------------------
    # table
    #! --------------------

    # ----------------------------------------------------------------------------------
    # テーブル確認

    def _table_exists(self):
        result = self._result_table_check()

        # テーブルが無い場合
        if result is None:
            self._multi_table_create()

        elif not result:
            raise ValueError("指定のtableと乖離があります（乖離情報は別途上記に記載）")

        return self.logger.info(f"table状態は整ってます")

    # ----------------------------------------------------------------------------------
    # tableの名前を取得

    def _get_table_names(self):
        sql_prompt = SqlitePrompt.TABLES_EXISTS.value
        cursor = self.conn.cursor()
        cursor.execute(sql_prompt)
        current_table_names = cursor.fetchall()  # すべてのテーブル名

        # SQLのレスポンスは[('GAME_CLUB',), ('MA_CLUB',), ('RRMT_CLUB',)]ため変換
        current_table_name_list = [row[0] for row in current_table_names]
        self.logger.info(f"\ncurrent_table_names: {current_table_name_list}")
        return current_table_name_list

    # ----------------------------------------------------------------------------------
    # 複数ののtable_patternにあるテーブルを作成する

    def _multi_table_create(self):
        # 新しくテーブルを作成する
        self.logger.info(f"すべてのテーブルを作成開始: {self.table_pattern_info}")
        self.logger.debug(f"self.db_file_name: {self.db_file_name}")
        self.logger.debug(f"self.table_pattern_info: {self.table_pattern_info}")

        # 複数pattern
        if isinstance(self.table_pattern_info, list):
            for table_name, cols_info in self.table_pattern_info.items():
                self._table_and_col_create(table_name=table_name, cols_info=cols_info)
        # 単発pattern
        else:
            self._table_and_col_create(
                table_name=self.db_file_name, cols_info=self.table_pattern_info
            )
        return None

    # ----------------------------------------------------------------------------------
    # tableを作成

    def _table_and_col_create(self, table_name: str, cols_info: Dict):
        self.logger.debug(f"table_name: {table_name}")
        self.logger.debug(f"cols_info: {cols_info}")
        # cols_info を SQL(str) の形式に変換
        str_cols_info = ", ".join(
            [f"{col} {dtype}" for col, dtype in cols_info.items()]
        )
        self.logger.debug(f"str_cols_info: {str_cols_info}")

        sql_prompt = SqlitePrompt.TABLES_CREATE.value.format(
            table_name=table_name, cols_info=str_cols_info
        )
        self.logger.debug(f"sql_prompt: {sql_prompt}")

        self.conn.execute(sql_prompt)
        self.logger.info(f"{table_name} tableを作成完了")
        return None

    # ----------------------------------------------------------------------------------
    # tableの整合チェック

    def _result_table_check(self):
        # すべてのテーブル名を取得
        current_table_name_list = self._get_table_names()

        if not current_table_name_list:
            self.logger.warning(
                f"table がないため新しく作成: {current_table_name_list}"
            )
            return None

        # 複数pattern
        if isinstance(self.table_pattern_info, list):
            # table_pattern_infoからtable_nameだけを取り出す
            check_table_name_list = list(self.table_pattern_info.keys())
        # 単発pattern
        else:
            check_table_name_list = [self.db_file_name]

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

    def _all_table_col_exists(self):
        false_tables_col_info = []
        table_name_list = []
        if isinstance(self.table_pattern_info, list):
            for table_name, check_col_list in self.table_pattern_info.items():
                current_col_name_list = self._get_column_name(table_name=table_name)
                result, msg = self._current_element_check(
                    current_list=current_col_name_list, check_list=check_col_list
                )

                # table_name_listに追加
                table_name_list.append(table_name)

                # columnに相違がある場合、リストに追加
                if not result:
                    false_tables_col_info.append(f"{table_name}: {msg}\n")

        else:
            current_col_name_list = self._get_column_name(table_name=self.db_file_name)
            result, msg = self._current_element_check(
                current_list=current_col_name_list, check_list=self.table_pattern_info
            )

        if false_tables_col_info:
            self.logger.error(
                f"以下のテーブルにカラム相違があります:\n{''.join(false_tables_col_info)}"
            )
            raise ValueError("カラム整合性に問題があります。")

        if not false_tables_col_info:
            self.logger.info(
                f"すべてのtableに入ってるColumnは正常です{table_name_list}"
            )

    # ----------------------------------------------------------------------------------
    # table_cols_infoからcol_name_listを生成

    def _get_column_name(self, table_name: str):
        sql_prompt = SqlitePrompt.COLUMNS_EXISTS.value.format(table_name=table_name)
        cursor = self.conn.cursor()
        cursor.execute(sql_prompt)

        # 全tableにあるcol_infoを取得
        table_cols_info = cursor.fetchall()

        # col_infoにある中からcol_nameを取得してリスト化
        check_col_list = [col_info["name"] for col_info in table_cols_info]
        self.logger.debug(f"{table_name} check_col_list: {check_col_list}")
        return check_col_list

    # ----------------------------------------------------------------------------------
    # columnの整合チェック

    def _current_element_check(self, current_list: List, check_list: List):
        self.logger.debug(f"current_list: {current_list}, check_list: {check_list}")
        # 不足しているカラム
        missing = [item for item in check_list if item not in current_list]

        # 余分なカラム（期待されていないカラム）
        extra = [item for item in current_list if item not in check_list]

        if missing:
            return False, f"不足している要素があります: {', '.join(missing)}"
        elif extra:
            return False, f"不必要な要素があります: {', '.join(extra)}"
        else:
            return True, f"整合性OK"


# ----------------------------------------------------------------------------------
