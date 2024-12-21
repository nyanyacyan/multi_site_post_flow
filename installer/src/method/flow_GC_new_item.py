# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# export PYTHONPATH="/Users/nyanyacyan/Desktop/project_file/domain_search/installer/src"


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import os, time, asyncio
from typing import Dict, List


# 自作モジュール
from base.utils import Logger
from base.chrome import ChromeManager
from base.loginWithId import SingleSiteIDLogin
from base.seleniumBase import SeleniumBasicOperations

# const
from const_str import SiteName, GameClubInfo
from const_element import LoginInfo

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


####################################################################################
# ----------------------------------------------------------------------------------
#todo 各メソッドをまとめる

    async def process(self, login_info: Dict):
        # IDログイン
        self.login.flowLoginID(login_info=login_info, timeout=120)

        # ランダム待機
        self.random_sleep._random_sleep()

        # 操作していく








# ----------------------------------------------------------------------------------
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# テスト実施

if __name__ == '__main__':
    login_info = LoginInfo.SITE_PATTERNS.value['GAME_CLUB']
    print(f"login_info: {login_info}")
    test_flow = FlowGCNewItem()
    asyncio.run(test_flow.process(login_info))
