# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# 2024/8/27 更新
# テストOK
# Pathの設定 export PYTHONPATH="${PYTHONPATH}:/Users/nyanyacyan/Desktop/project_file/SNS_auto_upper/installer/src/method/base"

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import

import sys
import pytest
import gspread
import unittest
from unittest.mock import patch, MagicMock, PropertyMock

# 自作モジュール
from installer.src.method.base.spreadsheetWrite import SpreadsheetWrite


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************
# 単体テスト 写真を取得


class TestSpreadsheetWrite(unittest.TestCase):

    # ----------------------------------------------------------------------------------
    # 成功したときのテスト
    # @patch('method')→この中にいれるmethodがモック化される→モック化されたものは引数に渡す必要がある

    def testGssWriteSuccess(self):
        # ダミーデータセット
        jsonKeyName = "dummyKey.json"
        spreadsheetId = "dummySheetId"
        sheetName = "dummySheetName"
        data = "TestData"
        cell = "B3"

        # importしたクラスの中から’client’属性を抽出してモックに置き換える
        with patch.object(
            SpreadsheetWrite, "client", new_callable=PropertyMock
        ) as mockClientProp:
            # モック化→空の箱にいれる
            mockClient = MagicMock()

            # 見つけた'client'属性の値をモックにいれる
            mockClientProp.return_value = mockClient

            # インスタンスの作成
            instance = SpreadsheetWrite(jsonKeyName=jsonKeyName)

            # メソッドの呼び出し
            instance.writeData(
                spreadsheetId=spreadsheetId, sheetName=sheetName, data=data, cell=cell
            )

            # モックが呼び出されたか確認
            # ? assert_called_once は、unittest モジュールに含まれる unittest.mock の機能の一部
            # ? assert_called_once は、モック化されたメソッドが一度だけ呼び出されたことを確認するためのアサーション
            # ? アサーションは、テストで用いられる概念で、「ある条件が成り立っているかどうか」を確認するための文
            mockClient.open_by_key.assert_called_once_with(spreadsheetId)

    # ----------------------------------------------------------------------------------
    # 失敗したときのテスト

    @patch("time.sleep", return_value=None)  # sleepをモックして、テストを高速化
    def testGssWriteApiError(self, mock_sleep):
        # ダミーデータセット
        jsonKeyName = "dummyKey.json"
        spreadsheetId = "dummySheetId"
        sheetName = "dummySheetName"
        data = "TestData"
        cell = "B3"

        # importしたクラスの中から’client’属性を抽出してモックに置き換える
        with patch.object(
            SpreadsheetWrite, "client", new_callable=PropertyMock
        ) as mockClientProp:
            # モック化→空の箱にいれる
            mockClient = MagicMock()

            # 見つけた'client'属性の値をモックにいれる
            mockClientProp.return_value = mockClient

            # モック化→空の箱にいれる
            mockErrorResponse = MagicMock()  # エラーを返すモック

            # エラー内容のjsonファイルをモック化
            mockErrorResponse.json.return_value = {
                "error": {"message": "API error", "code": 400}
            }

            # モックの中にエラー内容を代入
            mockErrorResponse.json.return_value = mockErrorResponse

            # エラー内容を指定
            error = gspread.exceptions.APIError(mockErrorResponse)

            # 実際に起きるエラー箇所にエラーを充当
            # ? .side_effectメソッドに対して例外を持たせてる
            #! 起きるべきエラー箇所に当てないとテストは成功しない
            mockClient.open_by_key.side_effect = error

            # エラーが起きるテストを指定
            with pytest.raises(SystemExit) as sys_exit:

                # インスタンスの作成
                instance = SpreadsheetWrite(jsonKeyName=jsonKeyName)

                # メソッドの呼び出し
                instance.writeData(
                    spreadsheetId=spreadsheetId,
                    sheetName=sheetName,
                    data=data,
                    cell=cell,
                )

                # 実際に起きるべきエラーを指定
                assert sys_exit.type == SystemExit
                assert sys_exit.value.code == 1

                # モックが呼び出されたかどうかを指定して例外処理が実施されることを確認
                assert mockClient.open_by_key.call_count == 3


# ----------------------------------------------------------------------------------
