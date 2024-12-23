# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# 2024/7/31 更新
# 2024/8/27 テストOK

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import time
from typing import Callable, Optional


# 自作モジュール
from .utils import Logger
from .path import BaseToPath
from .fileWrite import LimitFileWrite
from .ApiRequest import ApiRequest
from .decorators import Decorators

from const_str import FileName


decoInstance = Decorators()


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************


class ChatGPTOrder:
    def __init__(self):
        # def __init__(self, api_key: str):

        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

        # ApiKey
        # self.api_key = api_key

        # インスタンス
        self.apiRequest = ApiRequest()
        self.path = BaseToPath()
        self.fileWrite = LimitFileWrite()

    # ----------------------------------------------------------------------------------
    # SNSバージョン　リクエストした文章とresponseで帰ってきた文章を整理してjsonファイルに書き込む

    async def resultSave(
        self,
        prompt: str,
        fixedPrompt: str,
        endpointUrl: str,
        model: str,
        apiKey: str,
        maxTokens: int,
        maxlen: int,
        snsKinds: str,
        notifyMsg: str = None,
        notifyFunc: Optional[Callable[[str], None]] = None,
    ):

        result = await self.wordCountCheck(
            prompt=prompt,
            fixedPrompt=fixedPrompt,
            endpointUrl=endpointUrl,
            model=model,
            apiKey=apiKey,
            maxTokens=maxTokens,
            maxlen=maxlen,
        )

        userMsg = result["userMsg"]
        assistantMsg = result["assistantMsg"]
        chatHistory = result["chatHistory"]
        dateStamp = time.strftime("%Y%m%d")
        fileName = f"{snsKinds}_{dateStamp}"

        self.fileWrite.writeToJson(data=chatHistory, fileName=fileName)
        userToMsg = self.userToNotifyMsg(
            userMsg=userMsg, assistantMsg=assistantMsg, notifyMsg=notifyMsg
        )

        fileFullPath = self.path.getWriteFilePath(fileName=fileName)
        writeFilePath = f"{fileFullPath}.json"

        if notifyFunc:
            await notifyFunc(userToMsg, writeFilePath)

    # ----------------------------------------------------------------------------------
    # 純粋にチャッピーからの出力を返す

    async def resultOutput(
        self,
        prompt: str,
        fixedPrompt: str,
        endpointUrl: str,
        model: str,
        apiKey: str,
        maxTokens: int,
        maxlen: int,
    ):
        result = await self.wordCountCheck(
            prompt=prompt,
            fixedPrompt=fixedPrompt,
            endpointUrl=endpointUrl,
            model=model,
            apiKey=apiKey,
            maxlen=maxlen,
            maxTokens=maxTokens,
        )
        assistantMsg = result["assistantMsg"]["content"]
        return assistantMsg

    # ----------------------------------------------------------------------------------

    def userToNotifyMsg(self, userMsg, assistantMsg, notifyMsg):
        sendMsg = f"送信した内容 : \n{userMsg}"
        replyMsg = f"生成された文章 : \n{assistantMsg}"

        userToMsg = "\n\n".join([notifyMsg, sendMsg, replyMsg])
        self.logger.debug(f"userToMsg: {userToMsg}")

        return userToMsg

    # ----------------------------------------------------------------------------------
    # 文字数がオーバーした際に再リクエスト

    async def wordCountCheck(
        self,
        prompt: str,
        fixedPrompt: str,
        endpointUrl: str,
        model: str,
        apiKey: str,
        maxTokens: int,
        maxlen: int,
    ):
        result = await self.ChatHistory(
            prompt=prompt,
            endpointUrl=endpointUrl,
            model=model,
            apiKey=apiKey,
            maxTokens=maxTokens,
        )

        assistantMsg = result["assistantMsg"]["content"]
        chatHistory = result["chatHistory"]
        self.logger.debug(chatHistory)
        self.logger.debug(assistantMsg[10:])
        wordCount = len(assistantMsg)
        self.logger.debug(assistantMsg)
        self.logger.info(f"wordCount: {wordCount}\maxlen: {maxlen}")

        if wordCount > maxlen:
            newResult = await self.reRequest(
                fixedPrompt=fixedPrompt,
                beforeResult=result,
                endpointUrl=endpointUrl,
                model=model,
                apiKey=apiKey,
                maxTokens=maxTokens,
            )
            return newResult
        else:
            return result

    # ----------------------------------------------------------------------------------

    @decoInstance.characterLimitRetryAction(
        maxlen=100, maxCount=3, timeout=30, delay=2, notifyFunc=None
    )
    async def reRequest(
        self,
        fixedPrompt: str,
        beforeResult: dict,
        endpointUrl: str,
        model: str,
        apiKey: str,
        maxTokens: int,
    ):

        assistantMsg = beforeResult["assistantMsg"]
        chatHistory = beforeResult["chatHistory"]

        userFixedMsg = await self.userMsg(prompt=fixedPrompt)
        chatHistory.extend([userFixedMsg])

        assistantMsg = await self.assistantResponseMessage(
            endpointUrl=endpointUrl,
            model=model,
            apiKey=apiKey,
            messages=chatHistory,
            maxTokens=maxTokens,
        )
        chatHistory.extend([assistantMsg])

        self.logger.debug(f"ChatGPTとのやり取り: \n{chatHistory}")

        return {
            "userMsg": userFixedMsg,
            "assistantMsg": assistantMsg,
            "chatHistory": chatHistory,
        }

    # ----------------------------------------------------------------------------------

    async def ChatHistory(
        self, prompt: str, endpointUrl: str, model: str, apiKey: str, maxTokens: int
    ):
        chatHistory = []

        userMsg = await self.userMsg(prompt=prompt)
        chatHistory.extend([userMsg])

        assistantMsg = await self.assistantResponseMessage(
            endpointUrl=endpointUrl,
            model=model,
            apiKey=apiKey,
            messages=chatHistory,
            maxTokens=maxTokens,
        )
        chatHistory.extend([assistantMsg])

        self.logger.info(f"ChatGPTとのやり取り: {chatHistory}")

        return {
            "userMsg": userMsg,
            "assistantMsg": assistantMsg,
            "chatHistory": chatHistory,
        }

    # ----------------------------------------------------------------------------------
    # "user"が送信側、"assistant"がChatGPT

    async def userMsg(self, prompt: str):
        userMsg = {"role": "user", "content": prompt}
        return userMsg

    # ----------------------------------------------------------------------------------
    # "user"が送信側、"assistant"がChatGPT

    async def assistantResponseMessage(
        self, endpointUrl: str, model: str, apiKey: str, messages: str, maxTokens: int
    ):
        response = await self.chatGptRequest(
            endpointUrl=endpointUrl,
            model=model,
            apiKey=apiKey,
            messages=messages,
            maxTokens=maxTokens,
        )
        message = response["choices"][0]["message"]
        return message

    # ----------------------------------------------------------------------------------

    async def chatGptRequest(
        self, endpointUrl: str, model: str, apiKey: str, messages: str, maxTokens: int
    ):
        return await self.apiRequest.apiRequest(
            method="POST",
            endpointUrl=endpointUrl,
            headers=self.getHeaders(apiKey=apiKey),
            json=self.getJson(model=model, messages=messages, maxTokens=maxTokens),
        )

    # ----------------------------------------------------------------------------------
    # API認証情報

    def getHeaders(self, apiKey: str):
        return {"Authorization": f"Bearer {apiKey}", "Content-Type": "application/json"}

    # ----------------------------------------------------------------------------------
    # APIの設定情報

    def getJson(self, model: str, messages: str, maxTokens: int):
        return {"model": model, "messages": messages, "max_tokens": maxTokens}


# ----------------------------------------------------------------------------------
