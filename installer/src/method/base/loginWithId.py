# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import time
from typing import Dict
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.common.exceptions import TimeoutException, UnexpectedAlertPresentException, NoAlertPresentException

# 自作モジュール
from .utils import Logger
from .path import BaseToPath
from .fileWrite import LimitSabDirFileWrite
from .fileRead import ResultFileRead
from .elementManager import ElementManager
from .driverWait import Wait
from .decorators import Decorators
from .driverDeco import jsCompleteWaitDeco, InputDeco, ClickDeco
from method.base.jumpTargetPage import JumpTargetPage
from method.base.seleniumBase import SeleniumBasicOperations

# const
from method.const_element import LoginInfo

decoInstance = Decorators()
decoJsInstance = jsCompleteWaitDeco()
decoInstanceInput = InputDeco()
decoInstanceClick = ClickDeco()


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************


class SingleSiteIDLogin:
    def __init__(self, chrome: WebDriver):
        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

        self.chrome = chrome

        # インスタンス
        self.element = ElementManager(chrome=chrome)
        self.wait = Wait(chrome=self.chrome)
        self.path = BaseToPath()
        self.pickle_write = LimitSabDirFileWrite()
        self.pickle_read = ResultFileRead()
        self.jump = JumpTargetPage(chrome=self.chrome)
        self.random_sleep = SeleniumBasicOperations(chrome=self.chrome)

    # ----------------------------------------------------------------------------------
    # IDログイン
    # reCAPTCHA OK

    def flowLoginID(self, login_info: dict, timeout: int = 120):
        self.logger.debug(f"login_info: {login_info}")

        # サイトを開いてCookieを追加
        self.openSite(login_url=login_info["LOGIN_URL"])

        self.inputId(
            by=login_info["ID_BY"],
            value=login_info["ID_VALUE"],
            inputText=login_info["ID_TEXT"],
        )

        self.inputPass(
            by=login_info["PASS_BY"],
            value=login_info["PASS_VALUE"],
            inputText=login_info["PASS_TEXT"],
        )

        # クリックを繰り返しPOPUPがなくなるまで繰り返す
        self.click_login_btn_in_recaptcha(
            by=login_info["BTN_BY"], value=login_info["BTN_VALUE"]
        )

        # 検索ページなどが出てくる対策
        # PCのスペックに合わせて設定
        self.wait.jsPageChecker(chrome=self.chrome, timeout=10)

        # reCAPTCHA対策を完了確認
        return self.login_element_check(
            by=login_info["LOGIN_AFTER_ELEMENT_BY"],
            value=login_info["LOGIN_AFTER_ELEMENT_VALUE"],
            timeout=timeout,
        )

    # ----------------------------------------------------------------------------------
    # IDログイン
    # reCAPTCHA OK

    def flow_login_id_input_gui( self, login_info: dict, id_text: str, pass_text: str, timeout: int = 10):
        try:
            self.logger.debug(f"login_info: {login_info}")

            # サイトを開いてCookieを追加
            self.openSite(login_url=login_info["LOGIN_URL"])

            self.inputId( by=login_info["ID_BY"], value=login_info["ID_VALUE"], inputText=id_text, )

            self.inputPass( by=login_info["PASS_BY"], value=login_info["PASS_VALUE"], inputText=pass_text, )

            # クリックを繰り返しPOPUPがなくなるまで繰り返す
            self.click_login_btn_in_recaptcha( by=login_info["BTN_BY"], value=login_info["BTN_VALUE"], home_url=login_info["HOME_URL"], check_element_by=login_info["LOGIN_AFTER_ELEMENT_BY"], check_element_value=login_info["LOGIN_AFTER_ELEMENT_VALUE"], )

            self.wait.jsPageChecker(chrome=self.chrome, timeout=10)

            # reCAPTCHA対策を完了確認
            self.login_element_check( by=login_info["LOGIN_AFTER_ELEMENT_BY"], value=login_info["LOGIN_AFTER_ELEMENT_VALUE"], timeout=timeout, )
            return

        except TimeoutError:
            self.logger.critical(f'{self.__class__.__name__} reCAPTCHAの処理時間に {timeout} 秒以上 かかってしまいましたためtimeout')
            self.chrome.quit()
            time.sleep(5)  # 少し待って次へ

    # ----------------------------------------------------------------------------------
    # IDログイン reCAPTCHA での例外処理込

    def _flow_recapcha_handle_id_login( self, login_info: dict, id_text: str, pass_text: str, timeout: int = 120 ):
        try:
            self._flow_id_login( login_info=login_info, id_text=id_text, pass_text=pass_text )

            # reCAPTCHA対策を完了確認
            success = self.login_element_check( by=login_info["LOGIN_AFTER_ELEMENT_BY"], value=login_info["LOGIN_AFTER_ELEMENT_VALUE"], timeout=timeout, )
            self.logger.debug(f"ログインができてるかどうかを確認: {success}")
            return success

        # reCAPTCHAを実施する前にクリックがあった場合の例外処理
        except UnexpectedAlertPresentException as e:
            return self._handle_recaptcha_alert( login_info=login_info, id_text=id_text, pass_text=pass_text, timeout=timeout, e=e, )

    # ----------------------------------------------------------------------------------
    # reCAPTCHAを実施する前にクリックがあった場合の例外処理

    def _handle_recaptcha_alert( self, login_info: dict, id_text: str, pass_text: str, e: UnexpectedAlertPresentException, timeout: int = 120, ):
        try:
            self.logger.warning(
                f"{self.__class__.__name__} reCAPTCHAのアラートが検出されました。: {str(e)}"
            )

            error_message = str(e)  # エラーメッセージを取得
            self.logger.debug(f"error_message: {error_message}")

            if "私はロボットではありません" in error_message:

                self.random_sleep._random_sleep()

                max_count = 3
                count = 1
                while count < max_count:
                    self.logger.info(f"【 {count} 回目】reCAPTCHAの処理NGのため再実行")

                    # 新しいページにジャンプして開く
                    self.jump.flowJumpTargetPage(targetUrl=login_info["LOGIN_URL"])

                    # IDログインフロー
                    self._flow_id_login( login_info=login_info, id_text=id_text, pass_text=pass_text )

                    # ログインできてるか確認
                    success = self.login_element_check( by=login_info["LOGIN_AFTER_ELEMENT_BY"], value=login_info["LOGIN_AFTER_ELEMENT_VALUE"], timeout=timeout, )
                    self.logger.debug(f"ログイン整合: {success}")

                    if success == True:
                        return True

                    count += 1

                # 3回試行しても成功しなかった場合
                self.logger.warning(
                    f"{self.__class__.__name__} ({max_count}回) に達したため終了"
                )
                return False


        except Exception as err:
            self.logger.error(
                f"{self.__class__.__name__} アラート処理中に例外発生: {err}"
            )
            return False

    # ----------------------------------------------------------------------------------

    def _flow_id_login(self, login_info: dict, id_text: str, pass_text: str):
        # サイトを開いてCookieを追加
        self.openSite(login_url=login_info["LOGIN_URL"])

        self.inputId(
            by=login_info["ID_BY"],
            value=login_info["ID_VALUE"],
            inputText=id_text,
        )

        self.random_sleep._random_sleep()

        self.inputPass(
            by=login_info["PASS_BY"],
            value=login_info["PASS_VALUE"],
            inputText=pass_text,
        )

        # クリックを繰り返しPOPUPがなくなるまで繰り返す
        self.click_login_btn_in_recaptcha(
            by=login_info["BTN_BY"],
            value=login_info["BTN_VALUE"],
            home_url=login_info["HOME_URL"],
            check_element_by=login_info["LOGIN_AFTER_ELEMENT_BY"],
            check_element_value=login_info["LOGIN_AFTER_ELEMENT_VALUE"],
        )

        # 検索ページなどが出てくる対策
        # PCのスペックに合わせて設定
        self.wait.jsPageChecker(chrome=self.chrome, timeout=10)

    # ----------------------------------------------------------------------------------

    @decoJsInstance.jsCompleteWait
    def openSite(self, login_url: str):
        return self.chrome.get(url=login_url)

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

    def clickLoginBtn(self, by: str, value: str):
        self.logger.debug(f"value: {value}")
        return self.element.clickElement(by=by, value=value)

    # ----------------------------------------------------------------------------------
    # ログインボタン押下
    # reCAPTCHA

    def click_login_btn_in_recaptcha( self, by: str, value: str, home_url: str, check_element_by: str, check_element_value: str, ):
        self.logger.debug(f"value: {value}")

        return self.element.recaptcha_click_element( by=by, value=value, home_url=home_url, check_element_by=check_element_by, check_element_value=check_element_value, )

    # ----------------------------------------------------------------------------------

    def loginUrlCheck(self, url: str):
        self.logger.debug(f"\nurl: {url}\ncurrentUrl: {self.currentUrl()}")
        if url == self.currentUrl():
            self.logger.info(f"{__name__}: ログインに成功")
            self.wait.loadPageWait(chrome=self.chrome, timeout=10)
            return True
        else:
            self.logger.error(f"{__name__}: ログインに失敗")
            return False

    # ----------------------------------------------------------------------------------

    def login_element_check(self, by: str, value: str, timeout: int):
        try:
            self.wait.loadPageWait(by=by, value=value, timeout=timeout)
            self.logger.info(f"{__name__}: ログインに成功")
            return True

        except TimeoutException:
            self.logger.error(
                f"{__name__}: reCAPTCHAの処理時間に {timeout} 秒以上 かかってしまいましたためtimeout"
            )
            raise

    # ----------------------------------------------------------------------------------

    def actionBeforeLogin(
        self, url: str, login_info: dict, delay: int = 2, maxRetries: int = 3
    ):
        # 特定のサイトにアクセス
        self.openSite(url=url)

        retries = 0
        while retries < maxRetries:
            try:
                self.clickLoginBtn(
                    by=login_info["bypassIdBy"], value=login_info["bypassIdValue"]
                )
                element = self.wait.canWaitInput(
                    by=login_info["idBy"], value=login_info["idValue"]
                )
                time.sleep(delay)

                if element:
                    # ここから通常のIDログイン
                    self.flowLoginID(url=url, login_info=login_info, delay=delay)
                    break

            except TimeoutException:
                self.logger.warning(
                    f"要素が見つからなかったため、再試行します。リトライ回数: {retries + 1}/{maxRetries}"
                )
                retries += 1
                # self.clickLoginBtn(by=login_info['bypassIdBy'], value=login_info['bypassIdValue'])
                time.sleep(delay)  # リトライの間に少し待機して再試行する

        if retries == maxRetries:
            self.logger.error(
                "指定回数のリトライを行いましたが、要素にアクセスできませんでした"
            )

    # ----------------------------------------------------------------------------------

    def bypassOpenSite(self):
        return self.chrome.get(self.homeUrl)

    # ----------------------------------------------------------------------------------

    def _getCookie(self):
        cookies = self.chrome.get_cookies()
        # cookie = cookies[0]
        self.logger.debug(f"\ncookies(元データ→リスト): {cookies}")
        # checked_cookie = self.canValueInCookie(cookie=cookie)
        return cookies

    # ----------------------------------------------------------------------------------
    # Cookieの値が入っているか確認
    # TODO 使わない

    def canValueInCookie(self, cookie: Dict):
        if not cookie.get("name") or not cookie.get("value"):
            self.logger.warning(f"cookieに必要な情報が記載されてません {cookie}")
            return None
        else:
            return cookie

    # ----------------------------------------------------------------------------------

    async def flow_cookie_pickle_save(
        self, login_url: str, login_info: dict, timeout: int = 180
    ):
        # ログインの実施
        self.flowLoginID(login_url=login_url, login_info=login_info, timeout=timeout)

        # Cookieの取得
        cookies = self._getCookie()

        self.pickle_write.writeSabDirToPickle(data=cookies)


# **********************************************************************************


class MultiSiteIDLogin(SingleSiteIDLogin):
    def __init__(self, chrome):
        super().__init__(chrome)

    # ----------------------------------------------------------------------------------

    def _set_pattern(self, site_name: str):
        login_pattern_dict = LoginInfo.SITE_PATTERNS.value
        login_info = login_pattern_dict[site_name]
        self.logger.info(f"login_info: {login_info}")

        return login_info

    # ----------------------------------------------------------------------------------

    def flow_cookie_save_cap(
        self,
        login_url,
        login_info,
        cap_after_element_by,
        cap_after_element_path,
        tableName,
        columnsName,
        cap_timeout=180,
    ):
        return super().flow_cookie_save_cap(
            login_url,
            login_info,
            cap_after_element_by,
            cap_after_element_path,
            tableName,
            columnsName,
            cap_timeout,
        )


# ----------------------------------------------------------------------------------
