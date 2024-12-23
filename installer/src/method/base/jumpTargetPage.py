# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import time
from selenium.webdriver.chrome.webdriver import WebDriver


# 自作モジュール
from .utils import Logger
from .driverDeco import jsCompleteWaitDeco

from const_str import FileName


decoInstance = jsCompleteWaitDeco(debugMode=True)


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************


class JumpTargetPage:
    def __init__(self, chrome: WebDriver):
        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

        self.chrome = chrome

    # ----------------------------------------------------------------------------------

    @decoInstance.jsCompleteWaitRetry()
    def flowJumpTargetPage(self, targetUrl: str, delay: int = 2):
        self.openNewWindow()
        time.sleep(delay)

        self.changeNewPage()
        time.sleep(delay)

        self.getTargetPage(targetUrl=targetUrl)
        time.sleep(delay)

        self.urlCheck()
        time.sleep(delay)
        return

    # ----------------------------------------------------------------------------------
    # 新しいページを開く

    def openNewWindow(self):
        self.chrome.execute_script("window.open('')")
        self.logger.debug(f"{__name__} 新しいページを開きました")
        return

    # ----------------------------------------------------------------------------------
    # 新しいページに切り替える
    # self.chrome.window_handles[-1]→一番最後に開かれたページに切替

    def changeNewPage(self):
        self.chrome.switch_to.window(self.chrome.window_handles[-1])
        self.logger.debug(f"{__name__} 新しいページに切替を実行")
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
