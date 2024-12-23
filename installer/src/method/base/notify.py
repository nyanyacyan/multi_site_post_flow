# coding: utf-8
# 2023/6/16  更新
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import

import time
import os
import requests
from ..const_domain_search import EndPoint
from PIL import Image
from dotenv import load_dotenv
import aiofiles

# 自作モジュール
from .utils import Logger
from .decorators import Decorators
from .ApiRequest import ApiRequest

from const_str import FileName


decoInstance = Decorators()

load_dotenv()


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************
# LINE通知


class LineNotify:
    def __init__(self):
        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

        # インスタンス
        self.apiRequest = ApiRequest()

    # ----------------------------------------------------------------------------------
    # LINE本文のみ送信
    # os.getenvにてトークンなどを呼び出す

    def line_notify(self, lineToken, message):
        try:
            self.logger.info(f"********** line_notify start **********")

            self.logger.debug(f"message: {message}")

            line_end_point = EndPoint.Line.value
            headers = {"Authorization": f"Bearer {lineToken}"}
            data = {"message": message}

            response = requests.post(line_end_point, headers=headers, data=data)

            if response.status_code == 200:
                self.logger.info("送信成功")
            else:
                self.logger.error(
                    f"送信に失敗しました: ステータスコード {response.status_code},{response.text}"
                )

            self.logger.info(f"********** line_notify end **********")

        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"Connection error: {e}")
            raise

        except requests.exceptions.Timeout as e:
            self.logger.error(f"Timeout error: {e}")
            raise

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error: {e}")
            raise

        except Exception as e:
            self.logger.error(f"line_image_notify 処理中にエラーが発生:{e}")
            raise

    # ----------------------------------------------------------------------------------
    # LINE 本文＋画像を送信
    # os.getenvにてトークンなどを呼び出す

    def line_image_notify(self, lineToken, message, image_path):
        try:
            self.logger.info(f"********** line_image_notify start **********")

            self.logger.debug(f"message: {message}")

            line_end_point = EndPoint.Line.value
            headers = {"Authorization": f"Bearer {lineToken}"}
            data = {"message": message}

            with open(image_path, mode="rb") as jpeg_bin:
                files = {"imageFile": (image_path, jpeg_bin, "image/jpeg")}
                response = requests.post(
                    line_end_point, headers=headers, data=data, files=files
                )

            if response.status_code == 200:
                self.logger.debug("送信成功")
            else:
                self.logger.error(
                    f"送信に失敗しました: ステータスコード {response.status_code},{response.text}"
                )

            self.logger.info(f"********** line_image_notify end **********")

        except FileNotFoundError as e:
            self.logger.error(f"{image_path} が見つかりません:{e}")
            raise

        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"Connection error: {e}")
            raise

        except requests.exceptions.Timeout as e:
            self.logger.error(f"Timeout error: {e}")
            raise

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error: {e}")
            raise

        except Exception as e:
            self.logger.error(f"line_image_notify 処理中にエラーが発生:{e}")
            raise

    # ----------------------------------------------------------------------------------

    @decoInstance.asyncFuncBase
    async def lineDataFileNotify(self, lineToken, message, filePath):
        lineEndPoint = EndPoint.Line.value
        headers = {
            "Authorization": f"Bearer {lineToken}",
            "content-Type": "application/x-www-form-urlencoded",
        }

        async with aiofiles.open(filePath, "r", encoding="utf-8") as file:
            fileContent = await file.read()
            data = {"message": message + "\n" + fileContent}

            response = await self.apiRequest.apiRequest(
                method="post",
                endpointUrl=lineEndPoint,
                params=None,
                headers=headers,
                json=None,
                data=data,
            )

            if isinstance(response, dict):
                self.logger.info(f"送信成功")
            else:
                self.logger.error(f"送信に失敗しました: {response}")


# ----------------------------------------------------------------------------------
# **********************************************************************************
# Chatwork通知


class ChatworkNotify:
    def __init__(self):
        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

        # chatwork Token
        self.chatwork_notify_token = os.getenv("CHATWORK_NOTIFY_TOKEN")
        self.chatwork_roomid = os.getenv("CHATWORK_ROOMID")

    # ----------------------------------------------------------------------------------
    # 本文のみ送信
    # os.getenvにてトークンなどを呼び出す

    def chatwork_notify(self, chatwork_roomid, chatwork_notify_token, message):
        try:
            end_point = EndPoint.Chatwork.value
            url = end_point + "/rooms/" + str(chatwork_roomid) + "/messages"
            headers = {"X-ChatWorkToken": chatwork_notify_token}
            params = {"body": {message}}
            self.logger.debug(
                f"\n end_point: {end_point}\n url: {url}\n headers: {headers}\n params: {params}"
            )

            response = requests.post(url, headers=headers, params=params)

            if response.status_code == 200:
                self.logger.info("送信成功")
            else:
                self.logger.error(
                    f"送信に失敗しました: ステータスコード {response.status_code},{response.text}"
                )

        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"Connection error: {e}")
            raise

        except requests.exceptions.Timeout as e:
            self.logger.error(f"Timeout error: {e}")
            raise

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error: {e}")
            raise

        except Exception as e:
            self.logger.error(f"line_image_notify 処理中にエラーが発生:{e}")
            raise

    # ----------------------------------------------------------------------------------
    # 本文＋画像
    # os.getenvにてトークンなどを呼び出す

    def chatwork_image_notify(
        self,
        chatwork_roomid: str,
        chatwork_notify_token: str,
        message: str,
        img_path: str,
    ):
        try:
            # 画像サイズを確認して大きかった場合にはリサイズ
            resize_image_path = self._isChecked_image_size(img_path)
            end_point = EndPoint.Chatwork.value
            url = end_point + "/rooms/" + str(chatwork_roomid) + "/files"
            headers = {"X-ChatWorkToken": chatwork_notify_token}

            # 画像の読み込みを実施
            with open(str(resize_image_path), "rb") as png_bin:
                files = {"file": (str(resize_image_path), png_bin, "image/png")}
                data = {"message": message}

                self.logger.debug(
                    f"\n data: {data}\n resize_image_path: {resize_image_path}\n end_point: {end_point}\n url: {url}\n headers: {headers}"
                )

                # chatworkに画像とメッセージを送る
                response = requests.post(url, headers=headers, data=data, files=files)

            if response.status_code == 200:
                self.logger.debug("送信成功")

            else:
                self.logger.error(
                    f"送信に失敗しました: ステータスコード {response.status_code}: {response.text}"
                )
                return self.logger.error("送信処理に失敗（画像削除完了）")

        except FileNotFoundError as e:
            self.logger.error(f"{img_path} が見つかりません:{e}")
            raise

        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"Connection error: {e}")
            raise

        except requests.exceptions.Timeout as e:
            self.logger.error(f"Timeout error: {e}")
            raise

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error: {e}")
            raise

        except Exception as e:
            self.logger.error(f"chatwork_image_notify 処理中にエラーが発生:{e}")
            raise

    # ----------------------------------------------------------------------------------
    # 画像のサイズによって送信できるようにリサイズ

    def _isChecked_image_size(self, img_path, max_mb_size=5):
        try:
            if img_path and os.path.exists(
                img_path
            ):  # os.path.existsは有効なpathなのかを確認する
                # バイト単位で表示。バイト（B）: コンピュータのデータの最小単位。
                img_size = os.path.getsize(img_path)

                # キロバイト（KB）: 1 KB = 1024 バイト、メガバイト（MB）: 1 MB = 1024 キロバイト = 1024 * 1024 バイト。
                img_MB_size = img_size / (1024 * 1024)
                self.logger.debug(
                    f"\n img_MB_size: {img_MB_size}\n max_mb_size: {max_mb_size}"
                )

                # 指定したMAXのサイズよりも大きかったら処理する
                if img_MB_size > max_mb_size:

                    # resizeする画像の名称を定義
                    path, ext = os.path.splitext(img_path)
                    resize_image_path = f"{path}_resize{ext}"
                    self.logger.debug(f"resize_image_path: {resize_image_path}")

                    # 指定の画像を開く
                    with Image.open(img_path) as png:

                        # MAXのサイズよりも小さかったら繰り返し処理する
                        while img_MB_size > max_mb_size:
                            png = png.resize((png.width // 2, png.height // 2))
                            png.save(resize_image_path, "PNG")

                            img_size = os.path.getsize(resize_image_path)
                            img_MB_size = img_size / (1024 * 1024)

                    return resize_image_path
                else:
                    return img_path

            else:
                return img_path

        except Exception as e:
            self.logger.error(f"_image_resize 処理中にエラーが発生:{e}")
            raise


# ----------------------------------------------------------------------------------
# **********************************************************************************
# Slack通知


class SlackNotify:
    def __init__(self):
        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

        # token
        # 通知するチャンネルから権限を選択=> アプリインストールしてトークン作成=> .envに貼り付ける
        # slackの場合、メッセージ+画像はNG。画像+コメントになる
        self.slack_notify_token = os.getenv("SLACK_NOTIFY_TOKEN")
        self.slack_channel = os.getenv("SLACK_CHANNEL")

    # ----------------------------------------------------------------------------------
    # 本文のみ
    # os.getenvにてトークンなどを呼び出す

    def slack_notify(self, slack_notify_token, message):
        try:
            self.logger.info(f"********** slack_notify start **********")

            self.logger.debug(f"message: {message}")

            end_point = EndPoint.Slack.value

            headers = {"Authorization": f"Bearer {slack_notify_token}"}
            data = {"channel": {self.slack_channel}, "text": {message}}

            response = requests.post(end_point, headers=headers, data=data)

            if response.status_code == 200:
                self.logger.info(f"********** slack_notify end **********")
                return self.logger.info(f"送信処理完了")

            else:
                self.logger.info(f"********** slack_notify end **********")
                return self.logger.error(
                    f"送信に失敗しました: ステータスコード {response.status_code},{response.text}"
                )

        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"Connection error: {e}")
            raise

        except requests.exceptions.Timeout as e:
            self.logger.error(f"Timeout error: {e}")
            raise

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error: {e}")
            raise

        except Exception as e:
            self.logger.error(f"line_image_notify 処理中にエラーが発生:{e}")
            raise

    # ----------------------------------------------------------------------------------
    # 本文＋画像
    # os.getenvにてトークンなどを呼び出す

    def slack_image_notify(self, slack_notify_token, message, img_path):
        try:
            end_point = EndPoint.Slack.value

            headers = {"Authorization": f"Bearer {slack_notify_token}"}
            data = {
                "channels": self.slack_channel,
                "initial_comment": message,
                "filename": os.path.basename(img_path),
            }

            # 画像ファイルを指定する（png or jpeg）
            with open(img_path, "rb") as jpeg_bin:
                files = {"file": (img_path, jpeg_bin, "image/jpeg")}

                # Slackに画像とメッセージを送る
                response = requests.post(
                    end_point, headers=headers, data=data, files=files
                )

            if response.status_code == 200:
                return self.logger.info(f"送信処理完了")

            else:
                return self.logger.error(
                    f"送信に失敗しました: ステータスコード {response.status_code},{response.text}"
                )

        except FileNotFoundError as e:
            self.logger.error(f"指定されてるファイルが見つかりません:{e}")
            raise

        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"Connection error: {e}")
            raise

        except requests.exceptions.Timeout as e:
            self.logger.error(f"Timeout error: {e}")
            raise

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error: {e}")
            raise

        except Exception as e:
            self.logger.error(f"line_image_notify 処理中にエラーが発生:{e}")
            raise


# ----------------------------------------------------------------------------------
# **********************************************************************************
# Discord通知


class DiscordNotify:
    def __init__(self):
        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

    # ----------------------------------------------------------------------------------
    # 本文のみ
    # os.getenvにてトークンなどを呼び出す必要なし

    def discord_notify(self, message):
        try:
            self.logger.info(f"********** slack_notify start **********")

            self.logger.debug(f"message: {message}")

            end_point = EndPoint.Discord.value

            response = requests.post(end_point, data={"content": message})

            if response.status_code == 204:
                self.logger.info(f"********** slack_notify end **********")
                return self.logger.info(f"送信処理完了")

            else:
                self.logger.info(f"********** slack_notify end **********")
                return self.logger.error(
                    f"送信に失敗しました: ステータスコード {response.status_code},{response.text}"
                )

        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"Connection error: {e}")
            raise

        except requests.exceptions.Timeout as e:
            self.logger.error(f"Timeout error: {e}")
            raise

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error: {e}")
            raise

        except Exception as e:
            self.logger.error(f"line_image_notify 処理中にエラーが発生:{e}")
            raise

    # ----------------------------------------------------------------------------------
    # 本文＋画像
    # os.getenvにてトークンなどを呼び出す必要なし

    def discord_image_notify(self, message, img_path):
        try:
            self.logger.info(f"********** discord_image_notify start **********")

            self.logger.debug(f"message: {message}")
            end_point = EndPoint.Discord.value

            with open(img_path, "rb") as jpeg_bin:
                files = {"file": (img_path, jpeg_bin, "image/jpeg")}

                response = requests.post(
                    end_point, data={"content": message}, files=files
                )

            if response.status_code == 204:
                self.logger.info(f"********** discord_image_notify end **********")
                return self.logger.info(f"送信処理完了")

            else:
                self.logger.info(f"********** discord_image_notify end **********")
                return self.logger.error(
                    f"送信に失敗しました: ステータスコード {response.status_code},{response.text}"
                )

        except FileNotFoundError as e:
            self.logger.error(f"指定されてるファイルが見つかりません:{e}")
            raise

        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"Connection error: {e}")
            raise

        except requests.exceptions.Timeout as e:
            self.logger.error(f"Timeout error: {e}")
            raise

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error: {e}")
            raise

        except Exception as e:
            self.logger.error(f"line_image_notify 処理中にエラーが発生:{e}")
            raise


# ----------------------------------------------------------------------------------
# **********************************************************************************
