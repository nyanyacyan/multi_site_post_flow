# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# export PYTHONPATH="/Users/nyanyacyan/Desktop/project_file/multi_site_post_flow/installer/src"

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import asyncio
from typing import Dict
from selenium.webdriver.common.keys import Keys

# 自作モジュール
from method.base.utils import Logger
from method.base.chrome import ChromeManager
from method.base.loginWithId import SingleSiteIDLogin
from method.base.seleniumBase import SeleniumBasicOperations
from method.base.spreadsheetRead import GetDataGSSAPI
from method.base.elementManager import ElementManager
from method.base.decorators import Decorators
from method.base.jumpTargetPage import JumpTargetPage
from method.base.time_manager import TimeManager

# const
from .const_element import LoginInfo, GssInfo, SellInfo

deco = Decorators()

# ----------------------------------------------------------------------------------
# **********************************************************************************
# 一連の流れ


class FlowGameClubProcess:
    def __init__(self):
        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

        # 必要info
        self.gss_info = GssInfo.GAME_CLUB.value


    ####################################################################################
    # ----------------------------------------------------------------------------------
    # 各メソッドをまとめる

    def process(self, worksheet_name: str, id_text: str, pass_text: str):
        # 新しいブラウザを立ち上げ
        chrome_manager = ChromeManager()
        chrome = chrome_manager.flowSetupChrome()

        gss_read = GetDataGSSAPI()

        try:
            # スプシの読み込み（辞書でoutput）
            df = gss_read._get_df_in_gui(
                gss_info=self.gss_info, worksheet_name=worksheet_name
            )

            # dfの中からチェックがあるものだけ抽出
            process_df = df[df["チェック"] == "TRUE"].reset_index(drop=True)
            df_row_num = len(process_df)
            df_columns = process_df.shape[1]
            self.logger.debug(process_df.head)
            self.logger.debug(
                f"スプシの全行数: {df_row_num}行\nスプシの全column数: {df_columns}"
            )

            # インスタンス
            item_processor = FlowGameClubNewItem(chrome=chrome)

            # DFの各行に対して処理を行う
            for i, row in process_df.iterrows():
                # rowの情報を辞書化
                sell_data = row.to_dict()
                self.logger.debug(f"sell_data: {sell_data}")
                self.logger.info(f"{i + 1}/{df_row_num} タイトル: {sell_data['ゲームタイトル']}")
                self.logger.info(f"{i + 1}/{df_row_num} タイトル: {sell_data['出品タイトル']}")
                self.logger.info(f"{i + 1}/{df_row_num} タイトル: {sell_data['商品説明']}")
                self.logger.info(f"{i + 1}/{df_row_num} タイトル: {sell_data['商品価格']}")
                self.logger.info(f"{i + 1}/{df_row_num} 処理開始")

                # ログイン〜処理実施まで
                item_processor.row_process(
                    index=i, id_text=id_text, pass_text=pass_text, sell_data=sell_data
                )
                self.logger.info(f"{i + 1}/{df_row_num} 処理完了")

            self.logger.info(f"すべての処理完了")

        finally:
                chrome.quit()


    # ----------------------------------------------------------------------------------
# **********************************************************************************
# 一連の流れ


class FlowGameClubNewItem:
    def __init__(self, chrome):
        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

        # chrome
        self.chrome = chrome

        # インスタンス
        self.login = SingleSiteIDLogin(chrome=self.chrome)
        self.random_sleep = SeleniumBasicOperations(
            chrome=self.chrome,
        )

        self.element = ElementManager(chrome=self.chrome)
        self.jump_target_page = JumpTargetPage(chrome=self.chrome)
        self.time_manager = TimeManager()


        # 必要info
        self.login_info = LoginInfo.SITE_PATTERNS.value["GAME_CLUB"]
        self.sell_info = SellInfo.GAME_CLUB.value


    ####################################################################################

    # ログイン〜出品処理

    @deco.funcBase
    def row_process(self, index: int, id_text: str, pass_text: str, sell_data: Dict):
        self.logger.debug(f"index: {index}")
        if index == 0:
            # IDログイン
            self.login.flow_login_id_input_gui(
                login_info=self.login_info,
                id_text=id_text,
                pass_text=pass_text,
                timeout=120,
            )
        else:
            # Sessionを維持したままログインの手順を端折る
            self.jump_target_page.flowJumpTargetPage(
                targetUrl=self.login_info["HOME_URL"]
            )

        # 出品処理
        self.sell_process(sell_data=sell_data)

    # ----------------------------------------------------------------------------------
    # 出品処理

    def sell_process(self, sell_data: Dict):
        self.logger.debug(f"sell_processを開始:\n{sell_data}")
        # 出品ボタンをクリック
        self._click_first_sell_btn()

        # 画像添付
        self._photo_files_input(sell_data)

        # ゲームタイトルクリック
        self._game_title_click()

        # POPUPタイトル入力
        self._popup_title_input(sell_data=sell_data)

        # タイトルを選択
        self._game_title_select()

        # 種別を選択
        self._category_select(sell_data=sell_data)

        # 出品タイトル
        self._input_sell_title(sell_data=sell_data)

        # 商品説明
        self._input_game_explanation(sell_data=sell_data)

        # 買い手への初回msg
        self._input_first_msg(sell_data=sell_data)

        # 出品を通知
        self._user_notify(sell_data=sell_data)

        # 出品方法
        self._select_sell_method(sell_data=sell_data)

        # 商品価格
        self._input_price(sell_data=sell_data)

        # 暗証番号を設定
        self._click_input_pin()

        # 確認するをクリック
        self._check_click()

        # 出品するをクリック
        self._click_end_sell_btn()

    # ----------------------------------------------------------------------------------
    # 出品ボタンをクリック

    def _click_first_sell_btn(self):
        by = self.sell_info["FIRST_SELL_BTN_BY"]
        value = self.sell_info["FIRST_SELL_BTN_VALUE"]
        self.logger.debug(f"\nby: {by}\nvalue: {value}")
        self.element.clickElement(by=by, value=value)
        self._random_sleep()

    # ----------------------------------------------------------------------------------
    # 画像添付

    def _photo_files_input(self, sell_data: Dict):
        file_path_list = self.element._get_all_files_path_list(
            subDirName=self.sell_info["INPUT_PHOTO_FOLDER_NAME"],
            subSubDirName=sell_data["画像フォルダ"],
        )

        file_path_sort_list = self.element._list_sort_photo_data(all_photos_all_path_list=file_path_list)

        if file_path_sort_list:

            self.element.files_input(
                by=self.sell_info["FILE_INPUT_BY"],
                value=self.sell_info["FILE_INPUT_VALUE"],
                check_by=self.sell_info["CHECK_BY"],
                check_value=self.sell_info["CHECK_VALUE"],
                file_path_list=file_path_sort_list,
            )
            self._random_sleep()

    # ----------------------------------------------------------------------------------
    # ゲームタイトルクリック

    def _game_title_click(self):
        self.element.clickElement(
            by=self.sell_info["GAME_TITLE_CLICK_BY"],
            value=self.sell_info["GAME_TITLE_CLICK_VALUE"],
        )
        self._random_sleep()

    # ----------------------------------------------------------------------------------
    # POPUPタイトル入力

    def _popup_title_input(self, sell_data: Dict):
        input_game_title = sell_data["ゲームタイトル"]
        self.logger.debug(f"input_game_title: {input_game_title}")
        element = self.element.clickClearInput(
            by=self.sell_info["GAME_TITLE_INPUT_BY"],
            value=self.sell_info["GAME_TITLE_INPUT_VALUE"],
            inputText=input_game_title,
        )
        element.send_keys(Keys.RETURN)
        self._random_sleep()

    # ----------------------------------------------------------------------------------
    # タイトルを選択

    def _game_title_select(self):
        self.element.clickElement(
            by=self.sell_info["GAME_TITLE_SELECT_BY"],
            value=self.sell_info["GAME_TITLE_SELECT_VALUE"],
        )
        self._random_sleep()

    # ----------------------------------------------------------------------------------
    # カテゴリ選択

    def _category_select(self, sell_data: Dict):
        if sell_data["カテゴリ"] == "代行":
            element = self.element.clickElement(
                value=self.sell_info["CATEGORY_DAIKO_SELECT_VALUE"]
            )
            self.logger.debug(f"「代行」を選択: {element}")
            self._random_sleep()
        elif sell_data["カテゴリ"] == "リセマラ・初期垢":
            element = self.element.clickElement(
                value=self.sell_info["CATEGORY_RISEMARA_SELECT_VALUE"]
            )
            self.logger.debug(f"「リセマラ・初期垢」を選択: {element}")
            self._random_sleep()
        elif sell_data["カテゴリ"] == "アイテム・通貨":
            element = self.element.clickElement(
                value=self.sell_info["CATEGORY_ITEM_SELECT_VALUE"]
            )
            self.logger.debug(f"「アイテム・通貨」を選択: {element}")
            self._random_sleep()
        else:
            element = self.element.clickElement(
                value=self.sell_info["CATEGORY_INTAI_SELECT_VALUE"]
            )
            self.logger.debug(f"「引退垢」を選択: {element}")
            self._random_sleep

    # ----------------------------------------------------------------------------------
    # 出品タイトル

    def _input_sell_title(self, sell_data: Dict):
        input_sell_title = sell_data["出品タイトル"]
        self.logger.debug(f"input_sell_title: {input_sell_title}")
        self.element.clickClearInput(
            by=self.sell_info["SELL_TITLE_INPUT_BY"],
            value=self.sell_info["SELL_TITLE_INPUT_VALUE"],
            inputText=input_sell_title,
        )
        self._random_sleep()

    # ----------------------------------------------------------------------------------
    # 商品説明

    @deco.funcBase
    def _input_game_explanation(self, sell_data: Dict):
        input_game_explanation = sell_data["商品説明"]
        self.logger.debug(f"input_game_explanation: {input_game_explanation}")
        self.element.clickClearJsInput(
            by=self.sell_info["SELL_EXPLANATION_INPUT_BY"],
            value=self.sell_info["SELL_EXPLANATION_INPUT_VALUE"],
            inputText=input_game_explanation,
        )
        self._random_sleep()

    # ----------------------------------------------------------------------------------
    # 課金総額

    def _input_charge(self, sell_data: Dict):
        input_charge = sell_data["課金総額"]
        if not input_charge:
            self.logger.warning(f"「課金総額」入力なし: {input_charge}")
        self.logger.debug(f"input_game_explanation: {input_charge}")
        self.element.clickClearInput(
            value=self.sell_info["CHARGE_VALUE"], inputText=input_charge
        )
        self._random_sleep()

    # ----------------------------------------------------------------------------------
    # 買い手へ初回自動表示するメッセージ

    @deco.funcBase
    def _input_first_msg(self, sell_data: Dict):
        input_first_msg = sell_data["買い手へ初回自動表示するメッセージ"]
        if not input_first_msg:
            self.logger.warning(
                f"「買い手へ初回自動表示するメッセージ」入力なし: {input_first_msg}"
            )
            return

        self.logger.debug(f"input_first_msg: {input_first_msg}")
        self.element.clickClearInput(
            by=self.sell_info["FIRST_MSG_BY"],
            value=self.sell_info["FIRST_MSG_VALUE"],
            inputText=input_first_msg,
        )
        self._random_sleep()

    # ----------------------------------------------------------------------------------
    # 出品を通知

    @deco.funcBase
    def _user_notify(self, sell_data: Dict):
        input_sell_notify = sell_data["出品を通知"]
        if not input_sell_notify:
            self.logger.warning(f"「出品を通知」入力なし: {input_sell_notify}")
            return

        self.logger.debug(f"input_sell_notify: {input_sell_notify}")
        self.element.clickClearInput(
            value=self.sell_info["USER_NOTIFY"], inputText=input_sell_notify
        )
        self._random_sleep()

    # ----------------------------------------------------------------------------------
    # 出品方法

    @deco.funcBase
    def _select_sell_method(self, sell_data: Dict):
        select_sell_method = sell_data["出品方法"]
        if select_sell_method == "タイムセール":
            self.logger.info(f"「タイムセール」選択: {select_sell_method}")
            self.element.clickElement(
                value=self.sell_info["SELL_METHOD_TIME_SALE_VALUE"]
            )
        else:
            self.logger.info(
                f"「フリマ販売」選択のためアクションなし: {select_sell_method}"
            )
            # self.element.clickElement(value=self.sell_info['SELL_METHOD_FURIMA_VALUE'])
        self._random_sleep()

    # ----------------------------------------------------------------------------------
    # 商品価格

    @deco.funcBase
    def _input_price(self, sell_data: Dict):
        input_price = sell_data["商品価格"]
        self.logger.debug(f"input_price: {input_price}")
        self.element.clickClearInput(
            value=self.sell_info["PRICE_VALUE"], inputText=input_price
        )
        self._random_sleep(min_num=3, max_num=5)

    # ----------------------------------------------------------------------------------
    # 暗証番号をクリックして入力

    def _click_input_pin(self):
        self.element.clickElement(value=self.sell_info["PIN_CHECK_CLICK_VALUE"])
        self._random_sleep()

        # 暗証番号を入力
        input_pin = self.sell_info["PIN_INPUT_VALUE"]
        self.logger.debug(f"input_pin: {input_pin}")
        self.element.clickClearJsInput(
            by=self.sell_info["PIN_INPUT_AREA_BY"],
            value=self.sell_info["PIN_INPUT_AREA_VALUE"],
            inputText=input_pin,
        )
        self._random_sleep()

    # ----------------------------------------------------------------------------------
    # 確認するをクリック

    @deco.funcBase
    def _check_click(self):
        self.element.clickElement(value=self.sell_info["CHECK_VALUE"])
        self._random_sleep()

    # ----------------------------------------------------------------------------------
    # 出品するをクリック
    @deco.funcBase
    def _click_end_sell_btn(self):
        self.element.clickElement(value=self.sell_info["SELL_BTN"])
        self._random_sleep(min_num=2, max_num=5)

    # ----------------------------------------------------------------------------------
    # ランダムSleep

    def _random_sleep(self, min_num: int = 1, max_num: int = 3):
        self.random_sleep._random_sleep(min_num=min_num, max_num=max_num)


# ----------------------------------------------------------------------------------
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# テスト実施

if __name__ == "__main__":
    worksheet_name = LoginInfo.SITE_PATTERNS.value["GAME_CLUB"]["SITE_NAME"]
    id_text = LoginInfo.SITE_PATTERNS.value["GAME_CLUB"]["ID_TEXT"]
    pass_text = LoginInfo.SITE_PATTERNS.value["GAME_CLUB"]["PASS_TEXT"]
    print(
        f"worksheet_name: {worksheet_name}\nid_text: {id_text}\npass_text: {pass_text}"
    )

    test_flow = FlowGameClubNewItem()
    asyncio.run(
        test_flow.process(
            worksheet_name=worksheet_name, id_text=id_text, pass_text=pass_text
        )
    )
