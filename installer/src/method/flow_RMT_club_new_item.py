# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# export PYTHONPATH="/Users/nyanyacyan/Desktop/project_file/domain_search/installer/src"


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import time
from typing import Dict
from selenium import webdriver
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
from method.const_element import LoginInfo, GssInfo, SellInfo

deco = Decorators()

# ----------------------------------------------------------------------------------
# **********************************************************************************
# 一連の流れ


class FlowRMTProcess:
    def __init__(self):
        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

        # 必要info
        self.gss_info = GssInfo.RMT_CLUB.value


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
            item_processor = FlowRMTClubNewItem(chrome=chrome)

            # DFの各行に対して処理を行う
            for i, row in process_df.iterrows():
                # rowの情報を辞書化
                sell_data = row.to_dict()
                self.logger.debug(f"sell_data: {sell_data}")
                self.logger.info(f"{i + 1}/{df_row_num} タイトル: {sell_data['ゲーム名']}")
                self.logger.info(f"{i + 1}/{df_row_num} タイトル: {sell_data['掲載タイトル']}")
                self.logger.info(f"{i + 1}/{df_row_num} タイトル: {sell_data['詳細内容']}")
                self.logger.info(f"{i + 1}/{df_row_num} タイトル: {sell_data['取引価格']}")
                self.logger.info(f"{i + 1}/{df_row_num} 処理開始")

                # ログイン〜処理実施まで
                item_processor.row_process(
                    index=i, id_text=id_text, pass_text=pass_text, sell_data=sell_data
                )
                self.logger.info(f"{i + 1}/{df_row_num} 処理完了")

            self.logger.info(f"すべての処理完了")

        finally:
                chrome.quit()


# **********************************************************************************
# 一連の流れ

class FlowRMTClubNewItem:
    def __init__(self, chrome: webdriver):
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
        self.login_info = LoginInfo.SITE_PATTERNS.value['RMT_CLUB']
        self.sell_info = SellInfo.RMT_CLUB.value


####################################################################################
# ----------------------------------------------------------------------------------
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
        # 出品ボタンをクリック
        self._sell_btn_click()

        # 売りたいを選択
        self._sell_select_btn_click()

        # ゲームタイトル入力
        self._input_game_title(sell_data=sell_data)

        # アカウント種別の選択
        self._category_select(sell_data=sell_data)

        # 掲載タイトル
        self._input_comment_title(sell_data=sell_data)

        # タグ入力
        self._input_tag(sell_data=sell_data)

        # 商品説明
        self._input_sell_explanation(sell_data=sell_data)

        # 画像添付
        self._photo_files_input(sell_data)

        # ユーザーに出品を通知する →条件分岐させる
        self._user_notify(sell_data=sell_data)

        # 商品価格
        self._input_price(sell_data=sell_data)

        # 確認するをクリック
        self._click_check()

        # 同意するにレ点
        self._click_agree()

        # 出品するをクリック
        self._click_sell_finish_btn()

        # マイページへ戻る
        self._my_page_click()


# ----------------------------------------------------------------------------------
# 出品ボタンをクリック

    def _sell_btn_click(self):
        self.element.clickElement(value=self.sell_info['SELL_BTN_ONE'])
        self._random_sleep()


# ----------------------------------------------------------------------------------
# 売りたいをクリック

    def _sell_select_btn_click(self):
        self.element.clickElement(value=self.sell_info['SELL_SELECT_BTN'])
        self._random_sleep()


# ----------------------------------------------------------------------------------
# ゲームタイトル入力
# EnterKeyが必要かも→アカウント種別などが変わる

    def _input_game_title(self, sell_data: Dict):
        input_game_title = sell_data['ゲーム名']
        self.logger.debug(f'input_game_title: {input_game_title}')
        element = self.element.clickClearInput(by=self.sell_info['SELL_TITLE_INPUT_BY'], value=self.sell_info['SELL_TITLE_INPUT_VALUE'], inputText=input_game_title)
        element.send_keys(Keys.RETURN)
        self._random_sleep()


# ----------------------------------------------------------------------------------
# カテゴリ選択

    def _category_select(self, sell_data: Dict):
        if sell_data['アカウントの種別'] == 'アイテム・通貨':
            element = self.element.clickElement(value=self.sell_info['CATEGORY_ITEM_SELECT_VALUE'])
            self.logger.debug(f'「アイテム・通貨」を選択: {element}')
            self._random_sleep()
        elif sell_data['アカウントの種別'] == 'リセマラ':
            element = self.element.clickElement(value=self.sell_info['CATEGORY_ITEM_SELECT_VALUE'])
            self.logger.debug(f'「リセマラ」を選択: {element}')
            self._random_sleep()
        elif sell_data['アカウントの種別'] == '代行':
            element = self.element.clickElement(value=self.sell_info['CATEGORY_DAIKO_SELECT_VALUE'])
            self.logger.debug(f'「代行」を選択: {element}')
            self._random_sleep()
        else:
            element = self.element.clickElement(value=self.sell_info['CATEGORY_ACCOUNT_SELECT_VALUE'])
            self.logger.debug(f'「アカウント」を選択: {element}')
            self._random_sleep()


# ----------------------------------------------------------------------------------
# 掲載タイトルの入力

    def _input_comment_title(self, sell_data: Dict):
        input_comment_title = sell_data['掲載タイトル']
        self.logger.debug(f'input_comment_title: {input_comment_title}')
        self.element.clickClearJsInput(by=self.sell_info['COMMENT_TITLE_BY'], value=self.sell_info['COMMENT_TITLE_VALUE'], inputText=input_comment_title)
        self._random_sleep()


# ----------------------------------------------------------------------------------
# タグ欄への入力

    def _input_tag(self, sell_data: Dict):
        input_tag = sell_data['タグ']
        if not input_tag:
            self.logger.warning(f'「タグ」入力なし: {input_tag}')
            return

        self.logger.debug(f'input_tag: {input_tag}')
        self.element.clickClearInput(by=self.sell_info['TAG_BY'], value=self.sell_info['TAG_VALUE'], inputText=input_tag)
        self._random_sleep()


# ----------------------------------------------------------------------------------
# 詳細内容の入力

    def _input_sell_explanation(self, sell_data: Dict):
        input_sell_explanation = sell_data['詳細内容']
        self.logger.debug(f'input_sell_explanation: {input_sell_explanation}')
        self.element.clickClearJsInput(by=self.sell_info['SELL_EXPLANATION_INPUT_BY'], value=self.sell_info['SELL_EXPLANATION_INPUT_VALUE'], inputText=input_sell_explanation)
        self._random_sleep()


# ----------------------------------------------------------------------------------
# 画像添付

    def _photo_files_input(self, sell_data: Dict):
        file_path_list = self.element._get_all_files_path_list(subDirName=self.sell_info['INPUT_PHOTO_FOLDER_NAME'], subSubDirName=sell_data['画像フォルダ'])
        self.element.files_input(value=self.sell_info['FILE_INPUT_VALUE'], check_by=self.sell_info['CHECK_BY'], check_value=self.sell_info['CHECK_VALUE'], file_path_list=file_path_list)
        self._random_sleep()


# ----------------------------------------------------------------------------------
# 「ユーザーに出品を通知」に入力

    def _user_notify(self, sell_data: Dict):
        user_notify = sell_data['ユーザーに出品を通知する']
        if not user_notify:
            self.logger.warning(f'「ユーザーに出品を通知する」入力なし: {user_notify}')
            return

        self.logger.debug(f'user_notify: {user_notify}')
        self.element.clickClearInput(by=self.sell_info['USER_NOTIFY_BY'], value=self.sell_info['USER_NOTIFY_VALUE'], inputText=user_notify)
        self._random_sleep()


# ----------------------------------------------------------------------------------
# 取引価格

    def _input_price(self, sell_data: Dict):
        input_price = sell_data['取引価格']
        self.logger.debug(f'input_price: {input_price}')
        self.element.clickClearInput(by=self.sell_info['PRICE_BY'], value=self.sell_info['PRICE_VALUE'], inputText=input_price)
        self._random_sleep()


# ----------------------------------------------------------------------------------
# 確認するをクリック

    def _click_check(self):
        self.element.clickElement(value=self.sell_info['CHECK_VALUE'])
        self._random_sleep()


# ----------------------------------------------------------------------------------
# 「同意する」にレ点

    def _click_agree(self):
        self.element.clickElement(value=self.sell_info['AGREE_VALUE'])
        self._random_sleep()


# ----------------------------------------------------------------------------------
# 出品するをクリック

    def _click_sell_finish_btn(self):
        self.element.clickElement(value=self.sell_info['SELL_BTN'])
        self._random_sleep()


# ----------------------------------------------------------------------------------
# マイページへ戻る

    def _my_page_click(self):
        self.element.clickElement(value=self.sell_info['MY_PAGE_VALUE'])
        self._random_sleep()


# ----------------------------------------------------------------------------------
    # ランダムSleep

    def _random_sleep(self, min_num: int = 1, max_num: int = 3):
        self.random_sleep._random_sleep(min_num=min_num, max_num=max_num)


# ----------------------------------------------------------------------------------
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# テスト実施

if __name__ == '__main__':
    worksheet_name = LoginInfo.SITE_PATTERNS.value["RMT_CLUB"]["SITE_NAME"]
    id_text = LoginInfo.SITE_PATTERNS.value["RMT_CLUB"]["ID_TEXT"]
    pass_text = LoginInfo.SITE_PATTERNS.value["RMT_CLUB"]["PASS_TEXT"]
    print(
        f"worksheet_name: {worksheet_name}\nid_text: {id_text}\npass_text: {pass_text}"
    )
    test_flow = FlowRMTProcess()
    test_flow.process(worksheet_name=worksheet_name, id_text=id_text, pass_text=pass_text)

