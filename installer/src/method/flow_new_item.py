# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# export PYTHONPATH="/Users/nyanyacyan/Desktop/project_file/domain_search/installer/src"


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import os, time, asyncio

# 自作モジュール
from base.utils import Logger
from base.chrome import ChromeManager
from base.login_db_cookie import SingleLoginDBCookie


from const_str import SiteName, GameClubInfo

# ----------------------------------------------------------------------------------
# **********************************************************************************
# 一連の流れ

class FlowNewItem:
    def __init__(self, home_url: str, table_name: str, debugMode=True):

        # logger
        self.getLogger = Logger(__name__, debugMode=debugMode)
        self.logger = self.getLogger.getLogger()

        # chrome
        self.chromeManager = ChromeManager(debugMode=debugMode)
        self.chrome = self.chromeManager.flowSetupChrome()

        # const
        self.home_url = home_url
        self.table_name = table_name



        # インスタンス
        self.cookie_login = SingleLoginDBCookie(chrome=self.chrome, debugMode=debugMode)


####################################################################################
# ----------------------------------------------------------------------------------
#todo 各メソッドをまとめる

    async def process(self):
        self.cookie_login._cookie_login(home_url=self.home_url, table_name=self.table_name)

        # Cookieログイン


        # 自動出品








# ----------------------------------------------------------------------------------
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# テスト実施

if __name__ == '__main__':
    home_url = GameClubInfo.HOME_URL.value
    table_name = SiteName.GAME_CLUB.value
    test_flow = FlowNewItem(home_url=home_url, table_name=table_name)
    asyncio.run(test_flow.process())
