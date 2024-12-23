# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# 2023/3/29更新

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import

import requests
import gspread
from google.oauth2.service_account import Credentials
from typing import Dict, List
import pandas as pd
import io

from dotenv import load_dotenv

# 自作モジュール
from .utils import Logger
from .path import BaseToPath
from .decorators import Decorators

from const_str import FileName


load_dotenv()

decoInstance = Decorators()


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************


class SpreadsheetRead:
    def __init__(self, sheet_url, account_id):
        self.sheet_url = sheet_url
        self.account_id = account_id

        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

        self.path = BaseToPath()
        self.df = self.load_spreadsheet()

    ####################################################################################
    # ----------------------------------------------------------------------------------
    # スプシ読み込みからpandasでの解析→文字列データを仮想的なファイルを作成

    def load_spreadsheet(self, key_col):
        # スプシデータにアクセス
        spreadsheet = requests.get(self.sheet_url)

        # バイナリデータをutf-8に変換する
        # on_bad_lines='skip'→パラメータに'skip'を指定することで、不正な形式スキップして表示できる（絵文字、特殊文字）
        # StringIOは、文字列データをファイルのように扱えるようにするもの。メモリ上に仮想的なテキストファイルを作成する
        # .set_index('account')これによってIndexを'account'に設定できる。
        string_data = spreadsheet.content.decode("utf-8")
        data_io = io.StringIO(string_data)

        df = pd.read_csv(data_io, on_bad_lines="skip")

        # Indexを「account_id」にしたデータフレームを返してる
        return df.set_index(key_col)

    # ----------------------------------------------------------------------------------
    # Columnまでの公式を入れ込んだ関数

    def _sort_column_name(self, column_name):
        sort_value = self.df.loc[self.account_id, column_name]
        return sort_value

    # ----------------------------------------------------------------------------------
    # スプシからurlを取得

    def get_url_in_gss(self):
        column_name = "url"
        url = self._sort_column_name(column_name=column_name)
        self.logger.debug(f"url: {url}")
        return url

    # ----------------------------------------------------------------------------------
    # 取得したURLに付属してnameを取得

    def get_name_in_gss(self):
        column_name = "name"
        name = self._sort_column_name(column_name=column_name)
        self.logger.debug(f"name: {name}")
        return name


# ----------------------------------------------------------------------------------
# **********************************************************************************


class GSSReadNoID:
    def __init__(self, gss_url):
        self.gss_url = gss_url

        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

    ####################################################################################

    def spreadsheet_to_df(self):
        # スプシデータにアクセス
        spreadsheet = requests.get(self.gss_url)

        self.logger.debug(f"spreadsheet:\n{spreadsheet}")

        self.logger.debug(f"self.gss_url: {self.gss_url}")

        string_data = spreadsheet.content.decode("utf-8")
        data_io = io.StringIO(string_data)

        df = pd.read_csv(data_io, on_bad_lines="skip")

        # Indexを「account_id」にしたデータフレームを返してる
        return df


# ----------------------------------------------------------------------------------

# **********************************************************************************
# APIを使ってGSSの読み込み
# 複数のシートからの読み込みが必要な場合はこっち


class GetDataGSSAPI:
    def __init__(self):

        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

        # インスタンス
        self.path = BaseToPath()
        self.decorators = Decorators()

    # ----------------------------------------------------------------------------------
    # APIを使ってGSSからデータを取得してDataFrameに変換
    # TODO ここの3点セットをINFOにして辞書で渡す

    @decoInstance.retryAction(maxRetry=3, delay=30)
    def getDataFrameFromGss(self, gss_info: Dict):
        client = self.client(jsonKeyName=gss_info["jsonKeyName"])

        self.logger.debug(
            f"利用可能なワークシート: {client.open_by_key(gss_info['spreadsheetId']).worksheets()}"
        )

        # 対象のスプシを開く
        worksheet = client.open_by_key(gss_info["spreadsheetId"]).worksheet(
            gss_info["workSheetName"]
        )

        # デバッグ用
        all_values = worksheet.get_all_values()
        self.logger.debug(f"ワークシート全データ: {all_values}")

        # シートのデータを取得→ここでのデータは辞書型
        # columnの行に空白があると読込ができない→入力されてる部分以外を選択して消去
        dictData = worksheet.get_all_records()

        # DataFrameに変換
        df = pd.DataFrame(dictData)
        self.logger.info(f"スプシ読み込み完了 :\n{df.head()}")

        return df

    # ----------------------------------------------------------------------------------
    # スプシの認証プロパティ

    def creds(self, jsonKeyName: str):
        SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
        jsonKeyPath = self.path.getInputDataFilePath(fileName=jsonKeyName)
        creds = Credentials.from_service_account_file(jsonKeyPath, scopes=SCOPES)
        return creds

    # ----------------------------------------------------------------------------------
    # スプシアクセスのプロパティ

    def client(self, jsonKeyName: str):
        creds = self.creds(jsonKeyName=jsonKeyName)
        client = gspread.authorize(creds)
        return client

    # ----------------------------------------------------------------------------------
    # DataFrameから写真のURLを取得 テストOK

    def getPhotoUrl(self, df: pd.DataFrame, colName: str):
        self.logger.info(f"********** getPhoto start **********")

        self.logger.debug(f"df:\n{df.head(3)}")
        self.logger.debug(f"colName: {colName}")

        if not (df is None or df.empty):
            imageUrlList = df[colName].tolist()

            # リストの最初のものを抜き出す（ここを変数化してもよし）
            firstUrl = imageUrlList[0]
            self.logger.debug(f"firstUrl: {firstUrl}")
            self.logger.info(f"********** getPhoto end **********")

            return firstUrl

        else:
            raise ValueError(f"DataFrameがない")


# ----------------------------------------------------------------------------------
# **********************************************************************************
