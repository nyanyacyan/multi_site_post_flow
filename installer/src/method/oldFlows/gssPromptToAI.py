# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# 2024/8/1 更新
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import

import time
from datetime import datetime
from typing import Callable, Optional


# 自作モジュール
from ..base.AiOrder import ChatGPTOrder
from ..base.pklChange import PickleControl
from ..base.utils import Logger
from ..base.spreadsheetRead import GSSAPILogin
from ..base.context import GetContext


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************
# ##################################################################################
# オーバーライド

class OverrideChatGPTOrder(ChatGPTOrder):
    def __init__(self, debugMode=True):

        # logger
        self.getLogger = Logger(__name__, debugMode=debugMode)
        self.logger = self.getLogger.getLogger()

    # オーバーライド
    async def chatGPT_generate_prompt(self, api_key: str, engine: str, prompt: str, max_tokens: int, maxRetry: int = 3, delay: int = 5, notifyFunc: Callable[[str], None] | None = None):
        return await super().chatGPT_generate_prompt(api_key, engine, prompt, max_tokens, maxRetry, delay, notifyFunc)


# ##################################################################################
# オーバーライド

class OverrideGSSAPILogin(GSSAPILogin):
    def __init__(self, debugMode=True):

        # logger
        self.getLogger = Logger(__name__, debugMode=debugMode)
        self.logger = self.getLogger.getLogger()

    def get_df_in_gss(self, sheet_name: str, jsonKeyName: str, spreadsheetId: str):
        return super().get_df_in_gss(sheet_name, jsonKeyName, spreadsheetId)


# ##################################################################################
# **********************************************************************************
# GSSからプロンプトを取得してChatGPTへのリクエスト

class GetPromptGSS:
    def __init__(self, debugMode=True):

        # logger
        self.getLogger = Logger(__name__, debugMode=debugMode)
        self.logger = self.getLogger.getLogger()

        # インスタンス
        self.GPT = OverrideChatGPTOrder(debugMode=debugMode)
        self.GssApi = GSSAPILogin(debugMode=debugMode)
        self.pickle = PickleControl(debugMode=debugMode)
        self.context = GetContext(debugMode=debugMode)

# ----------------------------------------------------------------------------------
# GSSからプロンプトをDataFrameで取得する

    async def process(
            self,
            jsonKeyName: str,
            spreadsheetId: str,
            api_key: str,
            engine: str,
            prompt: str,
            max_tokens: int,
            maxRetry: int = 3,
            delay: int = 5,
            notifyFunc: Optional[Callable[[str], None]] = None
    ):
        self.logger.info(f"********** process start **********")

        sheet_name = await self.context._getWeekday()

        # GSSからプロンプトを取得
        prompt = self.GssApi.get_df_in_gss(jsonKeyName, spreadsheetId, sheet_name=sheet_name)

        time.sleep(3)



        time.sleep(3)

        # ChatGPTへのリクエスト
        message = await self.GPT.chatGPT_generate_prompt(api_key, engine,  max_tokens, maxRetry, delay, notifyFunc, prompt=prompt)

        self.logger.info(f"********** process end **********")

        return message

# ----------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------

# **********************************************************************************
