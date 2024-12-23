# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# export PYTHONPATH="/Users/nyanyacyan/Desktop/project_file/domain_search/installer/src"


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import sqlite3

# 自作モジュール
from utils import Logger
from const_str import FileName


# ----------------------------------------------------------------------------------
# **********************************************************************************


class SqliteChecker:
    def __init__(self):

        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

    # ----------------------------------------------------------------------------------

    def get_database_info(self, db_path: str):
        """
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        →これで取得できるデータ（tables_info）は
        [
            (0, 'id', 'INTEGER', 1, None, 1),
            (1, 'name', 'TEXT', 0, None, 0),
            (2, 'email', 'TEXT', 0, None, 0)
        ]

        """
        # SQLite データベースに接続
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        # テーブル一覧を取得
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        # 各テーブルのColumnを取得
        db_info = {}
        for table in tables:
            table_name = table[0]
            cursor.execute(f"PRAGMA table_info({table_name})")
            table_info_list = cursor.fetchall()
            col_names = [table_info[1] for table_info in table_info_list]
            db_info[table_name] = col_names

        # データベース切断
        connection.close()
        return db_info


# ----------------------------------------------------------------------------------


if __name__ == "__main__":
    print("デバッグを開始")
    sqlite_checker = SqliteChecker()

    #! ここを調べたいPathに変更
    db_path = "/Users/nyanyacyan/Desktop/project_file/multi_site_post_flow/installer/resultOutput/DB/241213.db"
    database_info = sqlite_checker.get_database_info(db_path)

    if not database_info:
        print(f"tableデータがありません。{database_info}")

    print(f"database_info :{database_info}")
    for table_name, columns in database_info.items():
        print(f"table名: {table_name}")
        print(f"{table_name}のすべてのcolumn名: {columns}")
