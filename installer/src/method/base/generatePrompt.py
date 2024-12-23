# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# 2024/8/1 更新
#! 2024/8/26 テスト実施済み

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

# import
import pandas as pd

# 自作モジュール
from .utils import Logger
from .decorators import Decorators
from .fileWrite import FileWrite
from .errorHandlers import GeneratePromptHandler

from const_str import FileName


decoInstance = Decorators()


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************
# GSSからプロンプトを取得してChatGPTへのリクエスト


class GeneratePrompt:
    def __init__(self):

        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

        # インスタンス
        self.fileWrite = FileWrite()
        self.errorHandler = GeneratePromptHandler()

    # ----------------------------------------------------------------------------------
    # DataFrameからPrompt生成する

    @decoInstance.generatePrompt
    async def generatePrompt(
        self,
        df: pd.DataFrame,
        conditionCol: str,
        conditionFormat: str,
        testimonialsCol: str,
        testimonialsFormat: str,
        keywordCol: str,
        keywordFormat: str,
        hashtagCol: str,
        hashtagFormat: str,
        exampleCol: str,
        exampleFormat: str,
        beforeCol: str,
        beforeFormat: str,
        openingComment: str,
        endingComment: str,
        fileName: str = __name__,
    ):

        # 条件
        conditionText = await self.generateText(
            df=df, col=conditionCol, textFormat=conditionFormat
        )
        self.logger.debug(conditionText[:20])

        # 体験談
        testimonialsText = await self.generateText(
            df=df, col=testimonialsCol, textFormat=testimonialsFormat
        )
        self.logger.debug(testimonialsText[:20])

        # キーワード
        keywordText = await self.generateText(
            df=df, col=keywordCol, textFormat=keywordFormat
        )
        self.logger.debug(keywordText[:20])

        # ハッシュタグ
        hashtagText = await self.generateText(
            df=df, col=hashtagCol, textFormat=hashtagFormat
        )
        self.logger.debug(hashtagText[:20])

        # 例題
        exampleText = await self.generateText(
            df=df, col=exampleCol, textFormat=exampleFormat
        )
        self.logger.debug(exampleText[:20])

        # 前回のコメント
        beforeText = await self.generateText(
            df=df, col=beforeCol, textFormat=beforeFormat
        )
        self.logger.debug(beforeText[:20])

        # 結合させてテキストに変換
        prompt = "\n\n".join(
            [
                openingComment,
                conditionText,
                testimonialsText,
                keywordText,
                exampleText,
                beforeText,
                endingComment,
            ]
        )
        self.logger.debug(f"prompt:\n\n{prompt}")

        self.fileWrite.writeToText(data=prompt, fileName=fileName)

        return prompt

    # ----------------------------------------------------------------------------------
    # 各行から必要な項目を抜き取ってつなぎ合わせる

    async def generateText(self, df: pd.DataFrame, col: str, textFormat: str):
        mergeText = await self.generateMergeText(df=df, col=col)

        # Formatに作成したリストを追加する
        text = textFormat.format(list=mergeText)
        self.logger.debug(f"Formatされたテキストを生成:\n{text}")

        return text

    # ----------------------------------------------------------------------------------
    # 指定したColumnのシリーズを抽出してリスト化

    async def dfColToList(self, df: pd.DataFrame, col: str):
        try:
            listData = df[col].tolist()
            self.logger.debug(f"listData:\n{listData}")
            return listData

        except Exception as e:
            self.errorHandler.generatePromptHandler(e=e)
            return None

    # ----------------------------------------------------------------------------------
    # 箇条書きのリストを作成

    async def generateBulletList(self, df: pd.DataFrame, col: str):
        listData = await self.dfColToList(df=df, col=col)
        bulletList = [f"・{data}\n" for data in listData if data.strip()]
        self.logger.debug(f"bulletList:\n{bulletList}")
        return bulletList

    # ----------------------------------------------------------------------------------
    # 箇条書きリストを1つの文字列文章へ

    async def generateMergeText(self, df: pd.DataFrame, col: str):
        bulletList = await self.generateBulletList(df=df, col=col)
        mergeText = "".join(bulletList)
        self.logger.debug(f"mergeText :{mergeText}")
        return mergeText


# ----------------------------------------------------------------------------------
# **********************************************************************************
