# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# 2024/9/8 更新

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import

import os, sys, time, pickle, subprocess, sqlite3
import asyncio
import gspread
import aiohttp
from selenium.common.exceptions import WebDriverException

from googleapiclient import errors  # pip install google-api-python-client
from typing import Callable, Optional, Any



# 自作モジュール
from .utils import Logger
from .sysCommand import SysCommand
from .popup import Popup


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************
# 例外処理をまとめたクラス


class NetworkHandler:
    def __init__(self):

        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

    # ----------------------------------------------------------------------------------
    # retryするネットワークの例外処理

    def gssRetryHandler(self, e: Exception, maxRetry: int, delay: int, retryCount: int):
        # Exceptionでキャッチしてからそれぞれのエラーをキャッチする
        if isinstance(e, gspread.exceptions.APIError) or isinstance(
            e, errors.HttpError
        ):
            self.logger.error(
                f"スプシ: サーバーエラーのためリトライ{retryCount}/{maxRetry} {e}"
            )

            # 上限に達した処理
            if retryCount >= maxRetry:
                self.logger.error(
                    f"スプシ: サーバーエラーのためリトライ リトライ上限のため終了"
                )
                # sys.exit(1)
            # 送らせて実行
            time.sleep(delay)

        # Exception
        else:
            self.logger.error(f"スプシ: 処理中にエラーが発生 {e}")
            # sys.exit(1)

        return retryCount


# ----------------------------------------------------------------------------------
# **********************************************************************************


class ResponseStatusCode:
    def __init__(self):

        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

    # ----------------------------------------------------------------------------------
    # response.statusが「200」以外の際の例外処理（リトライ）(通知あり)
    # Exceptionでキャッチしてからそれぞれのエラーをキャッチする

    async def retryHandler(
        self,
        e: Exception,
        response: Any,
        retryCount: int,
        notifyFunc: Optional[Callable[[str], None]] = None,
        maxRetry: int = 3,
        delay: int = 30,
    ):

        # クライアント側のなにかしらのエラー
        if isinstance(e, aiohttp.ClientError):
            await self.errorRetryAction(
                e=e,
                errorComment="API側にてエラーが発生",
                retryCount=retryCount,
                notifyFunc=notifyFunc,
                maxRetry=maxRetry,
                delay=delay,
            )

        # タイムアウトエラー
        elif isinstance(e, asyncio.TimeoutError):
            await self.errorRetryAction(
                e=e,
                errorComment="タイムアウトエラー",
                retryCount=retryCount,
                notifyFunc=notifyFunc,
                maxRetry=maxRetry,
                delay=delay,
            )

        else:
            # サーバーエラー
            if 500 <= response.status <= 599:
                await self.errorRetryAction(
                    e=e,
                    errorComment="サーバーエラー",
                    retryCount=retryCount,
                    notifyFunc=notifyFunc,
                    maxRetry=maxRetry,
                    delay=delay,
                )

            else:
                # サーバーエラー以外の場合のエラーコード
                self.noRetryAction(
                    e=e, errorComment="処理中にエラーが発生", notifyFunc=notifyFunc
                )

    # ----------------------------------------------------------------------------------
    # retryアクションあり（通知あり）

    async def errorRetryAction(
        self,
        e: Exception,
        errorComment: str,
        retryCount: int,
        notifyFunc: Optional[Callable[[str], None]] = None,
        maxRetry: int = 3,
        delay: int = 30,
    ):
        self.logger.error(f"{errorComment} :{retryCount}/{maxRetry} {e}")

        # 上限に達した処理
        if retryCount >= maxRetry:
            # サーバーエラー以外の場合のエラーコード
            self.logger.error(f"[リトライ上限] 強制終了 {errorComment} ")
            if not notifyFunc is None:
                notifyFunc(errorComment)
            sys.exit(1)

        # 送らせて実行
        await asyncio.sleep(delay)

    # ----------------------------------------------------------------------------------
    # retryアクションなし（通知あり）

    def noRetryAction(
        self,
        e: str,
        errorComment: str,
        notifyFunc: Optional[Callable[[str], None]] = None,
    ):
        self.logger.error(f"{errorComment} :{e}")

        if not notifyFunc is None:
            self.logger.error(f"{errorComment} :{e}")
            notifyFunc(errorComment)
        sys.exit(1)


# ----------------------------------------------------------------------------------
# **********************************************************************************


class FileWriteError:
    def __init__(self):

        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

    # ----------------------------------------------------------------------------------

    def fileNotFoundErrorHandler(
        self,
        e: Exception,
        fullPath: str,
        retryCount: int,
        maxRetry: int,
        notifyFunc: Optional[Callable[[str], None]] = None,
        delay: int = 2,
    ):
        self.logger.error(f"[ファイルPathが見つからにためディレクトリの作成]:{e}")

        # exist_ok=True→すでにディレクトリが合ったとしてもエラーにならない
        os.makedirs(fullPath, exist_ok=True)

        self.logger.debug(f"retryCount: {retryCount}")
        self.logger.debug(f"maxRetry: {maxRetry}")

        # 上限に達した処理
        if retryCount >= maxRetry:
            # サーバーエラー以外の場合のエラーコード
            self.logger.error(f"[ファイルの書き込み失敗]:{e} ")
            if not notifyFunc is None:
                notifyFunc(f"[ファイルの書き込み失敗]:{e} ")
            # sys.exit(1)

        self.logger.debug(f"リトライ実施")
        time.sleep(delay)

    # ----------------------------------------------------------------------------------

    def fileErrorHandler(
        self, e: Exception, notifyFunc: Optional[Callable[[str], None]] = None
    ):
        errorMessage = {
            PermissionError: "[ファイルの書込権限がありません]",
            IOError: "[入出力エラーが発生]",
            UnicodeDecodeError: "[デコード中にエラーが発生]",
            pickle.PickleError: "",
        }

        errorType = type(e)
        errorMessage = errorMessage.get(errorType, "[処理中に何らかのエラーが発生]")

        self.logger.error(f"{errorMessage}:{e}")

        if not notifyFunc is None:
            notifyFunc(e)


# ----------------------------------------------------------------------------------
# **********************************************************************************


class PickleWriteError:
    def __init__(self):

        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

    # ----------------------------------------------------------------------------------

    def handler(
        self,
        fileName: str,
        e: Exception,
        notifyFunc: Optional[Callable[[str], None]] = None,
    ):
        errorMessage = {
            PermissionError: "[ファイルの書込権限がありません]",
            IOError: "[入出力エラーが発生]",
            UnicodeDecodeError: "[デコード中にエラーが発生]",
            pickle.PickleError: "[データのpickle化中にエラーが発生]",
            ValueError: "[pickle化させようとしたデータが None ]",
            FileNotFoundError: "[pickleを書込場所が見つまりません（書込場所は生成されてるはず・・・）]",
        }

        errorType = type(e)

        # 2つ目の引数はgetできなかったときの表示
        errorMessage = errorMessage.get(
            errorType, "[pickle書込中に何らかのエラーが発生]"
        )

        self.logger.error(f"{errorMessage} {fileName}:{e}")

        if not notifyFunc is None:
            notifyFunc(e)


# ----------------------------------------------------------------------------------
# **********************************************************************************


class PickleReadError:
    def __init__(self):

        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

    # ----------------------------------------------------------------------------------

    def pickleErrorHandler(
        self,
        fileName: str,
        e: Exception,
        notifyFunc: Optional[Callable[[str], None]] = None,
    ):
        errorMessage = {
            PermissionError: "[ファイルの書込権限がありません]",
            IOError: "[入出力エラーが発生]",
            UnicodeDecodeError: "[デコード中にエラーが発生]",
            pickle.PickleError: "[データのpickle化中にエラーが発生]",
            ValueError: "[pickle化させようとしたデータが None]",
            FileNotFoundError: "[pickleFileが見つまりません]",
            TypeError: "[バイナリデータではない]",
        }

        errorType = type(e)

        # 2つ目の引数はgetできなかったときの表示
        errorMessage = errorMessage.get(
            errorType, "[pickle読込中に何らかのエラーが発生]"
        )

        self.logger.error(f"{errorMessage} {fileName}:{e}")

        if not notifyFunc is None:
            notifyFunc(e)

        return None


# ----------------------------------------------------------------------------------
# **********************************************************************************


class AccessFileNotFoundError:
    def __init__(self):

        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

    # ----------------------------------------------------------------------------------

    def accessFileNotFoundError(self, fileName: str, e: Exception):
        if isinstance(e, FileNotFoundError):
            self.logger.error(f"指定された場所に[{fileName}]がありません: {e}")

        else:
            self.logger.error(f"Pathの処理中にエラーが発生いたしました: {e}")
        return None


# ----------------------------------------------------------------------------------
# **********************************************************************************


class RequestRetryAction:
    def __init__(self):

        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

    # ----------------------------------------------------------------------------------
    # statusCodeを検知してそれぞれでエラーを検知して返す

    def handleStatus(
        self,
        statusCode: int,
        retryCount: int,
        maxRetry: int = 3,
        delay: int = 30,
        notifyFunc: Optional[Callable[[str], None]] = None,
    ):
        if 500 <= statusCode < 600:
            self.apiServerHandler(
                statusCode=statusCode,
                retryCount=retryCount,
                maxRetry=maxRetry,
                delay=delay,
                notifyFunc=notifyFunc,
            )
            return 500

        elif 400 <= statusCode < 500:
            retryCount = maxRetry
            self.apiHandler(
                statusCode=statusCode,
                retryCount=retryCount,
                maxRetry=maxRetry,
                delay=delay,
                notifyFunc=notifyFunc,
            )
            return 400

    # ----------------------------------------------------------------------------------

    async def apiServerHandler(
        self,
        statusCode: int,
        retryCount: int,
        maxRetry: int = 3,
        delay: int = 30,
        notifyFunc: Optional[Callable[[str], None]] = None,
    ):
        errorMessage = {
            500: "[Internal Server Error]: サーバーがリクエストの処理に失敗してます",
            502: "[Bad Gateway]: サーバーが別のサーバーからの無効な応答を受け取ってしまってます",
            503: "[Service Unavailable]: サーバーが一時的に利用できていない",
            504: "[Gateway Timeout]: サーバータイムアウト",
        }

        # 2つ目の引数はgetできなかったときの表示
        errorMessage = errorMessage.get(statusCode)

        self.logger.error(f"{errorMessage}")

        # 上限に達した処理
        if retryCount >= maxRetry:
            self.logger.error(
                f"リトライ上限に達したため終了{statusCode}:{errorMessage}"
            )
            if not notifyFunc is None:
                notifyFunc(errorMessage)
            # sys.exit(1)

        self.logger.debug(f"リトライ実施")
        await asyncio.sleep(delay)

    # ----------------------------------------------------------------------------------

    async def apiHandler(
        self, statusCode: int, notifyFunc: Optional[Callable[[str], None]] = None
    ):
        errorMessage = {
            400: "[Bad Request]: リクエスト方法が誤ってます",
            401: "[Unauthorized]: 認証情報が正しくありません。",
            403: "[Forbidden]: 権限がないため、拒否されてます。",
            404: "[Not Found]: リソースが見つかりません（URLが間違ってます）",
            405: "[Method Not Allowed]: 許可されてないアクセス方法です（GET,POSTなどではない可能性があります）",
            429: "[Too Many Requests]: ",
        }

        # 2つ目の引数はgetできなかったときの表示
        errorMessage = errorMessage.get(statusCode)

        self.logger.error(errorMessage)
        if not notifyFunc is None:
            notifyFunc(errorMessage)
        # sys.exit(1)

        return statusCode


# ----------------------------------------------------------------------------------
# **********************************************************************************


class FileReadHandler:
    def __init__(self):

        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

    # ----------------------------------------------------------------------------------

    def fileReadHandler(self, e: Exception):
        errorMessage = {
            FileNotFoundError: "[指定のFileが見つかりません]",
            PermissionError: "[ファイルにアクセスする権限がありません]",
            ValueError: "[File形式のTypeがアンマッチしてます]",
        }

        errorType = type(e)

        # 2つ目の引数はgetできなかったときの表示
        errorMessage = errorMessage.get(errorType, "[fileの読込で何らかのエラーが発生]")

        self.logger.error(f"{errorMessage}: {e}")

        # sys.exit(1)
        return None


# ----------------------------------------------------------------------------------
# **********************************************************************************


class GeneratePromptHandler:
    def __init__(self):

        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

    # ----------------------------------------------------------------------------------

    def generatePromptHandler(self, e: Exception):
        errorMessage = {
            KeyError: "[指定したColumn名がDataFrameに存在しません]",
            TypeError: "[型が違うため処理が進められません]",
            ValueError: "[constにあるformat文に {list} が入ってない定数があります]",
        }

        errorType = type(e)
        errorMessage = errorMessage.get(errorType, "[fileの読込で何らかのエラーが発生]")
        self.logger.error(f"{errorMessage}: {e}")

        # sys.exit(1)
        return None


# ----------------------------------------------------------------------------------
# **********************************************************************************


class ChromeHandler:
    def __init__(self):

        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

        # instance
        self.popup = Popup()
        self.sysCommand = SysCommand()

    # ----------------------------------------------------------------------------------

    def chromeHandler(
        self,
        e: Exception,
        popupTitle: str,
        comment: str,
        func: Optional[Callable[[], None]],
    ):
        errorMessage = {
            subprocess.CalledProcessError: "[Chromeのバージョンが不正です。PCの再起動が必要です。]",
            RuntimeError: "[Chromeのバージョンが不一致です。PCの再起動が必要です。]",
            ValueError: "[Chromeのバージョンが不一致です。PCの再起動が必要です。]",
            WebDriverException: "[Chromeを正しく起動できませんでした。PCの再起動が必要です。]",
        }

        errorType = type(e)
        errorMessage = errorMessage.get(
            errorType,
            "[Chromeを正しく起動できませんでした。PCの再起動が必要です。再起動でも改善されない場合には作成者にご連絡下さい]",
        )
        self.logger.error(f"{errorMessage}: {e}")

        self.popup.popupCommentChoice(popupTitle=popupTitle, comment=comment, func=func)


# ----------------------------------------------------------------------------------
# **********************************************************************************


class SqliteError:
    def __init__(self):

        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

    # ----------------------------------------------------------------------------------

    def Handler(self, e: Exception, notifyFunc: Optional[Callable[[], None]] = None):
        errorMessages = {
            sqlite3.IntegrityError: "[データの整合性エラー]",
            sqlite3.OperationalError: "[操作エラー（テーブルがない等）]",
            sqlite3.ProgrammingError: "[プログラミングエラー（SQL構文ミス等）]",
            sqlite3.DatabaseError: "[データベースに関するエラー]",
        }

        errorType = type(e)
        errorMessage = errorMessages.get(errorType, "[不明なSQLiteエラー]")
        self.logger.error(f"{errorMessage}: {e}")

        if not notifyFunc is None:
            notifyFunc(e)


# ----------------------------------------------------------------------------------
# **********************************************************************************
