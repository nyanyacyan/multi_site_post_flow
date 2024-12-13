# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# testOK
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import subprocess, shutil
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager  # pip install webdriver-manager

# 自作モジュール
from .utils import Logger
from .path import BaseToPath
from .decorators import Decorators
from const_str import FileName

decoInstance = Decorators(debugMode=True)


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************


class ChromeManager:
    def __init__(self, debugMode=True):

        # logger
        self.getLogger = Logger(__name__, debugMode=debugMode)
        self.logger = self.getLogger.getLogger()

        # インスタンスをクラス内で保持
        self.chrome = None

        # インスタンス
        self.path = BaseToPath(debugMode=debugMode)


# ----------------------------------------------------------------------------------


    @decoInstance.chromeSetup
    def flowSetupChrome(self):
        service = Service(self.getChromeDriverPath)
        chrome = webdriver.Chrome(service=service, options=self.setupChromeOption)
        return chrome


# ----------------------------------------------------------------------------------


    @property
    def getChromeDriverPath(self):
        # ChromeDriverManagerでインストールされたChromeDriverのパスを取得
        # shutil.rmtree(ChromeDriverManager().cache_path, ignore_errors=True)
        return ChromeDriverManager().install()


# ----------------------------------------------------------------------------------


    @property
    def getChromeDriverVersion(self):
        # ChromeDriverのバージョンはsubprocessを使って取得が必要
        ChromeDriverPath = self.getChromeDriverPath
        result = subprocess.run([ChromeDriverPath, '--version'], stdout=subprocess.PIPE)
        version = result.stdout.decode('utf-8').strip()
        return version


# ----------------------------------------------------------------------------------
# Chromeのバージョン管理＋拡張機能

    @property
    def setupChromeOption(self):

        chromeDriverVersion = self.getChromeDriverVersion
        self.logger.warning(f"インストールされた ChromeDriver バージョン: {chromeDriverVersion}")

        chromeOptions = Options()
        # chromeOptions.add_argument("--headless=new")  # ヘッドレスモードで実行
        chromeOptions.add_argument(f"--window-position=0,0")
        # chromeOptions.add_argument("--window-size=1440,900")  # ウィンドウサイズの指定
        chromeOptions.add_argument("start-maximized")
        chromeOptions.add_argument("--no-sandbox")
        # chromeOptions.add_argument("--disable-dev-shm-usage")
        chromeOptions.add_experimental_option('useAutomationExtension', False)
        chromeOptions.add_argument('--lang=ja-JP')

        # ヘッドレスでの場合に「user-agent」を設定することでエラーを返すものを通すことができる
        # chromeOptions.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.63 Safari/537.36')
        chromeOptions.add_extension(self.path.getInputDataFilePath(fileName=FileName.CHROME_OP_IFRAME.value))  # iframe対策の広告ブロッカー
        chromeOptions.add_extension(self.path.getInputDataFilePath(fileName=FileName.CHROME_OP_CAPTCHA.value))  # CAPTCHA

        # chromeOptions.add_argument("--disable-extensions")
        # chromeOptions.add_argument("--disable-popup-blocking")
        # chromeOptions.add_argument("--disable-translate")

        # chromeOptions.add_argument("--disable-blink-features")
        # chromeOptions.add_argument("--remote-debugging-port=9222")

        # ヘッドレス仕様のオプション
        chromeOptions.add_experimental_option("excludeSwitches", ["enable-automation"])
        chromeOptions.add_experimental_option('useAutomationExtension', False)
        chromeOptions.add_experimental_option('prefs', {
            'credentials_enable_service': False,
            'profile': {
                'password_manager_enabled': False
            }
        })

        chromeOptions.add_argument("--disable-software-rasterizer")
        chromeOptions.add_argument("--enable-features=NetworkService,NetworkServiceInProcess")

        chromeOptions.add_argument("--disable-blink-features=AutomationControlled")  # ブラウザが自動化されていることを示す機能を無効化
        chromeOptions.add_argument("--disable-infobars")  #"Chrome is being controlled by automated test software" の情報バーを無効化

        return chromeOptions


# ----------------------------------------------------------------------------------
