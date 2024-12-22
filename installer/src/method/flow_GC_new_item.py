# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# export PYTHONPATH="/Users/nyanyacyan/Desktop/project_file/domain_search/installer/src"


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import os, time, asyncio
from typing import Dict, List
import pandas as pd


# 自作モジュール
from base.utils import Logger
from base.chrome import ChromeManager
from base.loginWithId import SingleSiteIDLogin
from base.seleniumBase import SeleniumBasicOperations
from base.spreadsheetRead import GetDataGSSAPI

# const
from const_str import SiteName, GameClubInfo
from const_element import LoginInfo, GssInfo

# ----------------------------------------------------------------------------------
# **********************************************************************************
# 一連の流れ

class FlowGCNewItem:
    def __init__(self, debugMode=True):

        # logger
        self.getLogger = Logger(__name__, debugMode=debugMode)
        self.logger = self.getLogger.getLogger()

        # chrome
        self.chromeManager = ChromeManager(debugMode=debugMode)
        self.chrome = self.chromeManager.flowSetupChrome()


        # インスタンス
        self.login = SingleSiteIDLogin(chrome=self.chrome, debugMode=debugMode)
        self.random_sleep = SeleniumBasicOperations(chrome=self.chrome, debugMode=debugMode)
        self.gss_read = GetDataGSSAPI(debugMode=debugMode)



####################################################################################
# ----------------------------------------------------------------------------------
#todo 各メソッドをまとめる

    async def process(self, gss_info: Dict, login_info: Dict):
        # スプシの読み込み（辞書でoutput）
        df = self.gss_read.getDataFrameFromGss(gss_info=gss_info)

        # dfの中からチェックがあるものだけ抽出
        process_df = df[df['チェック'] == True]
        self.logger.debug(process_df.head)

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

if __name__ == '__main__':
    gss_info = GssInfo.GAME_CLUB.value
    login_info = LoginInfo.SITE_PATTERNS.value['GAME_CLUB']
    print(f"login_info: {login_info}")
    test_flow = FlowGCNewItem()
    asyncio.run(test_flow.process(login_info))
