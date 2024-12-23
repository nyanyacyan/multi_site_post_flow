# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# 2024/8/26 更新 テストOK

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import

import pandas as pd
import pytest
from unittest.mock import patch


# 自作モジュール
# from ..installer.src.method.base.utils import Logger
from installer.src.method.base.generatePrompt import GeneratePrompt
from installer.src.method.const import XPromptFormat, GssColumns

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************
# pytestを実行する


class TestGenerateText:

    # ----------------------------------------------------------------------------------

    def testGenerateText(self):
        # データのセット
        # 簡単なデータをここで定義してしまう。
        data = {"col1": ["りんご", "banana", "cherry"]}
        df = pd.DataFrame(data)
        col = "col1"
        textFormat = "これはテストです\n{list}"

        # インスタンス化
        testInstance = GeneratePrompt()

        # テストしたいmethodを定義
        result = testInstance.generateText(df, col, textFormat)

        # 期待される結果を記載
        expectedResult = "これはテストです\n・りんご\n・banana\n・cherry\n"

        # 出す結果と実際の結果を検証
        assert result == expectedResult

    # ----------------------------------------------------------------------------------
    # generatePromptのテスト

    def testGeneratePrompt(self):
        # データのセット
        data = {
            "条件": ["条件１", "条件２"],
            "体験談": ["体験談１", "体験談２"],
            "キーワード": ["キーワード１", ""],
            "ハッシュタグ": ["#１個目", "#２個目"],
            "例文": ["例１", ""],
            "前回の文章": ["前回の文章１", ""],
            # '画像':['https:example.com', '']
        }

        # セットしたデータをDataFrame化
        df = pd.DataFrame(data)

        # 引数を定義
        args = {
            "df": df,
            "conditionCol": GssColumns.conditionCol.value,
            "conditionFormat": XPromptFormat.conditionFormat.value,
            "testimonialsCol": GssColumns.testimonialsCol.value,
            "testimonialsFormat": XPromptFormat.testimonialsFormat.value,
            "keywordCol": GssColumns.keywordCol.value,
            "keywordFormat": XPromptFormat.keywordFormat.value,
            "hashtagCol": GssColumns.hashtagCol.value,
            "hashtagFormat": XPromptFormat.hashtagFormat.value,
            "exampleCol": GssColumns.exampleCol.value,
            "exampleFormat": XPromptFormat.exampleFormat.value,
            "beforeCol": GssColumns.beforeCol.value,
            "beforeFormat": XPromptFormat.beforeFormat.value,
            "openingComment": XPromptFormat.openingComment.value,
            "endingComment": XPromptFormat.endingComment.value,
        }

        # インスタンス化
        testInstance = GeneratePrompt()

        # ? テストしたいmethodを定義
        result = testInstance.generatePrompt(**args)

        print(f"result:\n{result}")


# ----------------------------------------------------------------------------------


if __name__ == "__main__":
    test = TestGenerateText()
    test.testGeneratePrompt()


# **********************************************************************************
