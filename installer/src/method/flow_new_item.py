# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# export PYTHONPATH="/Users/nyanyacyan/Desktop/project_file/domain_search/installer/src"


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import os, time, asyncio

# 自作モジュール
from .base.utils import Logger
from .base.chrome import ChromeManager



# ----------------------------------------------------------------------------------
# **********************************************************************************
# 一連の流れ

class FlowNewItem:
    def __init__(self, debugMode=True):

        # logger
        self.getLogger = Logger(__name__, debugMode=debugMode)
        self.logger = self.getLogger.getLogger()

        # chrome
        self.chromeManager = ChromeManager(debugMode=debugMode)
        self.chrome = self.chromeManager.flowSetupChrome()

        # const



        # インスタンス



####################################################################################
# ----------------------------------------------------------------------------------
#todo 各メソッドをまとめる

    async def process(self):
        await self.gss_to_notify.flowProcess()








# ----------------------------------------------------------------------------------
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# テスト実施

if __name__ == '__main__':
    test_flow = Flow()
    asyncio.run(test_flow.process())
