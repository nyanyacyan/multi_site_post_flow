# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# 2024/9/10 更新
# Pathの設定 export PYTHONPATH="${PYTHONPATH}:/Users/nyanyacyan/Desktop/project_file/SNS_auto_upper/installer/src/method/base"

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import

import pytest
import aiohttp
from unittest.mock import patch

# 自作モジュール
from installer.src.method.base.notify import (
    LineNotify,
    ChatworkNotify,
    SlackNotify,
    DiscordNotify,
)


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************
# 単体テスト 写真を取得


class TestLineApiRequest:

    # ----------------------------------------------------------------------------------
    # 成功したときのテスト
    # @patch('method')→この中にいれるmethodがモック化される→モック化されたものは引数に渡す必要がある

    def testLineApiRequestSuccess(self):
        # ダミーデータセット
        lineToken = "testToken"
        message = "dummyEndpointUrl"
        image_path = "testImagePath"
        resultJson = {"status": 200, "message": "ok"}
        mock_file_data = b"test binary data"

        # インスタンスの作成
        instance = LineNotify()

        # importしたクラスの中から’client’属性を抽出してモックに置き換える
        with patch("builtins.open", read_data=mock_file_data) as mock_file:
            with patch("requests.post", return_value=resultJson) as mockRequest:

                # メソッドの呼び出し
                result = instance.line_image_notify(
                    lineToken=lineToken, message=message, image_path=image_path
                )

                # 結果の検証
                assert result == resultJson
                mockRequest.assert_called_once()

            # 'open'が呼ばれたかどうかを確認
            mock_file.assert_called_once_with(image_path, mode="rb")


# ----------------------------------------------------------------------------------
# aiohttp.ClientSessionエラーのときのテスト

# def testApiRequestError(self):
#     # ダミーデータセット
#     method = 'GET'
#     endpointUrl = 'dummyEndpointUrl'
#     headers = {'Authorization': 'Bearer dummyToken'}
#     params = {'key': 'value'}
#     json = {'dummyData':'dummyValue'}

#     # インスタンスの作成
#     instance = ApiRequest()

#     # importしたクラスの中から’client’属性を抽出してモックに置き換える
#     with patch('aiohttp.ClientSession.request', side_effect=aiohttp.ClientError('ClientError')):
#         with pytest.raises(SystemExit) as exc_info:

#             # メソッドの呼び出し
#             instance.apiRequest(method=method, endpointUrl=endpointUrl, headers=headers, params=params, json=json)

#         # 結果の検証
#         assert exc_info.value.code == 1


# ----------------------------------------------------------------------------------
