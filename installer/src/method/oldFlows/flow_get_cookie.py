# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# export PYTHONPATH="/Users/nyanyacyan/Desktop/project_file/domain_search/installer/src"


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import os, time, asyncio

# 自作モジュール
from base.utils import Logger
from base.chrome import ChromeManager
from base.loginWithId import SingleSiteIDLogin

from const_str import SiteName, FileName
from const_element import LoginInfo
from constSqliteTable import TableSchemas


# ----------------------------------------------------------------------------------
# **********************************************************************************
# 一連の流れ


class FlowGetCookie:
    def __init__(
        self, site_name: str, db_file_name: str, table_pattern_info: str, debugMode=True
    ):

        # logger
        self.getLogger = Logger(
            moduleName=FileName.LOG_FILE_NAME.value, debugMode=debugMode
        )
        self.logger = self.getLogger.getLogger()

        # chrome
        self.chromeManager = ChromeManager(debugMode=debugMode)
        self.chrome = self.chromeManager.flowSetupChrome()

        # const
        login_pattern_dict = LoginInfo.SITE_PATTERNS.value
        self.login_info = login_pattern_dict[site_name]

        # インスタンス
        self.id_login = SingleSiteIDLogin(
            chrome=self.chrome,
            db_file_name=db_file_name,
            table_pattern_info=table_pattern_info,
            debugMode=debugMode,
        )

    ####################################################################################
    # ----------------------------------------------------------------------------------
    # todo 各メソッドをまとめる

    async def process(self):
        # ログインからCookieをDBへ保存
        await self.id_login.flow_cookie_save(
            login_url=self.login_info["LOGIN_URL"],
            login_info=self.login_info,
            table_name=self.login_info["TABLE_NAME"],
        )

        return self.logger.debug(f"bool: {bool}")

    # ----------------------------------------------------------------------------------
    # ----------------------------------------------------------------------------------
    # todo 各メソッドをまとめる

    async def pickle_process(self):
        # ログインからCookieをDBへ保存
        await self.id_login.flow_cookie_pickle_save(
            login_url=self.login_info["LOGIN_URL"],
            login_info=self.login_info,
        )

        return self.logger.debug(f"bool: {bool}")


# ----------------------------------------------------------------------------------
# **********************************************************************************


class GameClubClubGetCookieFlow(FlowGetCookie):
    def __init__(self, debugMode=True):
        site_name = SiteName.GAME_CLUB.value
        db_file_name = SiteName.GAME_CLUB.value
        table_pattern_info = TableSchemas.GAME_CLUB.value
        super().__init__(
            site_name=site_name,
            db_file_name=db_file_name,
            table_pattern_info=table_pattern_info,
            debugMode=debugMode,
        )


# **********************************************************************************


class MAClubGetCookieFlow(FlowGetCookie):
    def __init__(self, debugMode=True):
        site_name = SiteName.MA_CLUB.value
        db_file_name = SiteName.MA_CLUB.value
        table_pattern_info = TableSchemas.MA_CLUB.value
        super().__init__(
            site_name=site_name,
            db_file_name=db_file_name,
            table_pattern_info=table_pattern_info,
            debugMode=debugMode,
        )


# **********************************************************************************


class RRMTClubGetCookieFlow(FlowGetCookie):
    def __init__(self, debugMode=True):
        site_name = SiteName.RRMT_CLUB.value
        db_file_name = SiteName.RRMT_CLUB.value
        table_pattern_info = TableSchemas.RRMT_CLUB.value
        super().__init__(
            site_name=site_name,
            db_file_name=db_file_name,
            table_pattern_info=table_pattern_info,
            debugMode=debugMode,
        )


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# テスト実施

if __name__ == "__main__":

    async def test_flows():
        game_club_flow = GameClubClubGetCookieFlow()
        # ma_club_flow = MAClubGetCookieFlow()
        # rrmt_club_flow = RRMTClubGetCookieFlow()

        await asyncio.gather(
            game_club_flow.pickle_process(),
            # ma_club_flow.process(),
            # rrmt_club_flow.process()
        )

    asyncio.run(test_flows())
