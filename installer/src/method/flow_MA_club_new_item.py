# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# export PYTHONPATH="/Users/nyanyacyan/Desktop/project_file/domain_search/installer/src"


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import asyncio, threading
from typing import Dict
from selenium.common.exceptions import NoSuchElementException
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

class FlowMAClubNewItem:
    def __init__(self):
        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

        # chrome
        self.chromeManager = ChromeManager()
        self.chrome = self.chromeManager.flowSetupChrome()

        # インスタンス
        self.login = SingleSiteIDLogin(chrome=self.chrome, )
        self.random_sleep = SeleniumBasicOperations(chrome=self.chrome, )
        self.gss_read = GetDataGSSAPI()
        self.element = ElementManager(chrome=self.chrome, )
        self.jump_target_page = JumpTargetPage(chrome=self.chrome)
        self.time_manager = TimeManager()

        # 必要info
        self.gss_info = GssInfo.MA_CLUB.value
        self.login_info = LoginInfo.SITE_PATTERNS.value['MA_CLUB']
        self.sell_info = SellInfo.MA_CLUB.value


####################################################################################
    # ----------------------------------------------------------------------------------
    # ループ処理を行う

    async def loop_process(self, start_wait_time_info: Dict, stop_event: threading.Event, worksheet_name: str, id_text: str, pass_text: str, random_info: Dict):
        # 開始時間
        self.time_manager._start_wait_for_time(start_wait_time_info)

        # stop_eventのフラグが立つまでは実行し続ける
        while not stop_event.is_set():
            await self.process(
                worksheet_name=worksheet_name,
                id_text=id_text,
                pass_text=pass_text
            )

            # 設定した待機をランダムで実行
            self.time_manager._random_sleep(random_info=random_info)


    # ----------------------------------------------------------------------------------
    # 各メソッドをまとめる

    async def process(self, worksheet_name: str, id_text: str, pass_text: str):
        # スプシの読み込み（辞書でoutput）
        df = self.gss_read._get_df_in_gui(
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

        # 各行に対して処理を行う
        for i, row in process_df.iterrows():
            # rowの情報を辞書化
            sell_data = row.to_dict()
            self.logger.debug(f"sell_data: {sell_data}")
            self.logger.info(
                f"{i + 1}/{df_row_num} タイトル: {sell_data['案件タイトル']}"
            )
            self.logger.info(
                f"{i + 1}/{df_row_num} タイトル: {sell_data['出品タイトル']}"
            )
            self.logger.info(f"{i + 1}/{df_row_num} タイトル: {sell_data['案件説明']}")
            self.logger.info(f"{i + 1}/{df_row_num} タイトル: {sell_data['売却価格']}")
            self.logger.info(f"{i + 1}/{df_row_num} 処理開始")

            # ログイン〜処理実施まで
            self.row_process(
                index=i, id_text=id_text, pass_text=pass_text, sell_data=sell_data
            )
            self.logger.info(f"{i + 1}/{df_row_num} 処理完了")

        self.logger.info(f"{self.login_info['SITE_NAME']}すべての処理完了")

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
        self._click_first_sell_btn()

        # 画像添付
        self._photo_files_input(sell_data)

        # 案件カテゴリ欄をクリック
        self._case_title_click()

        # POPUPタイトル入力
        self._popup_title_input(sell_data=sell_data)

        # タイトルを選択
        self._case_title_select()

        # 種別を選択
        self._category_select(sell_data=sell_data)

        # 案件タイトル
        self._input_sell_title(sell_data=sell_data)

        # 案件説明
        self._input_game_explanation(sell_data=sell_data)

        # 買い主へ初回自動表示するメッセージ
        self._input_first_msg(sell_data=sell_data)

        # 案件の登録を通知
        self._user_notify(sell_data=sell_data)

        # 商品価格
        self._input_price(sell_data=sell_data)

        # 暗証番号を設定
        self._click_input_pin()

        # 確認するをクリック
        self._check_click()

        # 売却登録するをクリック
        self._click_end_sell_btn()


# ----------------------------------------------------------------------------------
# 出品ボタンをクリック

    def _click_first_sell_btn(self):
        by = self.sell_info['FIRST_SELL_BTN_BY']
        value = self.sell_info['FIRST_SELL_BTN_VALUE']
        self.logger.debug(f'\nby: {by}\nvalue: {value}')
        self.element.clickElement(by=by, value=value)
        self._random_sleep()


# ----------------------------------------------------------------------------------
# 画像添付

    def _photo_files_input(self, sell_data: Dict):
        file_path_list = self.element._get_all_files_path_list(subDirName=self.sell_info['INPUT_PHOTO_FOLDER_NAME'], subSubDirName=sell_data['画像フォルダ'])
        self.element.files_input(by=self.sell_info['FILE_INPUT_BY'], value=self.sell_info['FILE_INPUT_VALUE'], check_by=self.sell_info['CHECK_BY'], check_value=self.sell_info['CHECK_VALUE'], file_path_list=file_path_list)
        self._random_sleep()


# ----------------------------------------------------------------------------------
# 案件カテゴリーをクリック

    def _case_title_click(self):
        self.element.clickElement(by=self.sell_info['CASE_TITLE_CLICK_BY'], value=self.sell_info['CASE_TITLE_CLICK_VALUE'])
        self._random_sleep()


# ----------------------------------------------------------------------------------
# POPUPに案件タイトル入力

    def _popup_title_input(self, sell_data: Dict):
        input_case_title = sell_data['案件タイトル']
        self.logger.debug(f'input_case_title: {input_case_title}')
        element = self.element.clickClearJsInput(by=self.sell_info['CASE_TITLE_INPUT_BY'], value=self.sell_info['CASE_TITLE_INPUT_VALUE'], inputText=input_case_title)
        element.send_keys(Keys.RETURN)
        self._random_sleep()


# ----------------------------------------------------------------------------------
# 案件タイトルを選択

    @deco.funcBase
    def _case_title_select(self):
        self.element.clickElement(by=self.sell_info['CASE_TITLE_SELECT_BY'], value=self.sell_info['CASE_TITLE_SELECT_VALUE'])
        self._random_sleep()


# ----------------------------------------------------------------------------------
# カテゴリ選択
# スプシが選ばれているものがアンマッチしている場合の例外処理→スプシにないことをPOP出してエラーを出す→

    @deco.funcBase
    def _category_select(self, sell_data: Dict):
        try:
            if sell_data['カテゴリ'] == 'サイト売買・サービス譲渡':
                element = self.element.clickElement(value=self.sell_info['CATEGORY_SELL_SELECT_VALUE'])
                self.logger.debug(f'「サイト売買・サービス譲渡」を選択: {element}')
                self._random_sleep()
            elif sell_data['カテゴリ'] == 'その他':
                element = self.element.clickElement(value=self.sell_info['CATEGORY_OTHER_SELECT_VALUE'])
                self.logger.debug(f'「その他」を選択: {element}')
                self._random_sleep()
            elif sell_data['カテゴリ'] == '運用代行':
                element = self.element.clickElement(value=self.sell_info['CATEGORY_UNYODAIKO_SELECT_VALUE'])
                self.logger.debug(f'「運用代行」を選択: {element}')
                self._random_sleep()
            else:
                element = self.element.clickElement(value=self.sell_info['CATEGORY_JYOTO_SELECT_VALUE'])
                self.logger.debug(f'「アカウント譲渡」を選択: {element}')
                self._random_sleep()
        # スプシ誤選択
        except NoSuchElementException:
            error_msg = f"スプシ項目に誤り\n【案件タイトル】{sell_data['案件タイトル']} 選択項目: {sell_data['カテゴリ']}"
            self.logger.warning(error_msg)



# ----------------------------------------------------------------------------------
# 案件タイトル

    @deco.funcBase
    def _input_sell_title(self, sell_data: Dict):
        input_sell_title = sell_data['出品タイトル']
        self.logger.debug(f'input_sell_title: {input_sell_title}')
        self.element.clickClearJsInput(by=self.sell_info['SELL_TITLE_INPUT_BY'], value=self.sell_info['SELL_TITLE_INPUT_VALUE'], inputText=input_sell_title)
        self._random_sleep()


# ----------------------------------------------------------------------------------
# 案件説明

    @deco.funcBase
    def _input_game_explanation(self, sell_data: Dict):
        input_game_explanation = sell_data['案件説明']
        self.logger.debug(f'input_game_explanation: {input_game_explanation}')
        self.element.clickClearJsInput(by=self.sell_info['SELL_EXPLANATION_INPUT_BY'], value=self.sell_info['SELL_EXPLANATION_INPUT_VALUE'], inputText=input_game_explanation)
        self._random_sleep()


# ----------------------------------------------------------------------------------
# 買い主へ初回自動表示するメッセージ

    @deco.funcBase
    def _input_first_msg(self, sell_data: Dict):
        input_first_msg = sell_data['買い主へ初回自動表示するメッセージ']
        if not input_first_msg:
            self.logger.warning(f'「買い主へ初回自動表示するメッセージ」入力なし: {input_first_msg}')
            self._random_sleep()
            return

        self.logger.debug(f'input_first_msg: {input_first_msg}')
        self.element.clickClearJsInput(by=self.sell_info['FIRST_MSG_BY'], value=self.sell_info['FIRST_MSG_VALUE'], inputText=input_first_msg)
        self._random_sleep()


# ----------------------------------------------------------------------------------
# 案件の登録を通知

    @deco.funcBase
    def _user_notify(self, sell_data: Dict):
        input_sell_notify = sell_data['案件の登録を通知']
        if not input_sell_notify:
            self.logger.warning(f'「案件の登録を通知」入力なし: {input_sell_notify}')
            return

        self.logger.debug(f'input_sell_notify: {input_sell_notify}')
        self.element.clickClearJsInput(value=self.sell_info['USER_NOTIFY'], inputText=input_sell_notify)
        self._random_sleep()


# ----------------------------------------------------------------------------------
# 商品価格

    @deco.funcBase
    def _input_price(self, sell_data: Dict):
        input_price = sell_data['売却価格']
        self.logger.debug(f'input_price: {input_price}')
        self.element.clickClearJsInput(value=self.sell_info['PRICE_VALUE'], inputText=input_price)
        self._random_sleep(min_num=3, max_num=5)


# ----------------------------------------------------------------------------------
# 暗証番号をクリックして入力

    def _click_input_pin(self):
        self.element.clickElement(value=self.sell_info['PIN_CHECK_CLICK_VALUE'])
        self._random_sleep()

        # 暗証番号を入力
        input_pin= self.sell_info['PIN_INPUT_VALUE']
        self.logger.debug(f'input_pin: {input_pin}')
        self.element.clickClearJsInput(by=self.sell_info['PIN_INPUT_AREA_BY'], value=self.sell_info['PIN_INPUT_AREA_VALUE'], inputText=input_pin)
        self._random_sleep()

# ----------------------------------------------------------------------------------
# 確認するをクリック

    @deco.funcBase
    def _check_click(self):
        self.element.clickElement(value=self.sell_info['CHECK_VALUE'])
        self._random_sleep()


# ----------------------------------------------------------------------------------
# 出品するをクリック

    @deco.funcBase
    def _click_end_sell_btn(self):
        self.element.clickElement(value=self.sell_info['SELL_BTN'])
        self._random_sleep(min_num=5, max_num=15)


# ----------------------------------------------------------------------------------
# POPを消す

    def _delete_popup_click(self):
        self.element.clickElement(value=self.sell_info['POPUP_DELETE_BTN_VALUE'])
        self._random_sleep()


# ----------------------------------------------------------------------------------
# ランダムSleep

    def _random_sleep(self, min_num: int = 1, max_num: int = 3):
        self.random_sleep._random_sleep(min_num=min_num, max_num=max_num)


# ----------------------------------------------------------------------------------
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# テスト実施

if __name__ == "__main__":
    worksheet_name = LoginInfo.SITE_PATTERNS.value["MA_CLUB"]["SITE_NAME"]
    id_text = LoginInfo.SITE_PATTERNS.value["MA_CLUB"]["ID_TEXT"]
    pass_text = LoginInfo.SITE_PATTERNS.value["MA_CLUB"]["PASS_TEXT"]
    print(
        f"worksheet_name: {worksheet_name}\nid_text: {id_text}\npass_text: {pass_text}"
    )

    test_flow = FlowMAClubNewItem()
    asyncio.run(
        test_flow.process(
            worksheet_name=worksheet_name, id_text=id_text, pass_text=pass_text
        )
    )
