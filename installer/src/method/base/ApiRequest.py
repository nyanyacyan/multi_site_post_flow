# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# 2024/8/4 更新
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import

import aiohttp
import ssl
import certifi
from typing import Optional, Dict, Any

# 自作モジュール
from .utils import Logger
from .decorators import Decorators
from .errorHandlers import ResponseStatusCode

from const_str import FileName


decoInstance = Decorators()


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************


class ApiRequest:
    def __init__(self):

        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

        # インスタンス
        self.errorHandler = ResponseStatusCode()

    # ----------------------------------------------------------------------------------
    # 非同期のセッションを作成

    async def createSession(self):
        return aiohttp.ClientSession()

    # ----------------------------------------------------------------------------------
    # テスト環境用のセッションを作成

    async def _testCreateSession(self):
        return aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False))

    # ----------------------------------------------------------------------------------

    @decoInstance.requestRetryAction(maxRetry=3, delay=30, notifyFunc=None)
    async def apiRequest(
        self,
        method: str,  # GET, POSTなど
        endpointUrl: str,  # 指定のURL
        headers: Optional[
            Dict[str, str]
        ] = None,  # APIによって入力 セキュリティ、APIkey、resのデータ形式
        params: Optional[Dict[str, str]] = None,  # 各パラメーターを入力
        json: Optional[
            Dict[str, Any]
        ] = None,  # APIに伝えたり、APIの内容を書き換えたりするときに使う（body）
        data: Optional[Dict[str, str]] = None,  # 各パラメーターを入力
    ):

        # SSL証明書を強制的に発行
        # ssl.create_default_context()→安全な通信を設定するためのルール（安全にデータを送る準備）
        # certifi.where()→インターネット上で信頼できる相手かどうかを確認するための証明書のリスト
        ssl_context = ssl.create_default_context(cafile=certifi.where())

        # それぞれ別の部屋で実施してセッションを作った後にリクエストする
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method=method,
                url=endpointUrl,
                headers=headers,
                params=params,
                json=json,
                data=data,
                ssl=ssl_context,
            ) as response:

                statusCode = response.status
                if statusCode == 200:
                    self.logger.debug(f"statusCodeは {statusCode} です")
                    responseJson = await response.json()
                    self.logger.info(f"responseJson:\n{responseJson}")
                    return responseJson
                else:
                    return statusCode


# ----------------------------------------------------------------------------------
# **********************************************************************************
