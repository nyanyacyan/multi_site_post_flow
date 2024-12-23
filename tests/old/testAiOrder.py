# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# 2024/9/17 更新

# Pathの設定 export PYTHONPATH="${PYTHONPATH}:/Users/nyanyacyan/Desktop/project_file/SNS_auto_upper/installer/src/method/base"

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import

import pytest
import aiohttp
from unittest.mock import patch, AsyncMock

# 自作モジュール
from installer.src.method.base.AiOrder import ChatGPTOrder


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************
# 単体テスト 写真を取得


class TestAiOrder:

    # ----------------------------------------------------------------------------------
    # 成功したときのテスト
    # @patch('method')→この中にいれるmethodがモック化される→モック化されたものは引数に渡す必要がある

    @pytest.mark.asyncio
    async def testAiOrderSuccess(self):
        # ダミーデータセット
        prompt = "dummy"
        fixedPrompt = "直してください"
        model = "gpt-3.5-turbo"
        apiKey = "dummy"
        maxTokens = 100
        maxlen = 100
        snsKinds = "X"
        resultJson = {
            "choices": [{"message": {"role": "assistant", "content": "ああああああ"}}]
        }

        # インスタンスの作成
        instance = ChatGPTOrder()

        # importしたクラスの中から’client’属性を抽出してモックに置き換える
        with patch.object(
            instance, "chatGptRequest", AsyncMock(return_value=resultJson)
        ) as mockRequest:

            # メソッドの呼び出し
            await instance.resultSave(
                prompt=prompt,
                snsKinds=snsKinds,
                fixedPrompt=fixedPrompt,
                model=model,
                apiKey=apiKey,
                maxTokens=maxTokens,
                maxlen=maxlen,
            )

            # 結果の検証
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
        instance = ChatGPTOrder()

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
