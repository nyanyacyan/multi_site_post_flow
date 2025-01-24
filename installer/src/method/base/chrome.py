# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# testOK
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import os, shutil
from typing import Dict
from selenium_stealth import stealth
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# 自作モジュール
from .utils import Logger
from .path import BaseToPath
from .decorators import Decorators
from method.const_str import FileName

decoInstance = Decorators()


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************


class ChromeManager:
    def __init__(self):

        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

        # インスタンスをクラス内で保持
        self.chrome = None

        # インスタンス
        self.path = BaseToPath()

        # デフォルト画面サイズ（必要なら外部から設定可能にする）
        self.screen_width = 720  # 画面の幅
        self.screen_height = 600  # 画面の高さ

        # フラグと倍率設定
        self.flags = {
            "A": False,
            "B": False,
            "C": False,
            "D": False,
        }
        self.positions = {
            "A": (0.1, 0.1),  # 画面幅の10%右、画面高さの10%下
            "B": (0.5, 0.1),  # 画面幅の50%右、画面高さの10%下
            "C": (0.7, 0.5),  # 画面幅の70%右、画面高さの50%下
            "D": (0.9, 0.8),  # 画面幅の90%右、画面高さの80%下
        }

    # ----------------------------------------------------------------------------------

    def clear_cache(self):
        # webdriver_manager のデフォルトキャッシュパスを削除
        cache_path = os.path.expanduser("~/.wdm")
        if os.path.exists(cache_path):
            shutil.rmtree(cache_path, ignore_errors=True)
            print(f"キャッシュを削除しました: {cache_path}")
        else:
            print(f"キャッシュディレクトリが見つかりません: {cache_path}")

    # ----------------------------------------------------------------------------------

    @decoInstance.chromeSetup
    def flowSetupChrome(self):
        self.clear_cache()

        # selenium_driver_path = self._get_selenium_driver_path()

        # os.environ["SE_DRIVER_PATH"] = selenium_driver_path
        # self.logger.info(f"SE_DRIVER_PATH set to: {selenium_driver_path}")

        service = Service()
        chrome = webdriver.Chrome(service=service, options=self.setupChromeOption)


        # selenium-stealth を適用してWebDriverを偽装（日本語に設定）
        stealth(
            chrome,
            languages=["ja-JP", "ja"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )

        return chrome

    # ----------------------------------------------------------------------------------


    @decoInstance.chromeSetup
    def flow_setup_chromedriver(self):
        driver_path = self._get_driver_path()

        service = Service(driver_path)
        chrome = webdriver.Chrome(service=service, options=self.setupChromeOption)

        # selenium-stealth を適用してWebDriverを偽装（日本語に設定）
        stealth(
            chrome,
            languages=["ja-JP", "ja"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )

        return chrome

    # ----------------------------------------------------------------------------------

    @property
    def getChromeDriverPath(self):
        return None

    # ----------------------------------------------------------------------------------

    @property
    def getChromeDriverVersion(self):
        return "Selenium Manager is managing the ChromeDriver."

    # ----------------------------------------------------------------------------------
    # Chromeのバージョン管理＋拡張機能

    @property
    def setupChromeOption(self):

        chromeDriverVersion = self.getChromeDriverVersion
        self.logger.warning(f"インストールされた ChromeDriver バージョン: {chromeDriverVersion}")

        chromeOptions = Options()

        # chromeOptions.add_argument("--headless=new")  # ヘッドレスモードで実行
        # chromeOptions.add_argument(f"--window-position=0,0")
        # chromeOptions.add_argument(f"--window-position={self.x},{self.y}")
        chromeOptions.add_argument("--window-size=840,600")  # ウィンドウサイズの指定
        chromeOptions.add_argument("start-maximized")
        chromeOptions.add_argument("--no-sandbox")
        # chromeOptions.add_argument("--disable-dev-shm-usage")
        chromeOptions.add_experimental_option("useAutomationExtension", False)
        chromeOptions.add_argument("--lang=ja-JP")

        # ヘッドレスでの場合に「user-agent」を設定することでエラーを返すものを通すことができる
        # chromeOptions.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.63 Safari/537.36')
        # chromeOptions.add_extension(
        #     self.path.getInputDataFilePath(fileName=FileName.CHROME_OP_IFRAME.value)
        # )  # iframe対策の広告ブロッカー
        chromeOptions.add_extension(
            self.path.getInputDataFilePath(fileName=FileName.CHROME_OP_CAPTCHA.value)
        )  # CAPTCHA
        # chromeOptions.add_argument("--disable-extensions")
        # chromeOptions.add_argument("--disable-popup-blocking")
        # chromeOptions.add_argument("--disable-translate")

        # chromeOptions.add_argument("--disable-blink-features")
        # chromeOptions.add_argument("--remote-debugging-port=9222")

        # ヘッドレス仕様のオプション
        chromeOptions.add_experimental_option("excludeSwitches", ["enable-automation"])
        chromeOptions.add_experimental_option("useAutomationExtension", False)
        chromeOptions.add_experimental_option(
            "prefs",
            {
                "credentials_enable_service": False,
                "profile": {"password_manager_enabled": False},
            },
        )

        chromeOptions.add_argument("--disable-software-rasterizer")
        chromeOptions.add_argument(
            "--enable-features=NetworkService,NetworkServiceInProcess"
        )

        chromeOptions.add_argument(
            "--disable-blink-features=AutomationControlled"
        )  # navigator.webdriver = falseに設定して足跡が残らないように
        chromeOptions.add_argument(
            "--disable-infobars"
        )  # "Chrome is being controlled by automated test software" の情報バーを無効化

        return chromeOptions


    # ----------------------------------------------------------------------------------
    # 空いてるフラグ状況を確認

    def _check_flag_status(self):
        false_status_list = [key for key, value in self.flags.items() if not value]
        self.logger.debug(f'false_status_list: {false_status_list}')
        return false_status_list[0]  # 最初の値を取得

    # ----------------------------------------------------------------------------------
    # フラグをONにする

    def _flag_on(self, flag_name: str):
        self.flags[flag_name] = True
        self.logger.info(f"{flag_name} のフラグを立てました。\npositions: {self.positions[flag_name]}")

        ratio_x, ratio_y = self.positions[flag_name]
        self.x = self.screen_width * ratio_x
        self.y = self.screen_height * ratio_y


    # ----------------------------------------------------------------------------------
    # browserを閉じてフラグをOFFにする

    def close_browser(self, chrome: webdriver, flag_name: str):
        chrome.quit()
        self.flags[flag_name] = False
        self.logger.info(f"{flag_name} のbrowserを閉じました。")

    # ----------------------------------------------------------------------------------
    # ChromePath

    def _get_driver_path(self):
        file_path = self.path._get_input_chromedriver_path()
        self.logger.debug(f'ChromeのDriverPath: {file_path}')
        return file_path

    # ----------------------------------------------------------------------------------

    def _get_selenium_driver_path(self):
        return self.path._get_selenium_chromedriver_path()
