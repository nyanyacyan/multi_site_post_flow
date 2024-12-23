# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# 2024/8/27 更新
# テストOK
# Pathの設定 export PYTHONPATH="${PYTHONPATH}:/Users/nyanyacyan/Desktop/project_file/SNS_auto_upper/installer/src/method/base"


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import

import pytest
import unittest
from unittest.mock import patch, MagicMock, PropertyMock
from gspread.exceptions import APIError


# 自作モジュール
from installer.src.method.base.spreadsheetRead import GetDataGSSAPI


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************
# 単体テスト 写真を取得


class TestGetDataGSSAPI:

    # ----------------------------------------------------------------------------------

    def testGetDataFrameFromGss(self):
        # データのセット
        mockData = [
            {"列A": "データ1", "列B": "データ2"},
            {"列A": "データ3", "列B": "データ4"},
        ]

        KeyName = "dummyKey.json"
        spreadsheetId = "dummySpreadsheetId"
        sheetName = "dummyName"

        with patch.object(
            GetDataGSSAPI, "client", new_callable=PropertyMock
        ) as mockClientProp:
            # モック化→空の箱にいれる
            mockClient = MagicMock()

            # 見つけた'client'属性の値をモックにいれる
            mockClientProp.return_value = mockClient

            # インスタンスの作成
            instance = GetDataGSSAPI()

            # メソッドの呼び出し
            instance.getDataFrameFromGss(
                KeyName=KeyName, spreadsheetId=spreadsheetId, sheetName=sheetName
            )

            # モックが呼び出されたか確認
            # ? assert_called_once は、unittest モジュールに含まれる unittest.mock の機能の一部
            # ? assert_called_once は、モック化されたメソッドが一度だけ呼び出されたことを確認するためのアサーション
            # ? アサーションは、テストで用いられる概念で、「ある条件が成り立っているかどうか」を確認するための文
            mockClient.open_by_key.assert_called_once_with(spreadsheetId)


# ----------------------------------------------------------------------------------
# pytest -s /Users/nyanyacyan/Desktop/Project_file/SNS_Upper/tests/test_spreadsheetRead.py::TestSpreadSheetRead::testGssReadApiError


class TestSpreadSheetRead(unittest.TestCase):

    # 失敗したときのテスト

    @patch("time.sleep", return_value=None)
    def testGssReadApiError(self, mock_sleep):
        # テストデータの設定
        test_data = {
            "KeyName": "dummyKey.json",
            "spreadsheetId": "dummySheetId",
            "sheetName": "dummySheetName",
        }

        # エラーレスポンスの設定
        error_response = {"error": {"message": "API error", "code": 400}}
        mock_error_response = MagicMock()
        mock_error_response.json.return_value = error_response

        # credsのモック
        mock_creds = MagicMock()

        # gspread.authorizeのモック
        with patch("gspread.authorize") as mock_authorize:
            # authorizeがAPIErrorを発生させるように設定
            mock_authorize.side_effect = APIError(mock_error_response)

            # GetDataGSSAPIのcredsメソッドをモック化
            with patch.object(GetDataGSSAPI, "creds", return_value=mock_creds):
                instance = GetDataGSSAPI()

                # テスト実行と検証
                with pytest.raises(SystemExit) as SystemExit:
                    instance.getDataFrameFromGss(**test_data)

                assert SystemExit.value.code == 1
                assert mock_authorize.call_count == 3  # リトライ回数に応じて調整
                mock_sleep.assert_called()


# ----------------------------------------------------------------------------------
