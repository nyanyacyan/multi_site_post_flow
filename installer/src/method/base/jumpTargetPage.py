# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
from selenium.webdriver.chrome.webdriver import WebDriver


# 自作モジュール
from .utils import Logger
from .driverDeco import jsCompleteWaitDeco
from .seleniumBase import SeleniumBasicOperations


decoInstance = jsCompleteWaitDeco()


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************


class JumpTargetPage:
    def __init__(self, chrome: WebDriver):
        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

        self.chrome = chrome
        self.random_sleep = SeleniumBasicOperations(chrome=self.chrome)

    # ----------------------------------------------------------------------------------

    @decoInstance.jsCompleteWaitRetry()
    def flowJumpTargetPage(self, targetUrl: str):
        self.openNewWindow()

        self.changeNewPage()

        self.getTargetPage(targetUrl=targetUrl)

        self.urlCheck()
        return

    # ----------------------------------------------------------------------------------
    # 新しいページを開く

    def openNewWindow(self):
        self.chrome.execute_script("window.open('')")
        self.logger.debug(f"{__name__} 新しいページを開きました")
        self._random_sleep()
        return

    # ----------------------------------------------------------------------------------
    # 新しいページに切り替える
    # self.chrome.window_handles[-1]→一番最後に開かれたページに切替

    def changeNewPage(self):
        self.chrome.switch_to.window(self.chrome.window_handles[-1])
        self.logger.debug(f"{__name__} 新しいページに切替を実行")
        self._random_sleep()
        return

    # ----------------------------------------------------------------------------------

    def getTargetPage(self, targetUrl: str):
        self.chrome.get(targetUrl)

    # ----------------------------------------------------------------------------------

    @property
    def currentUrl(self):
        return self.chrome.current_url()

    # ----------------------------------------------------------------------------------

    def urlCheck(self):
        if self.targetUrl == self.currentUrl:
            self.logger.debug(f"新しいページに移行成功")
        else:
            self.logger.error(f"新しいページに移行できてません。")


# ----------------------------------------------------------------------------------
# ランダムSleep

    def _random_sleep(self, min_num: int = 1, max_num: int = 3):
        self.random_sleep._random_sleep(min_num=min_num, max_num=max_num)


# ----------------------------------------------------------------------------------
