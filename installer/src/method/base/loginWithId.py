# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import time
from typing import Dict, List
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.common.exceptions import TimeoutException

# 自作モジュール
from .utils import Logger
from .elementManager import ElementManager
from .driverWait import Wait
from .driverDeco import jsCompleteWaitDeco, InputDeco, ClickDeco
from .SQLite import SQLite

from ..constSqliteTable import TableSchemas

decoInstance = jsCompleteWaitDeco(debugMode=True)
decoInstanceInput = InputDeco(debugMode=True)
decoInstanceClick = ClickDeco(debugMode=True)


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************


class LoginID:
    def __init__(self, chrome: WebDriver, loginUrl: str, homeUrl: str, debugMode=True):
        # logger
        self.getLogger = Logger(__name__, debugMode=debugMode)
        self.logger = self.getLogger.getLogger()

        self.chrome = chrome
        self.loginUrl = loginUrl
        self.homeUrl = homeUrl

        # インスタンス
        self.element = ElementManager(chrome=chrome, debugMode=debugMode)
        self.wait = Wait(chrome=self.chrome, debugMode=debugMode)
        self.sqlite = SQLite(debugMode=debugMode)


# ----------------------------------------------------------------------------------
# IDログイン
# loginInfoはconstから取得
    @decoInstance.jsCompleteWaitRetry()
    def flowLoginID(self, url: str, loginInfo: dict):

        # サイトを開いてCookieを追加
        # self.openSite(url=url)
        # time.sleep(delay)

        self.inputId(by=loginInfo['idBy'], value=loginInfo['idValue'], inputText=loginInfo['idText'])

        self.inputPass(by=loginInfo['passBy'], value=loginInfo['passValue'], inputText=loginInfo['passText'])

        self.clickLoginBtn(by=loginInfo['btnBy'], value=loginInfo['btnValue'])

        # 検索ページなどが出てくる対策
        # PCのスペックに合わせて設定
        self.wait.jsPageChecker(chrome=self.chrome, timeout=10)

        # ログイン後に別のサイトへアクセスしてることを考慮して
        # self.openSite(url=url)

        return self.loginCheck(url)


# ----------------------------------------------------------------------------------


    def flow_cookie_save(self, url: str, loginInfo: dict, tableName: str, columnsName: tuple):
        self.flowLoginID(url=url, loginInfo=loginInfo)

        cookie = self._getCookie()

        self.canValueInCookie(cookie=cookie)

        self.insertCookieData(cookie=cookie, tableName=tableName, columnsName=columnsName)

        table_data_cols = self.sqlite.columnsExists(tableName=tableName)

        self.logger.info(f"cookieをDBへ保存完了")


# ----------------------------------------------------------------------------------


    @decoInstance.jsCompleteWait
    def openSite(self, url: str):
        return self.chrome.get(url=url)


# ----------------------------------------------------------------------------------


    def currentUrl(self):
        try:
            currentUrl = self.chrome.current_url
            self.logger.debug(f"currentUrl: {currentUrl}")
        except Exception as e:
            self.logger.error(f"なにかしらのエラー{e}")
        return currentUrl


# ----------------------------------------------------------------------------------
# IDの取得

    @decoInstanceInput.inputWait
    def inputId(self, by: str, value: str, inputText: str):
        return self.element.clickClearInput(by=by, value=value, inputText=inputText)


# ----------------------------------------------------------------------------------
# passの入力

    @decoInstanceInput.inputWait
    def inputPass(self, by: str, value: str, inputText: str):
        return self.element.clickClearInput(by=by, value=value, inputText=inputText)


# ----------------------------------------------------------------------------------
# ログインボタン押下

    @decoInstanceClick.clickWait
    def clickLoginBtn(self, by: str, value: str):
        return self.element.clickElement(by=by, value=value)


# ----------------------------------------------------------------------------------


    def loginCheck(self, url: str):
        self.logger.debug(f"\nurl: {url}\ncurrentUrl: {self.currentUrl()}")
        if url == self.currentUrl():
            self.logger.info(f"{__name__}: ログインに成功")
            self.wait.jsPageChecker(chrome=self.chrome)
            return True
        else:
            self.logger.error(f"{__name__}: ログインに失敗")
            return False


# ----------------------------------------------------------------------------------


    def actionBeforeLogin(self, url: str, loginInfo: dict, delay: int=2, maxRetries: int = 3):
        # 特定のサイトにアクセス
        self.openSite(url=url)

        retries = 0
        while retries < maxRetries:
            try:
                self.clickLoginBtn(by=loginInfo['bypassIdBy'], value=loginInfo['bypassIdValue'])
                element = self.wait.canWaitInput(by=loginInfo['idBy'], value=loginInfo['idValue'])
                time.sleep(delay)

                if element:
                    # ここから通常のIDログイン
                    self.flowLoginID(url=url, loginInfo=loginInfo, delay=delay)
                    break

            except TimeoutException:
                self.logger.warning(f"要素が見つからなかったため、再試行します。リトライ回数: {retries + 1}/{maxRetries}")
                retries += 1
                # self.clickLoginBtn(by=loginInfo['bypassIdBy'], value=loginInfo['bypassIdValue'])
                time.sleep(delay)  # リトライの間に少し待機して再試行する

        if retries == maxRetries:
            self.logger.error("指定回数のリトライを行いましたが、要素にアクセスできませんでした")


# ----------------------------------------------------------------------------------


    def bypassOpenSite(self):
        return self.chrome.get(self.homeUrl)


# ----------------------------------------------------------------------------------


    def _getCookie(self):
        cookies = self.chrome.get_cookies()
        cookie = cookies[0]
        self.logger.debug(f"\ncookies(元データ→リスト): {cookies}\ncookie（元データリストの1つ目の辞書）: {cookie}")
        return cookie


# ----------------------------------------------------------------------------------
# Cookieの値が入っているか確認

    @decoInstance.funcBase
    def canValueInCookie(self, cookie: Dict):
        if not cookie.get('name') or not cookie.get('value'):
            self.logger.warning(f"cookieに必要な情報が記載されてません {cookie}")
            return None
        else:
            return cookie


# ----------------------------------------------------------------------------------
# 有効期限をクリアしたmethod
# DBよりcookie情報を取得する

    @decoInstance.funcBase
    def insertCookieData(self, cookie: Dict, tableName: str, columnsNames: tuple = TableSchemas.BASE_COOKIES_TABLE_COLUMNS.value):
        cookieName = cookie['name']
        cookieValue = cookie.get('value')
        cookieDomain = cookie.get('domain')
        cookiePath = cookie.get('path')
        cookieExpires = cookie.get('expiry')
        cookieMaxAge = cookie.get('max-age')  # expiresよりも優先される、〇〇秒間、持たせる権限
        cookieCreateTime = int(time.time())

        # 値をtuple化
        values = (cookieName, cookieValue, cookieDomain, cookiePath, cookieExpires, cookieMaxAge, cookieCreateTime)
        self.logger.info(f"values:\n{values}")

        # データを入れ込む
        self.sqlite.insertData(tableName=tableName, cols=columnsNames, values=values)
        return cookie


# ----------------------------------------------------------------------------------