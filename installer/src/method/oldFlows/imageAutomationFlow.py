# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# 2024/9/23 更新

# sudo tree /Users/nyanyacyan/Desktop/Project_file/SNS_auto_upper -I 'venv|pyvenv.cfg|__pycache__'
# Mac mini PYTHONPATH=/Users/nyanyacyan/Desktop/Project_file/ImageAutomation/installer/src
# MacBook export PYTHONPATH="/Users/nyanyacyan/Desktop/Project_file/ImageAutomation/installer/src"


# 辞書データデバッグ
# import json
# json.dumps(data, indent=4, ensure_ascii=False)

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import os, asyncio
from dotenv import load_dotenv

# 自作モジュール
from base.utils import Logger
from base.chrome import ChromeManager
from base.cookieManager import CookieManager
from base.loginWithCookie import CookieLogin
from base.insertSql import InsertSql
from base.dataFormatterToSql import DataFormatterToSql
from const import SiteUrl
from constElementInfo import LoginElement

load_dotenv()

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

# **********************************************************************************
# 一連の流れ


class Flow:
    def __init__(self, debugMode=True):

        # logger
        self.getLogger = Logger(
            moduleName=FileName.LOG_FILE_NAME.value, debugMode=debugMode
        )
        self.logger = self.getLogger.getLogger()

        # chrome
        self.chromeManager = ChromeManager(debugMode=debugMode)
        self.chrome = self.chromeManager.flowSetupChrome()

        self.loginUrl = SiteUrl.LoginUrl.value
        self.homeUrl = SiteUrl.HomeUrl.value
        self.targetUrl = SiteUrl.TargetUrl.value
        self.signInUrl = SiteUrl.SIGN_IN_URL.value

        # インスタンス
        self.cookieManager = CookieManager(
            chrome=self.chrome,
            loginUrl=self.loginUrl,
            homeUrl=self.homeUrl,
            debugMode=debugMode,
        )
        self.cookieLogin = CookieLogin(
            chrome=self.chrome,
            loginUrl=self.loginUrl,
            homeUrl=self.homeUrl,
            signInUrl=self.signInUrl,
            debugMode=debugMode,
        )
        self.insertSql = InsertSql(chrome=self.chrome, debugMode=debugMode)
        self.createImage = DataFormatterToSql(chrome=self.chrome, debugMode=debugMode)

    # ----------------------------------------------------------------------------------

    async def flow(self):
        # ログイン情報を呼び出し
        loginInfo = LoginElement.LOGIN_INFO.value
        loginInfo["idText"] = os.getenv("ID")
        loginInfo["passText"] = os.getenv("PASS")

        # DBチェッカーから
        cookies = self.cookieManager.startBoolFilePath(
            url=self.homeUrl, loginInfo=loginInfo
        )

        # cookiesの出力によってログイン方法を分ける
        self.cookieLogin.flowSwitchLogin(
            cookies=cookies, url=self.homeUrl, loginInfo=loginInfo
        )

        # text, imageを取得してSQLiteに入れ込む→入れ込んだIDのリストを返す
        listPageInfoDict = self.insertSql.getListPageInfo()
        allData = await self.insertSql.getDetailPageInfo(
            listPageInfoDict=listPageInfoDict
        )

        self.createImage.flowAllDataCreate(allDataDict=allData)


# TODO batFileの作成→実行、install

# TODO 手順書の作成


# ----------------------------------------------------------------------------------


if __name__ == "__main__":
    process = Flow(debugMode=True)
    asyncio.run(process.flow())
