# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# 2024/8/27 更新
# テストOK
# Pathの設定 export PYTHONPATH="${PYTHONPATH}:/Users/nyanyacyan/Desktop/project_file/SNS_auto_upper/installer/src/method/base"

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import

import pytest
import aiohttp
from unittest.mock import patch

# 自作モジュール
from installer.src.method.base.ApiRequest import ApiRequest


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************
# 単体テスト 写真を取得


class TestApiRequest:

    # ----------------------------------------------------------------------------------
    # 非同期関数のモックを作成

    # def asyncMock(*args, **kwargs):
    #     m = AsyncMock(*args, **kwargs)
    #     return m

    # ----------------------------------------------------------------------------------
    # 成功したときのテスト
    # @patch('method')→この中にいれるmethodがモック化される→モック化されたものは引数に渡す必要がある

    @pytest.mark.asyncio
    async def testApiRequestSuccess(self):
        # ダミーデータセット
        method = "GET"
        endpointUrl = "dummyEndpointUrl"
        headers = {"Authorization": "Bearer dummyToken"}
        params = {"key": "value"}
        json = {"dummyData": "dummyValue"}
        resultJson = {"status": "mocked_success"}

        # インスタンスの作成
        instance = ApiRequest()

        # importしたクラスの中から’client’属性を抽出してモックに置き換える
        with patch.object(
            instance, "apiRequest", return_value=resultJson
        ) as mockRequest:

            # メソッドの呼び出し
            result = await instance.apiRequest(
                method=method,
                endpointUrl=endpointUrl,
                headers=headers,
                params=params,
                json=json,
            )

            # 結果の検証
            assert result == resultJson
            mockRequest.assert_called_once()

    # ----------------------------------------------------------------------------------
    # aiohttp.ClientSessionエラーのときのテスト

    @pytest.mark.asyncio
    async def testApiRequestError(self):
        # ダミーデータセット
        method = "GET"
        endpointUrl = "dummyEndpointUrl"
        headers = {"Authorization": "Bearer dummyToken"}
        params = {"key": "value"}
        json = {"dummyData": "dummyValue"}

        # インスタンスの作成
        instance = ApiRequest()

        # importしたクラスの中から’client’属性を抽出してモックに置き換える
        with patch(
            "aiohttp.ClientSession.request",
            side_effect=aiohttp.ClientError("ClientError"),
        ):
            with pytest.raises(SystemExit) as exc_info:

                # メソッドの呼び出し
                await instance.apiRequest(
                    method=method,
                    endpointUrl=endpointUrl,
                    headers=headers,
                    params=params,
                    json=json,
                )

            # 結果の検証
            assert exc_info.value.code == 1


# ----------------------------------------------------------------------------------
