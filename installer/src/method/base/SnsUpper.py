# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# 2024/7/31 更新
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import

import requests
import aiohttp
from typing import Callable, Optional, Dict, Any

# 自作モジュール
from .utils import Logger
from const_str import FileName, EndPoint
from .ApiRequest import ApiRequest


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
####################################################################################
# オーバーライド


class OverrideApiRequest(ApiRequest):
    def __init__(self):
        super().__init__(debugMode)

    def apiRequest(
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
        maxRetry=3,
        delay=3,
        notifyFunc: Optional[Callable[[str], None]] = None,
    ):

        return super().apiRequest(
            method, endpointUrl, headers, params, json, maxRetry, delay, notifyFunc
        )


####################################################################################
# **********************************************************************************


class XPoster:
    def __init__(
        self,
        xConsumerKey: str,
        xConsumerSecret: str,
        xAccessToken: str,
        xAccessTokenSecret: str,
    ):

        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

        # apikey
        self.consumer_key = xConsumerKey
        self.consumer_secret = xConsumerSecret
        self.access_token = xAccessToken
        self.access_token_secret = xAccessTokenSecret
        self.auth = (
            self.consumer_key,
            self.consumer_secret,
            self.access_token,
            self.access_token_secret,
        )

        # instance
        self.apiRequest = OverrideApiRequest()

    # ----------------------------------------------------------------------------------
    # Twitterの画像付きでアップ
    # 非同期処理

    async def process(
        self,
        imageUrl: str,
        message: str,
        notifyFunc: Optional[Callable[[str], None]] = None,
    ):
        self.logger.info(f"********** XPosterWithImage start **********")
        imageUploadUrl = EndPoint.X_image.value

        imageData = await self._downloadImage(imageUrl)
        files = {"media": imageData}
        upLoadResponse = requests.post(imageUploadUrl, auth=self.auth, files=files)

        if upLoadResponse.status_code == 200:
            mediaId = upLoadResponse.json()["media_id_string"]

            XResponse = await self.apiRequest.apiRequest(
                method="POST",
                endpointUrl=EndPoint.X.value,
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json",
                },
                json={"text": message, "media": [mediaId]},
                notifyFunc=notifyFunc,
            )

            if XResponse.status_code == 201:
                self.logger.info(f"********** XPosterWithImage end **********")
                success_message = f"X 送信成功: \n{message}"
                self.logger.info(success_message)
                if notifyFunc:
                    notifyFunc(success_message)

            else:
                self.logger.error(
                    f"X 送信失敗: {XResponse.status_code},{XResponse.text}"
                )

        else:
            self.logger.error(
                f"X の写真の送信失敗: {XResponse.status_code},{XResponse.text}"
            )

            self.logger.info(f"********** XPosterWithImage end **********")

    # ----------------------------------------------------------------------------------
    # 画像をURLから取得する

    async def _downloadImage(self, imageUrl: str):
        self.logger.info(f"********** _downloadImage start **********")

        self.logger.debug(f"imageUrl: {imageUrl}")

        try:
            # ネットワークに接続させるための通り道を確保
            async with aiohttp.ClientSession() as session:
                # ネットワークの接続ができた際にurlへアクセスできるように確保
                async with session.get(imageUrl) as response:
                    if response.status == 200:
                        # imageUrlから写真を取得
                        imageData = await response.read()
                        imageType = type(imageData)

                        if imageType == bytes:
                            self.logger.info(
                                f"********** _downloadImage start **********"
                            )
                            return imageData

                        else:
                            self.logger.error(f"写真の取得に失敗 type:{imageType}")
                            return None

        except aiohttp.ClientError as e:
            self.logger.error(f"Network error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            return None


# **********************************************************************************
# Instagramの投稿


class InstagramPoster:
    def __init__(self, instAccessToken: str, instBusinessAccountId: str):
        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

        # apikey
        self.instAccessToken = instAccessToken
        self.instBusinessAccountId = instBusinessAccountId

        # インスタンス
        self.apiRequest = OverrideApiRequest()

    # ----------------------------------------------------------------------------------
    # Instagramは画像を投稿してIDを取得する必要がある
    #! 画像は公開されてる写真ではないとNG

    async def _getMediaId(
        self, imageUrl: str, notifyFunc: Optional[Callable[[str], None]] = None
    ):
        self.logger.info(f"********** _getMediaId start **********")

        self.logger.debug(f"imageUrl: {imageUrl}")
        Endpoint_base_url = EndPoint.Instagram.value

        response = await self.apiRequest.apiRequest(
            method="POST",
            endpointUrl=Endpoint_base_url.format(self.instBusinessAccountId),
            params={"image_url": imageUrl, "instAccessToken": self.instAccessToken},
            notifyFunc=notifyFunc,
        )

        # responseの中にあるidを取得
        if response:
            mediaId = response["id"]
            self.logger.info(f"********** _getMediaId start **********")
            return mediaId
        else:
            self.logger.error(f"写真の取得に失敗 {imageUrl}")

    # ----------------------------------------------------------------------------------

    async def process(
        self,
        imageUrl: str,
        message: str,
        notifyFunc: Optional[Callable[[str], None]] = None,
    ):
        self.logger.info(f"********** process start **********")
        try:
            self.logger.debug(f"")
            Endpoint_base_url = EndPoint.InstagramImage.value

            mediaId = await self._getMediaId(imageUrl, notifyFunc)

            response = await self.apiRequest.apiRequest(
                method="POST",
                endpointUrl=Endpoint_base_url.format(self.instBusinessAccountId),
                params={
                    "creation_id": mediaId,
                    "caption": message,
                    "instAccessToken": self.instAccessToken,
                },
                notifyFunc=notifyFunc,
            )

            if response:
                if response.status_code == 200:
                    self.logger.info(f"Instagram 投稿成功")
                    self.logger.info(f"********** process end **********")

                    if notifyFunc:
                        notifyFunc(f"Instagram 投稿成功 {message[15:]}")

                else:
                    self.logger.debug(
                        f"resがエラーで帰ってきてる{response.status_code}"
                    )

            else:
                self.logger.debug(f"responseなし。")

        except Exception as e:
            self.logger.debug(f"responseなし。")
            raise


# ----------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------
# **********************************************************************************
