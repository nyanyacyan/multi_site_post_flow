# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# export PYTHONPATH="/Users/nyanyacyan/Desktop/project_file/domain_search/installer/src"


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import asyncio
from typing import Dict


# 自作モジュール
from base.utils import Logger
from base.chrome import ChromeManager
from base.loginWithId import SingleSiteIDLogin
from base.seleniumBase import SeleniumBasicOperations

# const
from const_str import FileName
from const_element import LoginInfo

# ----------------------------------------------------------------------------------
# **********************************************************************************
# 一連の流れ


class FlowMACNewItem:
    def __init__(self, debugMode=True):

        # logger
        self.getLogger = Logger(
            moduleName=FileName.LOG_FILE_NAME.value, debugMode=debugMode
        )
        self.logger = self.getLogger.getLogger()

        # chrome
        self.chromeManager = ChromeManager(debugMode=debugMode)
        self.chrome = self.chromeManager.flowSetupChrome()

        # インスタンス
        self.login = SingleSiteIDLogin(chrome=self.chrome, debugMode=debugMode)
        self.random_sleep = SeleniumBasicOperations(
            chrome=self.chrome, debugMode=debugMode
        )

    ####################################################################################
    # ----------------------------------------------------------------------------------
    # todo 各メソッドをまとめる

    async def process(self, login_info: Dict):
        # スプシの読み込み（辞書でoutput）

        # IDログイン
        self.login.flowLoginID(login_info=login_info, timeout=120)

        # ランダム待機
        self.random_sleep._random_sleep()

        # 各辞書から必要情報を定義

        # 操作していく
        # 出品ボタンをクリック
        # 画像添付
        # ゲームタイトルクリック
        # POPUPタイトル入力
        # タイトルを選択
        # カテゴリ選択
        # 出品タイトル
        # 商品説明
        # 課金総額
        # 商品価格


# ----------------------------------------------------------------------------------
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# テスト実施

if __name__ == "__main__":
    login_info = LoginInfo.SITE_PATTERNS.value["MA_CLUB"]
    print(f"login_info: {login_info}")
    test_flow = FlowMACNewItem()
    asyncio.run(test_flow.process(login_info))
