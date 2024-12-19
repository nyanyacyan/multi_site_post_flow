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
from base.fileRead import ResultFileRead


from const_str import SiteName, GameClubInfo

# ----------------------------------------------------------------------------------
# **********************************************************************************
# 一連の流れ

class FlowLoginCookie:
    def __init__(self, home_url: str, db_file_name: str, debugMode=True):

        # logger
        self.getLogger = Logger(__name__, debugMode=debugMode)
        self.logger = self.getLogger.getLogger()

        # chrome
        self.chromeManager = ChromeManager(debugMode=debugMode)
        self.chrome = self.chromeManager.flowSetupChrome()

        # const
        self.home_url = home_url
        self.db_file_name = db_file_name



        # インスタンス
        self.cookie_login = SingleLoginDBCookie(chrome=self.chrome, db_file_name=self.db_file_name, debugMode=debugMode)
        self.pickle_read = ResultFileRead(debugMode=debugMode)

####################################################################################
# ----------------------------------------------------------------------------------
#todo 各メソッドをまとめる

    async def process(self):
        cookie = self.pickle_read.readPickleLatestResult()

        self.cookie_login._cookie_login(home_url=self.home_url, cookie_info=cookie)









# ----------------------------------------------------------------------------------
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# テスト実施

if __name__ == '__main__':
    home_url = GameClubInfo.HOME_URL.value
    db_file_name = SiteName.GAME_CLUB.value
    test_flow = FlowLoginCookie(home_url=home_url, db_file_name=db_file_name)
    asyncio.run(test_flow.process())
