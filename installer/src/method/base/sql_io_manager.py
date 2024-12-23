# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# テストOK
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import sqlite3, traceback
from datetime import datetime
from typing import Dict

# 自作モジュール
from .utils import Logger
from .path import BaseToPath
from .errorHandlers import NetworkHandler
from .decorators import Decorators
from .Archive.sql_base import SqliteBase
from const_sql_comment import SqlitePrompt
from const_str import FileName

decoInstance = Decorators()


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

#! --------------------
# insert
#! --------------------
# **********************************************************************************


class SqliteInsert:
    def __init__(self, db_file_name: str, table_pattern_info: Dict):
        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

        # インスタンス化
        self.networkError = NetworkHandler()
        self.path = BaseToPath()
        self.sql_base = SqliteBase()

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
    # SQLiteへ入れ込む

    @decoInstance.funcBase
    def _insert_data(self, insert_data_list: list, table_name: str):
        cursor = self.conn.cursor()

        # トランザクションの開始
        self.conn.execute(SqlitePrompt.TRANSACTION.value)

        for insert_data in insert_data_list:

            # insert_dataからcolumnとプレースホルダーに分ける
            insert_data_keys, placeholders, insert_data_values = (
                self._get_cols_values_placeholders(insert_data=insert_data)
            )

            # 命令文の構築
            insert_sql_prompt = SqlitePrompt.INSERT.value.format(
                table_name=table_name,
                table_column_names=insert_data_keys,
                placeholders=placeholders,
            )
            self.logger.debug(f"insert_sql_prompt: {insert_sql_prompt}")

            # 処理の実行
            cursor.execute(insert_sql_prompt, insert_data_values)

        self.conn.commit()
        self.logger.info("データを入力させることを確定（コミット）を実施")
        self.logger.info(
            f"{len(insert_data_list)} 件のデータを {table_name} に挿入しました"
        )

    # ----------------------------------------------------------------------------------
    # placeholderを作成

    def _get_cols_values_placeholders(self, insert_data: Dict):
        insert_data_keys = ", ".join(
            insert_data.keys()
        )  # 出力: 'name, email' SQLで受け取れる文字列集合にするため
        placeholders = ", ".join(["?"] * len(insert_data))
        insert_data_values = tuple(insert_data.values())  # 値はtuple
        self.logger.debug(
            f"\ninsert_data_keys: {insert_data_keys}\nplaceholders: {placeholders}\ninsert_data_values: {insert_data_values}"
        )
        return insert_data_keys, placeholders, insert_data_values


# ----------------------------------------------------------------------------------

#! --------------------
# update
#! --------------------
# **********************************************************************************


class SqliteUpdate:
    def __init__(self, db_file_name: str, table_pattern_info: Dict):

        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

        # インスタンス化
        self.networkError = NetworkHandler()
        self.path = BaseToPath()
        self.sql_base = SqliteBase()

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
            self.logger.error("詳細なスタックトレース:")
            self.logger.error(
                "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            )

        else:
            self.conn.commit()
            self.logger.info("コミット（確定）を実施しました")

        self.conn.close()  # 接続を閉じる

    # ----------------------------------------------------------------------------------
    # SQLiteにあるデータをアップデートする
    # update_data_listの構造  [{value: "new_value", expires: 1700000000}, {value: "new_value2", expires: 1700000001}]
    # filter_keysの構造  {name: cookie_1, date: 20240101}

    @decoInstance.funcBase
    def _update_data(self, update_data_list: list, table_name: str, filter_keys: Dict):
        cursor = self.conn.cursor()

        # トランザクションの開始
        self.conn.execute(SqlitePrompt.TRANSACTION.value)

        for update_data in update_data_list:

            # update_dataからcolumnとプレースホルダーに分ける
            (
                update_placeholders,
                filter_keys_placeholders,
                update_data_values,
                filter_keys_values,
            ) = self._get_cols_values_placeholders(
                data=update_data, filter_keys=filter_keys
            )

            # 命令文の構築
            update_sql_prompt = SqlitePrompt.UPDATE.value.format(
                table_name=table_name,
                update_placeholders=update_placeholders,
                filter_keys_placeholders=filter_keys_placeholders,
            )
            self.logger.debug(f"update_sql_prompt: {update_sql_prompt}")

            # 処理の実行
            cursor.execute(update_sql_prompt, update_data_values + filter_keys_values)

        self.conn.commit()
        self.logger.info("データを入力させることを確定（コミット）を実施")
        self.logger.info(
            f"{len(update_data_list)} 件のデータを {table_name} に更新しました"
        )

    # ----------------------------------------------------------------------------------
    # placeholderを作成

    def _get_cols_values_placeholders(
        self, data: Dict, filter_keys: Dict
    ):  # -> tuple[LiteralString, str, tuple]:
        data_placeholders = ", ".join(
            [f"{key} = ?" for key in data.keys()]
        )  # 出力: 'name, email' SQLで受け取れる文字列集合にするため
        filter_keys_placeholders = " AND ".join([f"{key} = ?" for key in filter_keys])
        data_values = tuple(data.values())  # 値はtuple
        filter_keys_values = tuple(filter_keys.values())
        self.logger.debug(
            f"\ndata_placeholders: {data_placeholders}\nfilter_keys_placeholders: {filter_keys_placeholders}\ndata_values: {data_values}\nfilter_keys_values: {filter_keys_values}"
        )
        return (
            data_placeholders,
            filter_keys_placeholders,
            data_values,
            filter_keys_values,
        )


# ----------------------------------------------------------------------------------


#! --------------------
# read
#! --------------------
# **********************************************************************************
# 一連の流れ


class SqliteRead:
    def __init__(self, db_file_name: str, table_pattern_info: Dict):

        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

        # インスタンス化
        self.networkError = NetworkHandler()
        self.path = BaseToPath()
        self.sql_base = SqliteBase()

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
            self.logger.error("詳細なスタックトレース:")
            self.logger.error(
                "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            )

        else:
            self.conn.commit()
            self.logger.info("コミット（確定）を実施しました")

        self.conn.close()  # 接続を閉じる

    # ----------------------------------------------------------------------------------
    # SQLiteからデータを呼び出して取得
    # read_listの構造  [{value: "new_value", expires: 1700000000}, {value: "new_value2", expires: 1700000001}]
    # filter_keysの構造  {name: cookie_1, date: 20240101}

    @decoInstance.funcBase
    def _read_data(self, table_name: str, filter_keys: Dict = None):
        cursor = self.conn.cursor()

        # トランザクションの開始
        self.conn.execute(SqlitePrompt.TRANSACTION.value)

        # read_dataからcolumnとプレースホルダーに分ける
        filter_keys_placeholders, filter_keys_values = (
            self._get_cols_values_placeholders(filter_keys=filter_keys)
        )

        # 命令文の構築
        read_sql_prompt = SqlitePrompt.READ.value.format(table_name=table_name)

        # 絞り込みする項目があれば
        if filter_keys:
            read_sql_prompt += SqlitePrompt.READ_WHERE.value.format(
                filter_keys_placeholders=filter_keys_placeholders
            )
        else:
            filter_keys_values = ()  # Noneだった場合にこれを渡すため
        self.logger.debug(f"read_sql_prompt: {read_sql_prompt}")

        # 処理の実行
        cursor.execute(read_sql_prompt, filter_keys_values)
        rows = cursor.fetchall()

        self.logger.info(f"{len(rows)} 件のデータが {table_name} から取得されました")
        return rows

    # ----------------------------------------------------------------------------------
    # placeholderを作成

    def _get_cols_values_placeholders(
        self, filter_keys: Dict
    ):  # -> tuple[LiteralString, str, tuple]:
        if not filter_keys:
            return "", ()  # 条件なしの場合
        filter_keys_placeholders = " AND ".join(
            [f"{key} LIKE ?" for key in filter_keys]
        )
        filter_keys_values = tuple(filter_keys.values())
        self.logger.debug(
            f"\nfilter_keys_placeholders: {filter_keys_placeholders}\nfilter_keys_values: {filter_keys_values}"
        )
        return filter_keys_placeholders, filter_keys_values


# ----------------------------------------------------------------------------------


#! --------------------
# backup
#! --------------------
# **********************************************************************************


class SqliteBuckup:
    def __init__(self, db_file_name: str):

        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

        # インスタンス化
        self.path = BaseToPath()

        # 必要情報
        self.db_file_name = db_file_name

        # db_path
        self.db_path = self.path._db_path(db_file_name=self.db_file_name)
        self.db_backup_path = self.path._db_backup_path(db_file_name=self.db_file_name)

    # ----------------------------------------------------------------------------------
    # DBファイルのバックアップ

    def _data_buck_up(self):
        try:
            with sqlite3.connect(self.db_path) as source_conn, sqlite3.connect(
                self.db_backup_path
            ) as backup_conn:
                source_conn.backup(backup_conn)
                self.logger.info(
                    f"データベースのバックアップが作成されました: {self.db_backup_path}"
                )
        except Exception as e:
            self.logger.error(f"バックアップ中にエラーが発生: {e}")
            raise


# ----------------------------------------------------------------------------------
