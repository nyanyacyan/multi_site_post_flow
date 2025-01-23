# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# テストOK
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import time
from functools import wraps
from typing import Callable, Optional
import aiohttp
import asyncio


# 自作モジュール
from .utils import Logger
from .path import BaseToPath
from .sysCommand import SysCommand
from method.const_str import ErrorMessage
from .errorHandlers import (
    NetworkHandler,
    FileWriteError,
    RequestRetryAction,
    FileReadHandler,
    GeneratePromptHandler,
    ChromeHandler,
    SqliteError,
)
from dotenv import load_dotenv

load_dotenv()

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************
# 一連の流れ


class Decorators:
    def __init__(self):

        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

        # インスタンス化
        self.networkError = NetworkHandler()
        self.fileError = FileWriteError()
        self.basePath = BaseToPath()
        self.requestError = RequestRetryAction()
        self.fileHandler = FileReadHandler()
        self.generatePromptHandler = GeneratePromptHandler()
        self.chromeHandler = ChromeHandler()
        self.sysCommand = SysCommand()
        self.sqliteHandler = SqliteError()

    # ----------------------------------------------------------------------------------

    def funcBase(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            self.logger.info(f"********** {func.__name__} start **********")
            self.logger.debug(f"引数:\nargs={args}, kwargs={kwargs}")

            # 実行する関数を定義
            result = func(*args, **kwargs)

            if result is None:
                self.logger.warning(f"{func.__name__} resultが None")
            self.logger.info(f"{func.__name__} result:\n{result}")
            # ローカル変数をすべて出力
            # self.logger.debug(f"利用した変数一覧:\n{locals()}")

            return result

        return wrapper

    # ----------------------------------------------------------------------------------

    def asyncFuncBase(self, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            self.logger.info(f"********** {func.__name__} start **********")
            self.logger.debug(f"引数:\nargs={args}, kwargs={kwargs}")

            # 実行する関数を定義
            result = await func(*args, **kwargs)

            # ローカル変数をすべて出力
            self.logger.debug(f"利用した変数一覧:\n{locals()}")

            return result

        return wrapper

    # ----------------------------------------------------------------------------------

    def retryAction(self, maxRetry: int = 3, delay: int = 30):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                self.logger.info(f"引数:\nargs={args}, kwargs={kwargs}")
                retryCount = 0
                while retryCount < maxRetry:
                    try:
                        self.logger.info(
                            f"********** {func.__name__} start {retryCount + 1}回目 **********"
                        )

                        result = func(*args, **kwargs)

                        return result

                    except Exception as e:
                        retryCount += 1
                        retryCount = self.networkError.gssRetryHandler(
                            e=e, maxRetry=maxRetry, delay=delay, retryCount=retryCount
                        )

            return wrapper

        return decorator

    # ----------------------------------------------------------------------------------

    def fileRetryAction(
        self,
        maxRetry: int = 2,
        delay: int = 2,
        notifyFunc: Optional[Callable[[str], None]] = None,
    ):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                self.logger.debug(f"引数:\nargs={args}, kwargs={kwargs}")

                retryCount = 0
                while retryCount < maxRetry:
                    try:
                        self.logger.info(
                            f"********** {func.__name__} start {retryCount + 1}回目 **********"
                        )

                        fileName = kwargs.get("fileName")

                        if fileName:
                            func(*args, **kwargs)
                            self.logger.debug(f"{func.__name__} の書込に成功")
                            self.logger.debug(f"利用した変数一覧:\n{locals()}")
                            break

                        # ローカル変数をすべて出力

                    except FileNotFoundError as fe:
                        retryCount += 1

                        # fileName = kwargs.get('fileName')にてファイル名を取得
                        fileName = kwargs.get("fileName")
                        fullPath = self.basePath.getInputDataFilePath(fileName)
                        self.fileError.fileNotFoundErrorHandler(
                            e=fe,
                            fullPath=fullPath,
                            maxRetry=maxRetry,
                            retryCount=retryCount,
                            delay=delay,
                        )

                    except Exception as e:
                        retryCount = maxRetry
                        retryCount = self.fileError.fileErrorHandler(
                            e=e, notifyFunc=notifyFunc
                        )

            return wrapper

        return decorator

    # ----------------------------------------------------------------------------------

    def requestRetryAction(
        self,
        maxRetry: int = 3,
        delay: int = 30,
        notifyFunc: Optional[Callable[[str], None]] = None,
    ):
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                self.logger.debug(f"引数:\nargs={args}, kwargs={kwargs}")
                retryCount = 0
                while retryCount < maxRetry:
                    try:
                        self.logger.debug(
                            f"********** {func.__name__} start {retryCount + 1}回目 **********"
                        )

                        result = await func(*args, **kwargs)

                        self.logger.debug(f"result\n{result}")

                        if isinstance(result, dict):
                            self.logger.debug("APIリクエストは成功")
                            return result

                        elif 500 <= result < 600:
                            retryCount += 1
                            self.logger.warning(
                                f"サーバーエラーです。 {result} 再度リクエスト実施"
                            )
                            await self.requestError.apiServerHandler(
                                statusCode=result,
                                retryCount=retryCount,
                                maxRetry=maxRetry,
                                delay=delay,
                                notifyFunc=notifyFunc,
                            )

                        elif 400 <= result < 500:
                            self.logger.error(f"エラーです。statusCodeは {result} です")
                            statusCode = await self.requestError.apiHandler(
                                statusCode=result, notifyFunc=notifyFunc
                            )
                            return statusCode

                    except aiohttp.ClientError as e:
                        retryCount += 1
                        self.logger.error(
                            f"ネットワークの一時的なエラーを検知: 再リクエスト実施: {e}"
                        )
                        await asyncio.sleep(delay)

                    except Exception as e:
                        retryCount = maxRetry
                        self.logger.error(f"リクエスト中にエラーが発生: {e}")

            return wrapper

        return decorator

    # ----------------------------------------------------------------------------------
    #  -> Optional[str]:はNoneをエラーとしない

    def characterLimitRetryAction(
        self,
        maxlen: int = 100,
        maxCount: int = 3,
        timeout: int = 30,
        delay: int = 2,
        notifyFunc: Optional[Callable[[str], None]] = None,
    ) -> (
        Callable
    ):  # -> Callable[..., _Wrapped[Callable[..., Any], Any, Callable[...:# -> Callable[..., _Wrapped[Callable[..., Any], Any, Callable[...:
        def decorator(func) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs) -> Optional[str]:
                self.logger.info(f"引数:\nargs={args}, kwargs={kwargs}")

                # 初期化
                retryCount = 0
                wordCount = 0
                startTime = time.time()

                while retryCount < maxCount:
                    elapsedTime = time.time() - startTime
                    if elapsedTime >= timeout:
                        raise TimeoutError(
                            f"一定時間経過のためタイムアウトエラー {func.__name__}"
                        )

                    try:
                        self.logger.info(
                            f"********** {func.__name__} start {retryCount + 1}回目 **********"
                        )

                        result = await func(*args, **kwargs)
                        assistantMsg = result["assistantMsg"]["content"]
                        self.logger.debug(assistantMsg)
                        wordCount = len(assistantMsg)

                        if wordCount <= maxlen:
                            self.logger.debug(
                                f"[文字数は条件を満たしてます] 文字数: {wordCount}"
                            )
                            return result
                        else:
                            retryCount += 1
                            self.logger.warning(
                                f"文字数がオーバーのため再リクエスト:\nwordCount: {wordCount}\nmaxlen: {maxlen}"
                            )

                        if retryCount >= maxCount:
                            overRetryComment = f"[指定回数以上の実施が合ったためエラー] {result}回実施: {func.__name__}"
                            self.logger.error(overRetryComment)
                            if notifyFunc:
                                notifyFunc(overRetryComment)
                            return None

                        await asyncio.sleep(delay)

                    except Exception as e:
                        self.logger.error(
                            f"{func.__name__} 処理中ににエラーが発生: {e}"
                        )
                        return None

            return wrapper

        return decorator

    # ----------------------------------------------------------------------------------

    def fileRead(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                self.logger.info(f"********** {func.__name__} start **********")
                self.logger.debug(f"引数:\nargs={args}, kwargs={kwargs}")

                # 実行する関数を定義
                result = func(*args, **kwargs)

                # kwargsから抜き取る
                fileName = kwargs.get("fileName")

                self.logger.debug(f"Fileの読込成功: {fileName}")

                # ローカル変数をすべて出力
                self.logger.debug(f"利用した変数一覧:\n{locals()}")

                return result

            except Exception as e:
                self.fileHandler.fileReadHandler(e=e)

        return wrapper

    # ----------------------------------------------------------------------------------

    def generatePrompt(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                self.logger.info(f"********** {func.__name__} start **********")
                self.logger.debug(f"引数:\nargs={args}, kwargs={kwargs}")

                # 実行する関数を定義
                result = func(*args, **kwargs)

                self.logger.debug(f"promptの生成に成功: {func.__name__}")

                # ローカル変数をすべて出力
                self.logger.debug(f"利用した変数一覧:\n{locals()}")

                return result

            except Exception as e:
                self.generatePromptHandler.generatePromptHandler(e=e)

        return wrapper

    # ----------------------------------------------------------------------------------

    def chromeSetup(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                self.logger.info(f"********** {func.__name__} start **********")
                self.logger.debug(f"引数:\nargs={args}, kwargs={kwargs}")

                # 実行する関数を定義
                result = func(*args, **kwargs)

                self.logger.debug(f"chromeのインスタンス化に成功: {func.__name__}")

                # ローカル変数をすべて出力
                self.logger.debug(f"利用した変数一覧:\n{locals()}")

                return result

            except Exception as e:
                self.chromeHandler.chromeHandler(
                    e=e,
                    popupTitle=ErrorMessage.chromeDriverManagerErrorTitle.value,
                    comment=ErrorMessage.chromeDriverManagerError.value,
                    func=self.sysCommand.restartSys,
                )

        return wrapper

    # ----------------------------------------------------------------------------------

    def noneRetryAction(self, maxRetry: int = 2, delay: int = 10):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                self.logger.warning(f"デコレーターが適用された関数: {func.__name__}")
                self.logger.info(f"引数:\nargs={args}, kwargs={kwargs}")
                retryCount = 0
                while retryCount < maxRetry:
                    self.logger.info(
                        f"********** {func.__name__} start {retryCount + 1}回目 **********"
                    )

                    result = func(*args, **kwargs)

                    if result is None:
                        retryCount += 1
                        self.logger.warning(
                            f"結果がNoneだったためリトライ {retryCount}回目"
                        )
                        time.sleep(delay)
                        continue

                    return result

            return wrapper

        return decorator

    # ----------------------------------------------------------------------------------

    def sqliteErrorHandler(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            self.logger.info(f"********** {func.__name__} start **********")
            self.logger.debug(f"引数:\nargs={args}, kwargs={kwargs}")
            try:
                # 実行する関数を定義
                result = func(*args, **kwargs)
                return result

            except Exception as e:
                self.sqliteHandler.Handler(e=e)
                return None

        return wrapper


# ----------------------------------------------------------------------------------
