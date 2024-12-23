# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# 2024/9/23 更新

# sudo tree /Users/nyanyacyan/Desktop/Project_file/SNS_auto_upper -I 'venv|pyvenv.cfg|__pycache__'


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import os
import asyncio
from dotenv import load_dotenv

# 自作モジュール
from base.utils import Logger
from base.context import GetContext
from base.spreadsheetRead import GetDataGSSAPI
from base.AiOrder import ChatGPTOrder
from base.generatePrompt import GeneratePrompt
from base.notify import LineNotify

from const import (
    KeyFile,
    GssSheetId,
    GssColumns,
    XPromptFormat,
    InstagramPromptFormat,
    ChatgptUtils,
    xUtils,
    SnsKinds,
)

load_dotenv()

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************
# 一連の流れ


class XFlow:
    def __init__(self):

        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

        # インスタンス
        self.GssApi = GetDataGSSAPI()
        self.ChatGptOrder = ChatGPTOrder()
        self.generatePrompt = GeneratePrompt()
        self.Weekday = GetContext()
        self.lineNotify = LineNotify()

    # ----------------------------------------------------------------------------------
    # XProcess

    async def xProcess(self):
        WorkSheetName = self.Weekday.getWeekday()

        # スプシからプロンプトを取得（曜日ごとになるように）
        df = self.GssApi.getDataFrameFromGss(
            KeyName=KeyFile.gssKeyFile.value,
            spreadsheetId=GssSheetId.XSheetId.value,
            workSheetName=WorkSheetName,
        )

        # プロンプト別途作成（テストOK）
        generatePrompt = await self.generatePrompt.generatePrompt(
            df=df,
            conditionCol=GssColumns.conditionCol.value,
            conditionFormat=XPromptFormat.conditionFormat.value,
            testimonialsCol=GssColumns.testimonialsCol.value,
            testimonialsFormat=XPromptFormat.testimonialsFormat.value,
            keywordCol=GssColumns.keywordCol.value,
            keywordFormat=XPromptFormat.keywordFormat.value,
            hashtagCol=GssColumns.hashtagCol.value,
            hashtagFormat=XPromptFormat.hashtagFormat.value,
            exampleCol=GssColumns.exampleCol.value,
            exampleFormat=XPromptFormat.exampleFormat.value,
            beforeCol=GssColumns.beforeCol.value,
            beforeFormat=XPromptFormat.beforeFormat.value,
            openingComment=XPromptFormat.openingComment.value,
            endingComment=XPromptFormat.endingComment.value,
        )

        # ChatGPTへリクエストを投げる（４mini）（テストOK）
        await self.ChatGptOrder.resultSave(
            prompt=generatePrompt,
            fixedPrompt=XPromptFormat.fixedPrompt.value,
            endpointUrl=ChatgptUtils.endpointUrl.value,
            model=ChatgptUtils.model.value,
            apiKey=os.getenv("CHATGPT_APIKEY"),
            maxTokens=ChatgptUtils.MaxToken.value,
            maxlen=xUtils.maxlen.value,
            snsKinds=SnsKinds.X.value,
            notifyMsg=XPromptFormat.notifyMsg.value,
            # lambda関数によって引数がある場合にはこうするよ！という書き方
            notifyFunc=lambda userToMsg, fileFullPath: self.lineNotify.lineDataFileNotify(
                lineToken=os.getenv("LINE_TOKEN"),
                message=userToMsg,
                filePath=fileFullPath,
            ),
        )


# ----------------------------------------------------------------------------------
# **********************************************************************************
# 一連の流れ


class InstagramFlow:
    def __init__(self):

        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

        # インスタンス
        self.GssApi = GetDataGSSAPI()
        self.ChatGptOrder = ChatGPTOrder()
        self.generatePrompt = GeneratePrompt()
        self.Weekday = GetContext()
        self.lineNotify = LineNotify()

    # ----------------------------------------------------------------------------------
    # instagramProcess

    async def instagramProcess(self):
        WorkSheetName = self.Weekday.getWeekday()

        # スプシからプロンプトを取得（曜日ごとになるように）
        df = self.GssApi.getDataFrameFromGss(
            KeyName=KeyFile.gssKeyFile.value,
            spreadsheetId=GssSheetId.InstagramSheetId.value,
            workSheetName=WorkSheetName,
        )

        # プロンプト別途作成（テストOK）
        generatePrompt = await self.generatePrompt.generatePrompt(
            df=df,
            conditionCol=GssColumns.conditionCol.value,
            conditionFormat=InstagramPromptFormat.conditionFormat.value,
            testimonialsCol=GssColumns.testimonialsCol.value,
            testimonialsFormat=InstagramPromptFormat.testimonialsFormat.value,
            keywordCol=GssColumns.keywordCol.value,
            keywordFormat=InstagramPromptFormat.keywordFormat.value,
            hashtagCol=GssColumns.hashtagCol.value,
            hashtagFormat=InstagramPromptFormat.hashtagFormat.value,
            exampleCol=GssColumns.exampleCol.value,
            exampleFormat=InstagramPromptFormat.exampleFormat.value,
            beforeCol=GssColumns.beforeCol.value,
            beforeFormat=InstagramPromptFormat.beforeFormat.value,
            openingComment=InstagramPromptFormat.openingComment.value,
            endingComment=InstagramPromptFormat.endingComment.value,
        )

        # ChatGPTへリクエストを投げる（４mini）（テストOK）
        await self.ChatGptOrder.resultSave(
            prompt=generatePrompt,
            fixedPrompt=InstagramPromptFormat.fixedPrompt.value,
            endpointUrl=ChatgptUtils.endpointUrl.value,
            model=ChatgptUtils.model.value,
            apiKey=os.getenv("CHATGPT_APIKEY"),
            maxTokens=ChatgptUtils.MaxToken.value,
            maxlen=xUtils.maxlen.value,
            snsKinds=SnsKinds.Instagram.value,
            notifyMsg=InstagramPromptFormat.notifyMsg.value,
            # lambda関数によって引数がある場合にはこうするよ！という書き方
            notifyFunc=lambda userToMsg, fileFullPath: self.lineNotify.lineDataFileNotify(
                lineToken=os.getenv("LINE_TOKEN"),
                message=userToMsg,
                filePath=fileFullPath,
            ),
        )


# ----------------------------------------------------------------------------------
# **********************************************************************************

# 非同期処理に変換


async def runXProcess():
    xFlowInstance = XFlow()
    await xFlowInstance.xProcess()


async def runInstagramProcess():
    instagramFlowInstance = InstagramFlow()
    await instagramFlowInstance.instagramProcess()


# ----------------------------------------------------------------------------------

if __name__ == "__main__":
    asyncio.run(runXProcess())


# ----------------------------------------------------------------------------------
# **********************************************************************************
