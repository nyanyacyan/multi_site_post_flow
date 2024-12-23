# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# 2024/8/26 更新 テストOK

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import

import pytest
from unittest.mock import AsyncMock, patch

# 自作モジュール
from installer.src.method.base.AiOrder import ChatGPTOrder


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************
# pytestを実行する


class TestApiRequest:

    # ----------------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_chatGPT_generate_prompt(self):
        # データのセット
        # 簡単なデータをここで定義してしまう。
        api_key = "テストAPIKEY"

        args = {
            "prompt": "これはテストPromptです。",
            "maxLength": 250,  # 文字数
            "model": "gpt-4o-mini-2024-07-18",
            "max_tokens": 16000,
            "againComment": "再度リクエストします",
            # 'maxRetry': 3,
            # 'delay': 30,
            # 'notifyFunc': '',
        }

        # モックの作成
        mockApiRequest = AsyncMock(
            return_value={
                "choices": [{"message": {"content": "これはテストレスポンスです"}}]
            }
        )

        # モック化させる部分のPath+クラス名+method名
        #! methodのインスタンス化されてる部分をモック化させる→オーバーライドしたものではないので注意
        pathToClassToMethod = "installer.src.method.base.AI_order.ApiRequest.apiRequest"

        # API部分をモックに差し替える
        with patch(pathToClassToMethod, mockApiRequest) as mocked_method:
            print(f"モックが適用されたメソッド: {mocked_method}")

            # インスタンス化
            testInstance = ChatGPTOrder(
                api_key=api_key,
            )

            # テストしたいmethodを定義
            result = await testInstance.chatGPT_generate_prompt(**args)

            # 期待される結果を記載
            expectedResult = "これはテストレスポンスです"

            # 出す結果と実際の結果を検証
            assert result == expectedResult

            mockApiRequest.assert_called_once()

            # さらに、モックが呼ばれた際の引数や戻り値を確認する
            print(mockApiRequest.call_args)  # 呼び出し時の引数を確認
            print(mockApiRequest.return_value)  # モックが返す値を確認


# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------
# **********************************************************************************
