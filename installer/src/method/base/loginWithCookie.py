# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import requests, time
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.common.exceptions import InvalidCookieDomainException
from selenium.common.exceptions import TimeoutException

# 自作モジュール
from .utils import Logger
from .driverWait import Wait
from .seleniumBase import SeleniumBasicOperations
from .cookieManager import CookieManager
from .loginWithId import SingleSiteIDLogin
from .driverDeco import jsCompleteWaitDeco
from .elementManager import ElementManager

from const_str import FileName


decoInstance = jsCompleteWaitDeco()


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************


class CookieLogin:
    def __init__(
        self,
        chrome: WebDriver,
        loginUrl: str,
        homeUrl: str,
        targetUrl: str,
        signInUrl: str,
        ,
    ):
        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

        self.chrome = chrome
        self.loginUrl = loginUrl
        self.homeUrl = homeUrl
        self.signInUrl = signInUrl
        self.targetUrl = targetUrl

        # インスタンス
        self.browser = SeleniumBasicOperations(
            chrome=self.chrome, homeUrl=self.homeUrl,
        )
        self.driverWait = Wait(chrome=self.chrome, )
        self.cookieManager = CookieManager(
            chrome=self.chrome,
            loginUrl=self.loginUrl,
            homeUrl=self.homeUrl,
            ,
        )
        self.idLogin = SingleSiteIDLogin(
            chrome=self.chrome,
            homeUrl=self.homeUrl,
            loginUrl=self.loginUrl,
            ,
        )
        self.element = ElementManager(chrome=self.chrome, )

    # ----------------------------------------------------------------------------------
    # 2段階ログイン

    def flowSwitchLogin(self, cookies: dict, url: str, loginInfo: dict, delay: int = 2):
        if self.chrome.current_url == self.targetUrl:
            return

        if cookies is None:
            self.idLogin.flowLoginID(url=url, loginInfo=loginInfo)
            return

        if self.cookieLogin(cookies=cookies, url=url, loginInfo=loginInfo):
            time.sleep(delay)  # 広告などが遅れて表示されることを懸念
            # 検索画面、広告が合った場合に消去
            self.element.closePopup(
                by=loginInfo["modalBy"], value=loginInfo["modalValue"]
            )
            self.logger.info(f"Cookieログインに成功")
        else:
            self.logger.error(
                "Cookieログインに失敗したためセッションログインに切り替えます"
            )
            result = self.sessionBeforeAction(
                cookies=cookies, url=url, loginInfo=loginInfo
            )

            if result is None:
                self.logger.warning(
                    f"Sessionログインに゙失敗したためIDログインを実施: {result}"
                )
                self.idLogin.flowLoginID(url=url, loginInfo=loginInfo)

    # ----------------------------------------------------------------------------------
    # sessionログイン

    def sessionLogin(self, cookies: dict, url: str):
        session = self.sessionSetting(cookies=cookies)
        session.get(self.homeUrl)
        return self.loginCheck(url=url)

    # ----------------------------------------------------------------------------------

    def sessionBeforeAction(
        self,
        cookies: dict,
        url: str,
        loginInfo: dict,
        delay: int = 2,
        maxRetries: int = 3,
    ):

        retries = 0
        while retries < maxRetries:
            try:
                self.element.clickElement(
                    by=loginInfo["bypassIdBy"], value=loginInfo["bypassIdValue"]
                )
                time.sleep(delay)

                # ここから通常のIDログイン
                if self.sessionLogin(cookies=cookies, url=url):
                    self.logger.info(f"Cookieログインに成功")
                    return None
                else:
                    self.logger.error(f"セッションログインにも失敗: {cookies}")
                    return None

            except TimeoutException:
                self.logger.warning(
                    f"要素が見つからなかったため、再試行します。リトライ回数: {retries + 1}/{maxRetries}"
                )
                retries += 1
                time.sleep(delay)  # リトライの間に少し待機して再試行する

        if retries == maxRetries:
            self.logger.error(
                "指定回数のリトライを行いましたが、要素にアクセスできませんでした"
            )

    # ----------------------------------------------------------------------------------
    # Cookieログイン

    def cookieLogin(self, cookies: dict, url: str, loginInfo: dict):

        self.logger.info(f"cookies: {cookies}")

        # サイトを開いてCookieを追加
        self.openSite()

        if self.element.getElement(
            by=loginInfo["bypassIdBy"], value=loginInfo["bypassIdValue"]
        ):
            self.element.clickElement(
                by=loginInfo["bypassIdBy"], value=loginInfo["bypassIdValue"]
            )

        try:
            self.addCookie(cookie=cookies)
            # サイトをリロードしてCookieの適用を試行
            self.openSite()

        except InvalidCookieDomainException as e:
            self.logger.error(
                f"ドメインが変わるサイトのためIDログインに切り替えます。{e}"
            )
            self.idLogin.flowLoginID(url=url, loginInfo=loginInfo)

        return self.loginCheck(url=url)

    # ----------------------------------------------------------------------------------

    def addCookie(self, cookie: dict):
        # クッキー情報をデバッグ
        self.logger.debug(f"Adding cookie: {cookie}")
        # 必須フィールドが揃っているか確認
        required_keys = ["name", "value"]
        for key in required_keys:
            if key not in cookie:
                self.logger.error(f"Cookie情報が入っていません: '{key}'")
                raise ValueError(f"Cookie情報が入っていません: '{key}'")

        # クッキーを追加
        return self.chrome.add_cookie(cookie_dict=cookie)

    # ----------------------------------------------------------------------------------

    @decoInstance.jsCompleteWait
    def openSite(self):
        return self.browser.openSite()

    # ----------------------------------------------------------------------------------

    @property
    def session(self):
        # sessionを定義（セッションの箱を作ってるイメージ）
        return requests.Session()

    # ----------------------------------------------------------------------------------

    @decoInstance.jsCompleteWait
    def sessionSetting(self, cookies):
        self.logger.warning(f"cookies: {cookies}")
        if cookies:
            session = self.session
            session.cookies.set(
                name=cookies["name"],
                value=cookies["value"],
                domain=cookies["domain"],
                path=cookies["path"],
            )
            self.logger.debug(
                f"Cookieの中身:\nname={cookies['name']}\nvalue={cookies['value']}\ndomain={cookies['domain']}, path={cookies['path']}"
            )
            return session
        else:
            self.logger.error(f"cookiesがありません")
            return None

    # ----------------------------------------------------------------------------------

    def loginCheck(self, url: str):
        if url == self.chrome.current_url:
            self.logger.info(f"{__name__}: ログインに成功")
            return True
        else:
            self.logger.error(f"{__name__}: ログインに失敗")
            return False


# ----------------------------------------------------------------------------------
