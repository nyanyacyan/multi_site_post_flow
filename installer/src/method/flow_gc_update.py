# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# export PYTHONPATH="/Users/nyanyacyan/Desktop/project_file/domain_search/installer/src"


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import

# 自作モジュール
from base.utils import Logger
from base.chrome import ChromeManager
from base.loginWithId import SingleSiteIDLogin
from base.seleniumBase import SeleniumBasicOperations
from base.elementManager import ElementManager
from base.decorators import Decorators
from base.time_manager import TimeManager

# const
from const_element import LoginInfo, UpdateInfo

deco = Decorators()

# ----------------------------------------------------------------------------------
# **********************************************************************************
# 一連の流れ


class FlowGameClubUpdate:
    def __init__(self):
        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

        # chrome
        self.chromeManager = ChromeManager()
        self.chrome = self.chromeManager.flowSetupChrome()

        # インスタンス
        self.login = SingleSiteIDLogin(chrome=self.chrome)
        self.random_sleep = SeleniumBasicOperations(chrome=self.chrome)
        self.element = ElementManager(chrome=self.chrome)
        self.time_manager = TimeManager()


        # 必要info
        self.login_info = LoginInfo.SITE_PATTERNS.value["GAME_CLUB"]
        self.update_info = UpdateInfo.GAME_CLUB.value


    ####################################################################################
    # ----------------------------------------------------------------------------------
    # アップロードプロセス

    @deco.funcBase
    def process(self, id_text: str, pass_text: str):
        # idログイン
        self._id_login(id_text=id_text, pass_text=pass_text)

        # 出品した商品をクリック
        self._click_sell_item_btn()

        # 日時が古い順を選択
        self._select_old_datetime()

        # 無効化されているか確認
        self._disable_element_check_process()


    # ----------------------------------------------------------------------------------
    # idログイン

    def _id_login(self, id_text: str, pass_text: str):
            self.login.flow_login_id_input_gui(
                login_info=self.login_info,
                id_text=id_text,
                pass_text=pass_text,
                timeout=120,
            )


    # ----------------------------------------------------------------------------------
    # 出品した商品をクリック

    def _click_sell_item_btn(self):
        value = self.update_info["SELL_ITEM_BTN_VALUE"]
        self.logger.debug(f"value: {value}")
        self.element.clickElement(value=value)
        self._random_sleep()


    # ----------------------------------------------------------------------------------
    # 出品した日時をクリック→_select_old_datetimeで事足りるかな？

    # def _click_item_sort_btn(self):
    #     value = self.update_info["ITEM_SORT_BTN_VALUE"]
    #     self.logger.debug(f"value: {value}")
    #     self.element.clickElement(value=value)
    #     self._random_sleep()


    # ----------------------------------------------------------------------------------
    # 日時が古い順を選択

    def _select_old_datetime(self):
        value = self.update_info["ITEM_SORT_BTN_VALUE"]
        select_value = self.update_info["SELECT_VALUE"]
        self.logger.debug(f"value: {value}\nselect_value: {select_value}")
        self.element._select_element(value=value, select_value=select_value)
        self._random_sleep()


    # ----------------------------------------------------------------------------------
    # 無効化されているか確認

    def _disable_element_check_process(self):
        value = self.update_info["DISABLE_ELEMENT_VALUE"]
        self.logger.debug(f"value: {value}")
        disable_element_bool = self.element._disable_element_check(value=value)

        max_count = 15
        count = 0
        while count < max_count:
            if not disable_element_bool:
                self.logger.debug(f"クリック試行: {count + 1}回目")
                self._click_update_btn()
                count += 1
                self._random_sleep()

            else:
                self.logger.info(f'更新の上限に達しました: 実施回数 {count}回、Update実施')
                break


    # ----------------------------------------------------------------------------------
    # 更新処理

    def _click_update_btn(self):
        value = self.update_info["UPDATE_BTN_VALUE"]
        self.logger.debug(f"value: {value}")
        self.element.clickElement(value=value)
        self._random_sleep()


    # ----------------------------------------------------------------------------------
    # ランダムSleep

    def _random_sleep(self, min_num: int = 1, max_num: int = 3):
        self.random_sleep._random_sleep(min_num=min_num, max_num=max_num)


# ----------------------------------------------------------------------------------
