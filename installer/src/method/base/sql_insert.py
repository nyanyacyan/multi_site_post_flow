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
from const_str import Extension
from constSqliteTable import TableSchemas
from const_sql_comment import SqlitePromptExists

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


# ----------------------------------------------------------------------------------
# SQLiteへ入れ込む
# TODO DBファイルにテーブルが有るかどうかを確認→基本は1サイトにつき１つのDBファイル
# TODO 流れの確認→PathからDBファイルの確認→テーブルがあるか確認→入れ込み

    @decoInstance.funcBase
    def _insert_data(self, db_file_name: str, all_tables_column_info: Dict, tableName: str, columnNames: tuple, values: tuple):
        # DBファイルの存在を確認して処理する
        db_path = self.DB_file_exists(db_file_name=db_file_name, all_tables_column_info=all_tables_column_info)

        # テーブルにあるColumnの確認
        table_columnNames = self._columns_Exists(db_path=db_path, all_tables_column_info=all_tables_column_info, tableName=tableName, columnNames=columnNames)
        self.logger.debug(f'\ncolumnNames: {columnNames}\ntable_columnNames: {table_columnNames}')

        # valuesのカウントをしてその分「？」を追加して結合
        placeholders = ', '.join(['?' for _ in values])
        self.logger.warning(f"\ncolumnNames: {columnNames}\nvalues: {values}")

        # データをSQLiteに入れ込む
        sql = f"INSERT INTO {tableName} {table_columnNames} VALUES ({placeholders})"
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
# values: tuple = () > パラメータが何もなかったら空にするという意味

    @decoInstance.sqliteErrorHandler
    def sql_process(self, db_path: str, sql: str, values: tuple = (), fetch: str = None):
        conn = self._get_DB_connect(db_path)
        if not conn:
            return None

        try:
            cursor = self._execute_SQL(conn=conn, sql=sql, values=values)

            if fetch == 'one':
                self.logger.debug(f"[one] c.fetchone()が実行されました")
                return cursor.fetchone()

            elif fetch == 'all':
                self.logger.debug(f"[all] c.fetchall()が実行されました")
                return cursor.fetchall()

            # データ抽出以外の処理を実施した場合
            else:
                conn.commit()
                self.logger.info(f"コミットの実施をしました")
                return cursor.lastrowid

        finally:
            self.logger.debug("connを閉じました")
            conn.close()


# ----------------------------------------------------------------------------------
# DBがなかったら作成する→複数のDBファイルを作成しないpattern
# ファイル名は指定できるようにする

    def DB_file_exists(self, db_file_name: str, all_tables_column_info: Dict, extension: str = Extension.DB.value):


        if not dbFilePath.exists():
            self.logger.warning(f'{db_file_name}{extension}ファイルがないので新しく作成します。: {dbFilePath}')
            self._createAllTable(db_path=dbFilePath, all_tables_column_info=all_tables_column_info)

        else:
            self.logger.info(f'指定のDBファイルの確認発見: ファイル名（{db_file_name}{extension}）: {dbFilePath}')
        return dbFilePath


# ----------------------------------------------------------------------------------
# テーブルのすべてのカラムを取得する
# PRAGMA table_infoはそのテーブルのColumn情報を取得する
# →1つ目のリストはcolumnID、２つ目column名、３つ目データ型、４つ目はカラムがNULLを許可するかどうかを示す（1はNOT NULL、0はNULL許可）
# ５→columnに指定されたデフォルト値
# columnData[1]=columns名

    @decoInstance.funcBase
    def _columns_Exists(self, tableName: str, db_path: str, all_tables_column_info: Dict, columnNames: tuple) -> List[str]:
        sql = f"PRAGMA table_info({tableName});"
        columnsStatus = self.sql_process(db_path=db_path, sql=sql, fetch='all')
        self.logger.debug(f"columnsStatus: {columnsStatus}")

        if not columnsStatus:
            self.logger.debug(f'all_tables_column_info: {all_tables_column_info}')
            self._createAllTable(db_path=db_path, all_tables_column_info=all_tables_column_info)

        table_columnNames = tuple(columnData[1] for columnData in columnsStatus)
        self.logger.warning(f"{tableName} テーブルにあるすべてのColumn: {table_columnNames}")
        self.logger.debug(f'columnNames: {columnNames}')
        # テーブルに作成したColumnが正しく反映しているか確認
        if table_columnNames == columnNames:
            self.logger.info(f'tableに作られた絡むと定義してるColumnが一致しています: {table_columnNames}')
        else:
            self.logger.error(f'tableに作成されたColumnが正しくありません。: {table_columnNames}')

        return table_columnNames


# ----------------------------------------------------------------------------------
# 定義するDBのテーブルデータをまとめたものを読み込んでテーブルを作成

    @decoInstance.sqliteErrorHandler
    def _createAllTable(self, db_path: str, all_tables_column_info: Dict):
        # すべてのテーブルを受け取ってテーブルごとにする
        for tableName, table_column_info in all_tables_column_info.items():
            self.logger.debug(f"tableName: {tableName}")
            sql = self._createTableSqlPrompt(tableName=tableName, table_column_info=table_column_info)
            self.sql_process(db_path=db_path, sql=sql)
        self.checkTableExists(db_path=db_path, all_tables_column_info=all_tables_column_info)


# ----------------------------------------------------------------------------------
# テーブルに定義するColumnの情報を取得してテーブルを作成する

    @decoInstance.funcBase
    def _createTableSqlPrompt(self, tableName: str, table_column_info: dict):
        colDef = ',\n'.join([f"{colName} {colSTS}" for colName, colSTS in table_column_info.items()])
        self.logger.debug(f"colDef:\n{colDef}")

        prompt = f"CREATE TABLE IF NOT EXISTS {tableName}(\n{colDef}\n)"
        return prompt


# ----------------------------------------------------------------------------------

# 全てのテーブル名を取得して、作成したテーブルが反映してるのか確認

    @decoInstance.funcBase
    def checkTableExists(self, db_path: str, all_tables_column_info: Dict):
        sql = f"SELECT name FROM sqlite_master WHERE type='table';"
        allTables = self.sql_process(db_path=db_path, sql=sql, fetch='all')
        self.logger.debug(f"allTables: {allTables}")

        tableNames = [table[0] for table in allTables]
        expectedTable = [tableKey for tableKey in self.tablePattern.keys()]
        self.logger.warning(f"tableNames: {tableNames}")
        self.logger.debug(f"出力されるべきテーブルは: {expectedTable}")

        # テーブルアンマッチリスト
        missingTables = [table for table in expectedTable if table not in tableNames]

        if not missingTables:
            self.logger.info(f"全てのテーブルの作成に成功しています。")
        else:
            self.logger.error(f"期待してるテーブルが揃ってません: 存在しないtable[{missingTables}]")

            # もしテーブルが作成されてなかった場合に足りてないテーブルを作成
            self._createAllTable(db_path=db_path, all_tables_column_info=all_tables_column_info)
            self.logger.info(f"{missingTables} table を作成しました。")
        return allTables


# ----------------------------------------------------------------------------------

# -----------------------
# SQL実行
# -----------------------

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
# 実行の基底Method→sql_promptを渡す＋fetchを選択する

    @decoInstance.sqliteErrorHandler
    def sql_process(self, db_path: str, sql_prompt: str, values: tuple = (), fetch: str = None):
        conn = self._get_DB_connect(db_path)
        if not conn:
            return None

        try:
            cursor = self._execute_SQL(conn=conn, sql_prompt=sql_prompt, values=values)

            if fetch == 'one':
                self.logger.debug(f"[one] c.fetchone()が実行されました")
                return cursor.fetchone()

            elif fetch == 'all':
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

# dbファイルと接続を開始

    @decoInstance.sqliteErrorHandler
    def _get_DB_connect(self, db_path: str) -> sqlite3.Connection:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # 行を辞書形式で取得できるようにする
        return conn


# ----------------------------------------------------------------------------------
# 実行するSQL文にて定義して実行まで行う

    @decoInstance.sqliteErrorHandler
    def _execute_SQL(self, conn: sqlite3.Connection, sql_prompt: str, values: tuple = ()) -> sqlite3.Cursor:
        cursor = conn.cursor()  # DBとの接続オブジェクトを受け取って通信ができるようにする
        cursor.execute(sql_prompt, values)  # 実行するSQL文にて定義して実行まで行う
        return cursor


# ----------------------------------------------------------------------------------


# -----------------------
# SQL実行
# -----------------------


# ----------------------------------------------------------------------------------

# check
# DBファイル確認

    def _db_file_exists(self, db_file_name: str):
        db_file_path = self._db_path(db_file_name=db_file_name)
        if not db_file_path.exists(db_file_path):
            self.logger.warning(f'DBファイル({db_file_name})がないため作成: {db_file_path}')
            # TODO ここにテーブル作成処理

        else:
            self.logger.info(f'DBファイル({db_file_name})を発見: {db_file_path}')
            return db_file_path


# ----------------------------------------------------------------------------------
# TODO テーブル確認





# ----------------------------------------------------------------------------------


    def _get_table_names(self, db_path: str):
        sql_prompt = SqlitePromptExists.TABLES_EXISTS.value
        current_table_names = self.sql_process(db_path=db_path, sql_prompt=sql_prompt, fetch='all')

        # SQLのレスポンスは[('GAME_CLUB',), ('MA_CLUB',), ('RRMT_CLUB',)]ため変換
        current_table_name_list = [row[0] for row in current_table_names]
        self.logger.info(f'\ncurrent_table_names: {current_table_name_list}')
        return current_table_name_list


# ----------------------------------------------------------------------------------
# すべてのtable_patternにあるテーブルを作成する

    def _all_table_create(self, db_path: str, table_pattern_info: Dict):
        for tableName, cols_info in table_pattern_info.items():
            self._table_and_col_create(tableName=tableName, cols_info=cols_info, db_path=db_path)
        return None

# ----------------------------------------------------------------------------------
# tableを作成

    def _table_and_col_create(self, tableName: str, cols_info: Dict, db_path: str):
        # cols_info を SQL(str) の形式に変換
        str_cols_info = ", ".join([f"{col} {dtype}" for col, dtype in cols_info.items()])

        sql_prompt = SqlitePromptExists.TABLES_CREATE.value.format(tableName=tableName, cols_info=str_cols_info)
        self.sql_process(db_path=db_path, sql_prompt=sql_prompt, fetch='all')
        self.logger.info(f'{tableName} tableを作成完了')
        return None


# ----------------------------------------------------------------------------------
# columnの整合チェック

    def _result_table_check(self, db_path: str, check_table_name_list: List):
        # すべてのテーブル名を取得
        current_table_name_list = self._get_table_names(db_path=db_path)

        # resultとmsgを受け取って返す
        result, msg = self._current_element_check(current_list=current_table_name_list, check_list=check_table_name_list)

        if result:
            self.logger.info(f'table :整合OK: {msg}')
        else:
            self.logger.error(f'table 相違あり: {msg}')
        return result


# ----------------------------------------------------------------------------------
# columnの確認をして真偽値を返す

    def _result_col_check(self, tableName: str, db_path: str, check_col_list: List):
        # table_cols_infoからcol_name_listを生成
        col_name_list = self._get_column_name(tableName=tableName, db_path=db_path)

        # resultとmsgを受け取って返す
        result, msg = self._current_element_check(cols_in_table=col_name_list, check_col_list=check_col_list)

        if result:
            self.logger.info(f'column、整合OK: {msg}')
        else:
            self.logger.error(f'table内にあるcolumnに相違あり: {msg}')
        return result

# ----------------------------------------------------------------------------------
# table_cols_infoを取得 [columnのID, column名, columnのtype, notnullの制約, PrimaryKeyの成約]を持ったcolumns

    def _get_table_cols_info(self, tableName: str, db_path: str):
        sql_prompt = SqlitePromptExists.COLUMNS_EXISTS.value.format(tableName)
        table_cols_info = self.sql_process(db_path=db_path, sql_prompt=sql_prompt, fetch='all')
        self.logger.info(f'table_cols_info: {table_cols_info}')
        return table_cols_info


# ----------------------------------------------------------------------------------
# table_cols_infoからcol_name_listを生成

    def _get_column_name(self, tableName: str, db_path: str):
        table_cols_info = self._get_table_cols_info(tableName=tableName, db_path=db_path)
        col_name_list = [col_info['name'] for col_info in table_cols_info]
        self.logger.info(f'col_name_list: {col_name_list}')
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


# -----------------------
# SQL実行
# -----------------------



# 操作
# TODO データを入れ込むMethod
# ----------------------------------------------------------------------------------

# TODO データを取り出すMethod
# ----------------------------------------------------------------------------------

# TODO DBファイルの作成
# ----------------------------------------------------------------------------------

# TODO テーブルの作成
# ----------------------------------------------------------------------------------

# TODO Columnの入れ込み
