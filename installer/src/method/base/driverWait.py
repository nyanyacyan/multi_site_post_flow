# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# 自作モジュール
from .utils import Logger



# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************


class Wait:
    def __init__(self, chrome, debugMode=True):
        self.chrome = chrome

        # logger
        self.getLogger = Logger(__name__, debugMode=debugMode)
        self.logger = self.getLogger.getLogger()


# ----------------------------------------------------------------------------------
# クリックができるまで待機

    def canWaitClick(self, by: str, value: str, timeout: int = 10):
        if WebDriverWait(self.chrome, timeout).until(EC.element_to_be_clickable(by, value)):
            self.logger.info(f"insert（input）が可能になってます")
        return


# ----------------------------------------------------------------------------------
# 入力ができるまで待機

    def canWaitInput(self, by: str, value: str, timeout: int = 10):
        element = WebDriverWait(self.chrome, timeout).until(EC.visibility_of_element_located((by, value)))
        self.logger.info(f"insert（input）が可能になってます")
        return element


# ----------------------------------------------------------------------------------
# ページが完全に開くまで待機

    def loadPageWait(self, by: str, value: str, timeout: int = 10):
        if WebDriverWait(self.chrome, timeout).until(EC.visibility_of_element_located((by, value))):
            self.logger.info(f"指定の要素が見つかりました")
        return


# ----------------------------------------------------------------------------------
# DOM上に存在するまで待機

    def canWaitDom(self, by: str, value: str, timeout: int = 10):
        if WebDriverWait(self.chrome, timeout).until(EC.presence_of_element_located((self._locator_select(by), value))):
            self.logger.info(f"指定の要素のDOMを確認できました")
        return


# ----------------------------------------------------------------------------------
# 指定のURLに切り替わるまで待機

    def changeUrlWait(self, by: str, Url: str, timeout: int = 10):
        if WebDriverWait(self.chrome, timeout).until(EC.url_changes(Url)):
            self.logger.info(f"指定のURLに切り替わりました")
        return


# ----------------------------------------------------------------------------------
# 次のページに移動後にページがちゃんと開いてる状態か全体を確認してチェックする

    def jsPageChecker(self, chrome: WebDriver, timeout: int = 10):
            if WebDriverWait(chrome, timeout).until(lambda driver: driver.execute_script('return document.readyState')=='complete'):
                self.logger.debug(f"{__name__} ページが更新OK")


# ----------------------------------------------------------------------------------

# **********************************************************************************
