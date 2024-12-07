# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# export PYTHONPATH="/Users/nyanyacyan/Desktop/project_file/domain_search/installer/src"


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import os, time, asyncio

# 自作モジュール
from base.utils import Logger
from base.chrome import ChromeManager
from base.loginWithId import LoginID



# ----------------------------------------------------------------------------------
# **********************************************************************************
# 一連の流れ

class FlowGetCookie:
    def __init__(self, debugMode=True):

        # logger
        self.getLogger = Logger(__name__, debugMode=debugMode)
        self.logger = self.getLogger.getLogger()

        # chrome
        self.chromeManager = ChromeManager(debugMode=debugMode)
        self.chrome = self.chromeManager.flowSetupChrome()

        # const


        # インスタンス
        self.id_login = LoginID(chrome=self.chrome, debugMode=debugMode)



####################################################################################
# ----------------------------------------------------------------------------------
#todo 各メソッドをまとめる

    async def process(self):
        await self.id_login.flow_cookie_save(
            url=,
            loginInfo=,
            tableName=,
            columnsName=
        )








# ----------------------------------------------------------------------------------
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# テスト実施

if __name__ == '__main__':
    test_flow = Flow()
    asyncio.run(test_flow.process())
