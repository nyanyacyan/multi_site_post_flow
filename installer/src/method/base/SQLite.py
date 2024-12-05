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
from ..const_str import Extension
from ..constSqliteTable import TableSchemas

decoInstance = Decorators(debugMode=True)


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************
# 一連の流れ

class SQLite:
    def __init__(self, debugMode=True):

        # logger
        self.getLogger = Logger(__name__, debugMode=debugMode)
        self.logger = self.getLogger.getLogger()


        # インスタンス化
        self.networkError = NetworkHandler(debugMode=debugMode)
        self.path = BaseToPath(debugMode=debugMode)
        self.currentDate = datetime.now().strftime('%y%m%d')
        self.tablePattern = TableSchemas.TABLE_PATTERN


# ----------------------------------------------------------------------------------
# ①DBデータの存在確認

    def boolFilePath(self, extension: str = Extension.DB.value):
        dbDirPath = self.path.getResultDBDirPath()
        self.logger.debug(f"dbDirPath: {type(dbDirPath)}")
        if not dbDirPath.exists():
            self.logger.error(f"ディレクトリが存在しません{dbDirPath}")
        self.logger.debug(f"dbDirPath: {dbDirPath}")
        dbFilePath = dbDirPath / f"{self.currentDate}{extension}"
        self.logger.warning(f"dbFilePath: {dbFilePath}")
        if dbFilePath.exists():
            self.logger.info(f"DBファイルが見つかりました: {dbFilePath}")
            self.cleanWriteFiles(filePath=dbFilePath, extension=extension, keepWrites=5)
            return True
        else:
            self.logger.error(f"DBファイルはまだ作成されてません: {dbFilePath}")
            return False


# ----------------------------------------------------------------------------------


    def cleanWriteFiles(self, filePath, extension: str, startIntNum: int = 6, keepWrites: int=3):
        dirPath = os.path.dirname(filePath)
        files = os.listdir(dirPath)

        self.logger.warning(f"現在の {extension} ファイル数: {len(files)}個\n上限数: {keepWrites}")

        # 6桁の数字をすべてリスト化する
        upperLimit = int('1' + '0' * startIntNum)
        validPrefixes = tuple(str(i).zfill(startIntNum) for i in range(upperLimit))
        self.logger.warning(f"数字 {startIntNum} で始まるファイル数: {len(validPrefixes)}個\n上限数: {keepWrites}")

        # 拡張子によってファイルを厳選
        writeFiles = [
            file for file in os.listdir(dirPath)
            if file.startswith(validPrefixes) and file.endswith(extension)
        ]
        self.logger.info(f"writeFiles :{writeFiles}")

        if len(writeFiles) > keepWrites:
            sortWriteFiles = writeFiles.sort()
            self.logger.debug(f"sortWriteFiles: {sortWriteFiles}")

            oldFile = writeFiles[0]
            fileToRemove = os.path.join(dirPath, oldFile)
            if os.path.exists(fileToRemove):
                os.remove(fileToRemove)
                self.logger.info(f"{keepWrites}つ以上のファイルを検知: {oldFile} を削除")


# ----------------------------------------------------------------------------------
# ①

    def DBFullPath(self, extension: str = Extension.DB.value):
        dbDirPath = self.path.getResultDBDirPath()
        dbFilePath = dbDirPath / f"{self.currentDate}{extension}"
        return dbFilePath


# ----------------------------------------------------------------------------------
# ②
# ディレクトリがない可能性の箇所に貼る関数→同時にテーブルを作成

    def isFileExists(self):
        fullPath = self.DBFullPath()

        if not fullPath.exists():
            fullPath.touch()
            self.logger.info(f"{fullPath.name} がないため作成")
        else:
            self.logger.debug(f"{fullPath.name} 発見")
        return fullPath


# ----------------------------------------------------------------------------------
# ③
# SQLiteにcookiesの情報を書き込めるようにするための初期設定

    @decoInstance.sqliteErrorHandler
    def createAllTable(self):
        for tableName, cols in self.tablePattern.items():
            self.logger.debug(f"tableName: {tableName}")
            sql = self._createTableSqlPrompt(tableName=tableName, cols=cols)
            self.SQLPromptBase(sql=sql)
        self.checkTableExists()


# ----------------------------------------------------------------------------------
# ④

    @decoInstance.funcBase
    def _createTableSqlPrompt(self, tableName: str, cols: dict):
        colDef = ',\n'.join([f"{colName} {colSTS}" for colName, colSTS in cols.items()])
        self.logger.debug(f"colDef: {colDef}")

        prompt = f"CREATE TABLE IF NOT EXISTS {tableName}(\n{colDef}\n)"
        return prompt


# ----------------------------------------------------------------------------------
# values: tuple = () > パラメータが何もなかったら空にするという意味

    @decoInstance.sqliteErrorHandler
    def SQLPromptBase(self, sql: str, values: tuple = (), fetch: str = None):
        conn = self._getDBconnect()
        if not conn:
            return None

        try:
            cursor = self._executeSQL(conn=conn, sql=sql, values=values)

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
# 実行するSQL文にて定義して実行まで行う

    @decoInstance.sqliteErrorHandler
    def _executeSQL(self, conn: sqlite3.Connection, sql: str, values: tuple = ()) -> sqlite3.Cursor:
        cursor = conn.cursor()  # DBとの接続オブジェクトを受け取って通信ができるようにする
        cursor.execute(sql, values)  # 実行するSQL文にて定義して実行まで行う
        return cursor


# ----------------------------------------------------------------------------------


    @decoInstance.sqliteErrorHandler
    def _getDBconnect(self) -> sqlite3.Connection:
        dbFullPath = self.DBFullPath()
        conn = sqlite3.connect(dbFullPath)
        conn.row_factory = sqlite3.Row  # 行を辞書形式で取得できるようにする
        return conn


# ----------------------------------------------------------------------------------


    @decoInstance.funcBase
    def resetTable(self, tableName: str):
        self.logger.warning("既存のテーブルを破棄して、再度構築")
        sqlDrop = f"DROP TABLE IF EXISTS {tableName}"
        self.SQLPromptBase(sql=sqlDrop, fetch=None)
        return self.createTable()


# ----------------------------------------------------------------------------------
# テーブルのすべてのカラムを取得する
# PRAGMA table_infoはそのテーブルのColumn情報を取得する
# →1つ目のリストはcolumnID、２つ目column名、３つ目データ型、４つ目はカラムがNULLを許可するかどうかを示す（1はNOT NULL、0はNULL許可）
# ５→columnに指定されたデフォルト値
# columnData[1]=columns名

    @decoInstance.funcBase
    def columnsExists(self, tableName: str) -> List[str]:
        sql = f"PRAGMA table_info({tableName});"
        columnsStatus = self.SQLPromptBase(sql=sql, fetch='all')
        self.logger.debug(f"columnsStatus: {columnsStatus}")

        columnNames = [columnData[1] for columnData in columnsStatus]
        self.logger.info(f"columnNames: {columnNames}")
        return columnNames


# ----------------------------------------------------------------------------------
# 全てのテーブル名を取得して、作成したテーブルが反映してるのか確認

    @decoInstance.funcBase
    def checkTableExists(self):
        sql = f"SELECT name FROM sqlite_master WHERE type='table';"
        allTables = self.SQLPromptBase(sql=sql, fetch='all')
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
            self.createAllTable()
            self.logger.info(f"{missingTables} table を作成しました。")
        return allTables


# ----------------------------------------------------------------------------------
# SQLiteへ入れ込む

    @decoInstance.funcBase
    def insertData(self, tableName: str, cols: tuple, values: tuple):
        # valuesのカウントをしてその分「？」を追加して結合
        placeholders = ', '.join(['?' for _ in values])
        self.logger.debug(f"values: {values}")

        sql = f"INSERT INTO {tableName} {cols} VALUES ({placeholders})"

        # 最終はIDを返すようにしてる
        insertId = self.SQLPromptBase(sql=sql, values=values, fetch=None)

        self.logger.debug(f"{tableName} の行データ: {insertId}")
        self.logger.info(f"【success】{tableName} テーブルにデータを追加に成功")

        # SQLiteにデータが入ったか確認
        sqlCheck = f"SELECT * FROM {tableName}"
        allData = self.SQLPromptBase(sql=sqlCheck, fetch='all')
        self.logger.debug(f"{tableName} の全データ: {allData}")
        return insertId


# ----------------------------------------------------------------------------------
# 既存であるデータを更新する

    def updateData(self, tableName: str, updateColumnsData: dict, rowId: int):
        strChangeDict = {col: self._strChange(value=value) for col, value in updateColumnsData.items()}
        setClause = ', '.join([f"{col} = ?" for col in strChangeDict.keys()])
        self.logger.debug(f"setClause: \n{setClause}")

        # IDを元にアップデート→SET部分がそのColumnを指している
        sql = f"UPDATE {tableName} SET {setClause} WHERE id = ?"

        # 入れ込むデータと最後にIDを渡す
        values = tuple(strChangeDict.values())
        self.logger.debug(f"values: \n{values}")

        # 最後に ID を追加
        valuesWithId = values + (rowId,)
        self.logger.debug(f"最終的な値: {valuesWithId}")

        self.SQLPromptBase(sql=sql, values=valuesWithId, fetch=None)
        self.logger.info(f"【success】{tableName} ID:{rowId} のデータ更新に成功 \n追加したデータ{updateColumnsData}")


# ----------------------------------------------------------------------------------
# 文字列に変換

    def _strChange(self, value):
        if isinstance(value, list) or isinstance(value, dict):
            self.logger.info(f"SQLで扱えないデータ（リストか辞書）を文字列に変換する\n{value}")
            return ', '.join(value)
        elif value is None:
            return None
        return value


# ----------------------------------------------------------------------------------
# 基本の辞書をSQLiteへ入れ込む
# placeholders→(?, ?, ?)

    @decoInstance.funcBase
    def insertDictData(self, tableName: str, inputDict: Dict):
        # inputDictとSQLiteにあるColumnを突合して存在してるものだけを抽出
        cols, values = self._columnsExtract(tableName=tableName, inputDict=inputDict)

        # SQLiteに入れ込むために文字列に変換
        cols = ', '.join(cols)
        self.logger.info(f"col: {cols}\nvalues: {values}")

        # プレースホルダーを作成
        placeholders = ', '.join(['?' for _ in values]) # valuesの数の文？を追加して結合
        self.logger.debug(f"cols: {cols}")
        self.logger.debug(f"values: {placeholders}")  # valueの数だけ「？」ができる

        # INSERT INTO tableName (col1, col2, col3) VALUES (?, ?, ?)→この形にする
        sql = f"INSERT INTO {tableName} ({cols}) VALUES ({placeholders})"

        # 値をtupleに変更→オブジェクトになっているためtupleに変更が必要
        # values = tuple(inputDict.values())

        self.logger.debug(f"sql文: {sql}\nvalues: {values}")

        rowData = self.SQLPromptBase(sql=sql, values=values, fetch=None)
        self.logger.debug(f"{tableName} の行データ: {rowData}")
        self.logger.info(f"【success】{tableName} テーブルにデータを追加に成功")

        # SQLiteにデータが入ったか確認
        sqlCheck = f"SELECT * FROM {tableName}"
        allData = self.SQLPromptBase(sql=sqlCheck, fetch='all')
        self.logger.debug(f"{tableName} の全データ: {allData}")
        return rowData


# ----------------------------------------------------------------------------------
# 対象テーブルのColumnをすべて取得して現在のColumnと突合させる

    @decoInstance.funcBase
    def _columnsExtract(self, tableName: str, inputDict: Dict):
        # keyを抜き出す
        inputCols = list(inputDict.keys())

        sql = f"PRAGMA table_info({tableName});"
        sqlAllColsInfo = self.SQLPromptBase(sql=sql, fetch='all')
        sqlAllCols = [colInfo[1] for colInfo in sqlAllColsInfo]
        self.logger.debug(f"sqlAllCols: {sqlAllCols}")

        # 存在するColumnと値
        existCols = [col for col in inputCols if col in sqlAllCols]
        existVols = [inputDict[col] for col in existCols]

        # inputDictにある除外されたColumn
        exclusionCols = [col for col in inputCols if not col in sqlAllCols]

        self.logger.info(f"\nSQLiteに存在するColumn: {existCols}\nSQLiteに存在するColumnの値: {existVols}")

        if exclusionCols:
            self.logger.error(f"除外されたColumnがあります: {exclusionCols}")

        return existCols, existVols


# ----------------------------------------------------------------------------------
# テーブルデータを全て引っ張る

    @decoInstance.funcBase
    def getRecordsAllData(self, tableName: str):
        sql = f"SELECT * FROM {tableName}"
        result = self.SQLPromptBase(sql=sql, fetch='all')
        self.logger.info(f"【success】{tableName} すべてのデータを抽出")
        allData = [dict(row) for row in result]
        return allData


# ----------------------------------------------------------------------------------
# 指定したColumnの値を指定して行を抽出 > Column=name Value=5 > 指定の行を抜き出す > List

    @decoInstance.funcBase
    def getAllRecordsByCol(self, tableName: str, col: str, value: Any):
        sql = f"SELECT * FROM {tableName} WHERE {col} = ?"
        result = self.SQLPromptBase(sql=sql, values=(value, ), fetch='all')
        self.logger.info(f"【success】{tableName} 指定のカラムデータをすべて抽出")
        return result


# ----------------------------------------------------------------------------------
# 指定したColumnの値を指定して行を抽出 > Column=name Value=5 > 指定の行を抜き出す > row

    @decoInstance.funcBase
    def getRowRecordsByCol(self, tableName: str, col: str, value: Any):
        sql = f"SELECT * FROM {tableName} WHERE {col} = ?"
        result = self.SQLPromptBase(sql=sql, values=(value, ), fetch='one')
        if result:
            self.logger.info(f"【success】{tableName} 指定の行のデータを抽出")
            self.logger.info(f"result: {result}")
            return result
        else:
            self.logger.error(f"resultがNoneです。命令文に問題がある可能性があります")


# ----------------------------------------------------------------------------------
# 指定したColumnの値を指定して行を削除 > Column=name Value=5 > 指定の行を抜き出す

    @decoInstance.funcBase
    def deleteRecordsByCol(self, tableName: str, col: str, value: Any):
        deleteRow = self.getRowRecordsByCol(col=col, value=value)
        self.logger.debug(f"削除対象のデータです\n{deleteRow}")
        sql = f"DELETE FROM {tableName} WHERE {col} = ?"
        result = self.SQLPromptBase(sql=sql, values=(value, ), fetch=None)
        self.logger.info(f"【success】{tableName} 指定のデータを削除")
        self.logger.info(f"result: {result}")
        return result


# ----------------------------------------------------------------------------------
# 指定したColumnの値を指定して行を削除 > Column=name Value=5 > 指定の行を抜き出す

    @decoInstance.funcBase
    def deleteAllRecords(self, tableName: str):
        deleteData = self.getRecordsAllData()
        self.logger.warning(f"削除対象のデータです\n{deleteData}")
        sql = f"DELETE FROM {tableName}"
        result = self.SQLPromptBase(sql=sql, fetch=None)
        self.logger.info(f"【success】{tableName} すべてのデータを削除")
        self.logger.info(f"result: {result}")
        return result


# ----------------------------------------------------------------------------------

    @decoInstance.sqliteErrorHandler
    def getColMaxValueRow(self, tableName: str, primaryKey: str):
        sql = f"SELECT * FROM {tableName} ORDER BY {primaryKey} DESC LIMIT 1"
        result = self.SQLPromptBase(sql=sql, fetch='all')
        self.logger.info(f"【success】{tableName} 最新情報を取得: primaryKey: {primaryKey}")
        self.logger.info(f"result: {result}")
        return result


# ----------------------------------------------------------------------------------


    @decoInstance.sqliteErrorHandler
    def getSqlOldData(self, tableName: str, primaryKey: str):
        sql = f"""
        DELETE FROM {tableName}
        WHERE {primaryKey} IN (
            SELECT {primaryKey}
            FROM {tableName}
            ORDER BY {primaryKey} ASC
            LIMIT (SELECT COUNT(*) FROM {tableName}) - 5
        );
        """
        result = self.SQLPromptBase(sql=sql, fetch='None')
        self.logger.info(f"【success】{tableName} ５日以上経ったデータを消去しました: primaryKey: {primaryKey}")
        self.logger.info(f"result: {result}")
        return result


# ----------------------------------------------------------------------------------
#? ソートした一番上のデータを取得
# sortするcolumn→createTimeを最新に並び替える
# DESCは降順→createTimeを上に持ってくる
# nameは物件名→部屋名＋部屋番号

    def getSortColOneData(self, tableName: str, primaryKeyCol: str, primaryKeyColValue: str, cols: List, sortCol: str):
        allCol= ', '.join(cols)
        # SQL文 →SELECT col1, col2, col3 FROM tableName WHERE primaryKeyColのようになる
        sql = f"SELECT {allCol} FROM {tableName} WHERE {primaryKeyCol} = ? ORDER BY {sortCol} DESC LIMIT 1"
        result = self.SQLPromptBase(sql=sql, values=(primaryKeyColValue,), fetch='one')
        self.logger.info(f"【success】{tableName}: primaryKey: {primaryKeyCol}: データ取得完了" )
        self.logger.info(f"result: {result}")
        return result


# ----------------------------------------------------------------------------------
#? ソートしたすべてのデータを取得
# sortするcolumn→createTimeを最新に並び替える
# DESCは降順→createTimeを上に持ってくる
# nameは物件名→部屋名＋部屋番号

    def getSortColAllData(self, tableName: str, primaryKeyCol: str, primaryKeyColValue: str, cols: List, sortCol: str):
        allCol= ', '.join(cols)
        # SQL文 →SELECT col1, col2, col3 FROM tableName WHERE primaryKeyColのようになる
        sql = f"SELECT {allCol} FROM {tableName} WHERE {primaryKeyCol} = ? ORDER BY {sortCol} DESC"
        result = self.SQLPromptBase(sql=sql, values=(primaryKeyColValue,), fetch='all')
        self.logger.info(f"【success】{tableName}: primaryKey: {primaryKeyCol}: データ取得完了" )
        self.logger.info(f"result: {result}")
        return result


# ----------------------------------------------------------------------------------