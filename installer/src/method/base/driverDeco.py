# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import time
from functools import wraps
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement


# 自作モジュール
from .utils import Logger


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************


class jsCompleteWaitDeco:
    def __init__(self):

        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

    # ----------------------------------------------------------------------------------
    # func > jsCompleteWait > refresh > retry

    def jsCompleteWaitRetry(self, maxRetry: int = 2, delay: int = 2, timeout: int = 10):
        def decorator(func):
            @wraps(func)
            def wrapper(instance, *args, **kwargs):
                self.logger.info(f"引数:\nargs={args}, kwargs={kwargs}")
                retryCount = 0
                while retryCount < maxRetry:
                    try:
                        self.logger.info(
                            f"********** {func.__name__} start {retryCount + 1}回目 **********"
                        )

                        chrome = instance.chrome
                        self.logger.warning(f"chrome: {type(chrome)}")

                        result = func(instance, *args, **kwargs)

                        self.jsPageChecker(chrome=chrome, timeout=timeout)

                        return result

                    except TimeoutException as e:
                        retryCount += 1
                        if retryCount < maxRetry:
                            self.logger.error(
                                f"{func.__name__}: {timeout}秒以上経過したためタイムアウト\nページを更新してリトライ実施: {retryCount} 回目"
                            )
                            time.sleep(delay)
                            chrome.refresh()
                            continue

                        else:
                            self.logger.error(f"{func.__name__}: リトライ上限まで実施")

                    except Exception as e:
                        self.logger.error(
                            f"{func.__name__} ページが更新されるまでの待機中になんらかのエラーが発生: {e}"
                        )
                        break

            return wrapper

        return decorator

    # ----------------------------------------------------------------------------------

    def jsCompleteWait(self, func):
        @wraps(func)
        def wrapper(instance, *args, **kwargs):
            self.logger.info(f"********** {func.__name__} start **********")
            self.logger.debug(f"引数:\nargs={args}, kwargs={kwargs}")
            try:
                chrome = instance.chrome

                result = func(instance, *args, **kwargs)

                self.jsPageChecker(chrome=chrome)

                return result

            except TimeoutException as e:
                self.logger.error(f"{func.__name__} TimeoutException発生: {e}")
                raise e

            # ローカル変数をすべて出力
            # self.logger.debug(f"利用した変数一覧:\n{locals()}")

        return wrapper

    # ----------------------------------------------------------------------------------
    # 次のページに移動後にページがちゃんと開いてる状態か全体を確認してチェックする

    def jsPageChecker(self, chrome: WebDriver, timeout: int = 10):
        if WebDriverWait(chrome, timeout).until(
            lambda driver: driver.execute_script("return document.readyState")
            == "complete"
        ):
            self.logger.debug(f"{__name__} ページが更新OK")


# ----------------------------------------------------------------------------------
# **********************************************************************************


class InputDeco:
    def __init__(self):

        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

    # ----------------------------------------------------------------------------------
    # WaitClick > func > checkInput

    def inputWait(self, func, delay: int = 2):
        @wraps(func)
        def wrapper(instance, *args, **kwargs):
            self.logger.info(f"********** {func.__name__} start **********")
            self.logger.debug(f"引数:\nargs={args}, kwargs={kwargs}")
            try:
                chrome = instance.chrome

                by = kwargs["by"]
                value = kwargs["value"]
                inputText = kwargs["inputText"]

                element = self.canWaitClick(chrome=chrome, by=by, value=value)
                self.logger.info(f"{__name__} Clickできる状態になってます")

                result = func(instance, *args, **kwargs)
                time.sleep(delay)

                self.checkInput(element=element, inputText=inputText)

                return result

            except TimeoutException as e:
                self.logger.error(f"{func.__name__} TimeoutException発生: {e}")
                raise e

            # ローカル変数をすべて出力
            # self.logger.debug(f"利用した変数一覧:\n{locals()}")

        return wrapper

    # ----------------------------------------------------------------------------------
    # クリックができるまで待機

    def canWaitClick(self, chrome: WebDriver, by: str, value: str, timeout: int = 10):
        return WebDriverWait(chrome, timeout).until(
            EC.element_to_be_clickable((by, value))
        )

    # ----------------------------------------------------------------------------------

    def checkInput(self, element: WebElement, inputText: str):
        enteredText = element.get_attribute("value")
        if enteredText == inputText:
            self.logger.info(f"入力に成功: {inputText}")
        else:
            self.logger.error(
                f"入力エラー: {inputText} → {enteredText} と表示されてしまってる"
            )
            # raise ValueError


# ----------------------------------------------------------------------------------
# **********************************************************************************


class ClickDeco:
    def __init__(self):

        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

    # ----------------------------------------------------------------------------------
    # WaitClick > func > jsPageChecker

    def clickWait(self, func, delay: int = 2):
        @wraps(func)
        def wrapper(instance, *args, **kwargs):
            self.logger.info(f"********** {func.__name__} start **********")
            self.logger.debug(f"引数:\nargs={args}, kwargs={kwargs}")
            try:
                chrome = instance.chrome

                by = kwargs["by"]
                value = kwargs["value"]

                self.canWaitClick(chrome=chrome, by=by, value=value)

                time.sleep(delay)

                result = func(instance, *args, **kwargs)

                self.jsPageChecker(chrome=chrome)

                return result

            except TimeoutException as e:
                self.logger.error(f"{func.__name__} TimeoutException発生: {e}")
                raise e

            # ローカル変数をすべて出力
            # self.logger.debug(f"利用した変数一覧:\n{locals()}")

        return wrapper

    # ----------------------------------------------------------------------------------
    # クリックができるまで待機

    def canWaitClick(
        self, chrome: WebDriver, value: str, by: str = "xpath", timeout: int = 10
    ):
        self.logger.debug(f'by: {by}')
        self.logger.debug(f'value: {value}')
        if WebDriverWait(chrome, timeout).until(
            EC.element_to_be_clickable((by, value))
        ):
            self.logger.info(f"{__name__} Clickできる状態になってます")

    # ----------------------------------------------------------------------------------
    # 次のページに移動後にページがちゃんと開いてる状態か全体を確認してチェックする

    def jsPageChecker(self, chrome: WebDriver, timeout: int = 10):
        if WebDriverWait(chrome, timeout).until(
            lambda driver: driver.execute_script("return document.readyState")
            == "complete"
        ):
            self.logger.debug(f"{__name__} ページが更新OK")


# ----------------------------------------------------------------------------------
