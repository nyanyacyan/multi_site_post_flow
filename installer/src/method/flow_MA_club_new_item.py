# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# export PYTHONPATH="/Users/nyanyacyan/Desktop/project_file/domain_search/installer/src"


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import asyncio
from typing import Dict


# 自作モジュール
from base.utils import Logger
from base.chrome import ChromeManager
from base.loginWithId import SingleSiteIDLogin
from base.seleniumBase import SeleniumBasicOperations
from base.spreadsheetRead import GetDataGSSAPI
from base.elementManager import ElementManager
from base.decorators import Decorators

# const
from const_element import LoginInfo, GssInfo, SellInfo

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

        # ランダム待機
        self.random_sleep = self.random_sleep._random_sleep()


####################################################################################
# ----------------------------------------------------------------------------------
#todo 各メソッドをまとめる

    async def process(self, gss_info: Dict, login_info: Dict, sell_info: Dict):
        # スプシの読み込み（辞書でoutput）
        df = self.gss_read.getDataFrameFromGss(gss_info=gss_info)

        # dfの中からチェックがあるものだけ抽出
        process_df = df[df['チェック'] == 'TRUE']
        df_row_num = len(process_df)
        df_columns = process_df.shape[1]
        self.logger.debug(process_df.head)
        self.logger.debug(f"スプシの全行数: {df_row_num}行\nスプシの全column数: {df_columns}")

        # 各行に対して処理を行う
        for i, row in process_df.iterrows():
            self.logger.info(f'{i + 1}/{df_row_num} 目の処理 開始')

            # rowの情報を辞書化
            sell_data = row.to_dict()
            self.logger.debug(f'sell_data: {sell_data}')

            self.logger.info(f"{i + 1}/{df_row_num} タイトル: {sell_data['ゲームタイトル']}")
            self.logger.info(f"{i + 1}/{df_row_num} タイトル: {sell_data['出品タイトル']}")
            self.logger.info(f"{i + 1}/{df_row_num} タイトル: {sell_data['商品説明']}")
            self.logger.info(f"{i + 1}/{df_row_num} タイトル: {sell_data['商品価格']}")


            # ログイン〜処理実施まで
            self.logger.info(f'{i + 1}/{df_row_num} 目の処理 START')

            self.row_process(login_info=login_info, sell_data=sell_data, sell_info=sell_info)

            self.logger.info(f'{i + 1}/{df_row_num} 目の処理 END')

        self.logger.info(f"{login_info['site_name']}すべての処理完了: {sell_data['管理コード']}")


# ----------------------------------------------------------------------------------
# ログイン〜出品処理

    @deco.funcBase
    def row_process(self, login_info: Dict, sell_data: Dict, sell_info: Dict):
        # IDログイン
        self.login.flowLoginID(login_info=login_info, timeout=120)

        # 出品処理
        self.sell_process(sell_data=sell_data, sell_info=sell_info)


# ----------------------------------------------------------------------------------
# 出品処理

    def sell_process(self, sell_data: Dict, sell_info: Dict):
        # 出品ボタンをクリック
        self._sell_btn_click(sell_info)

        # 画像添付
        self._photo_files_input(sell_data, sell_info)

        # 案件カテゴリ欄をクリック
        self._title_click(sell_info=sell_info)

        # POPUPタイトル入力
        self._popup_title_input(sell_info=sell_info)

        # 種別を選択
        self._category_select(sell_data=sell_data, sell_info=sell_info)

        # 案件タイトル
        self._input_sell_title(sell_data=sell_data, sell_info=sell_info)

        # 案件説明
        self._input_game_explanation(sell_data=sell_data, sell_info=sell_info)

        # 課金総額
        # self._input_charge(sell_data=sell_data, sell_info=sell_info)

        # 買い手への初回msg
        self._input_first_msg(sell_data=sell_data, sell_info=sell_info)

        # 案件の登録を通知
        # self._input_sell_notify(sell_data=sell_data, sell_info=sell_info)

        # 商品価格
        self._input_price(sell_data=sell_data, sell_info=sell_info)

        # 確認するをクリック
        self._check_click(sell_info=sell_info)

        # 売却登録するをクリック
        self._sell_btn_click(sell_info=sell_info)

        # POPを消す
        self._delete_popup_click(sell_info=sell_info)

        # マイページへ戻る
        self._my_page_click(sell_info=sell_info)


# ----------------------------------------------------------------------------------
# 出品ボタンをクリック

    def _sell_btn_click(self, sell_info: Dict):
        self.element.clickElement(value=sell_info['SELL_BTN'])


# ----------------------------------------------------------------------------------
# 画像添付

    def _photo_files_input(self, sell_data: Dict, sell_info: Dict):
        file_path_list = self.element._get_all_files_path_list(subDirName=sell_info['INPUT_PHOTO_FOLDER_NAME'], subSubDirName=sell_data['画像フォルダ'])
        self.element.files_input(by=sell_info['FILE_INPUT_BY'], value=sell_info['FILE_INPUT_VALUE'], check_by=sell_info['CHECK_BY'], check_value=sell_info['CHECK_VALUE'], file_path_list=file_path_list)


# ----------------------------------------------------------------------------------
# ゲームタイトルクリック

    def _title_click(self, sell_info: Dict):

        self.element.clickElement(value=sell_info['TITLE_CLICK_VALUE'])
        self.random_sleep


# ----------------------------------------------------------------------------------
# POPUPに案件タイトル入力

    def _popup_title_input(self, sell_data: Dict, sell_info: Dict):
        input_game_title = sell_data['案件タイトル']
        self.logger.debug(f'input_game_title: {input_game_title}')
        self.element.clickClearInput(value=sell_info['GAME_TITLE_INPUT_VALUE'], inputText=input_game_title)
        self.random_sleep


# ----------------------------------------------------------------------------------
# 案件タイトルを選択

    def _game_title_select(self, sell_data: Dict, sell_info: Dict):
        game_title = sell_data['案件タイトル']
        game_title_path = sell_info['GAME_TITLE_SELECT_VALUE'].format(game_title)
        self.logger.debug(f'game_title_path: {game_title_path}')
        self.element.clickElement(value=game_title_path)
        self.random_sleep


# ----------------------------------------------------------------------------------
# カテゴリ選択

    def _category_select(self, sell_data: Dict, sell_info: Dict):
        if sell_data['カテゴリ'] == 'その他':
            element = self.element.clickElement(value=sell_info['CATEGORY_OTHER_SELECT_VALUE'])
            self.logger.debug(f'「その他」を選択: {element}')
            self.random_sleep

        else:
            element = self.element.clickElement(value=sell_info['CATEGORY_JYOTO_SELECT_VALUE'])
            self.logger.debug(f'「アカウント譲渡」を選択: {element}')
            self.random_sleep


# ----------------------------------------------------------------------------------
# 出品タイトル

    def _input_sell_title(self, sell_data: Dict, sell_info: Dict):
        input_sell_title = sell_data['出品タイトル']
        self.logger.debug(f'input_sell_title: {input_sell_title}')
        self.element.clickClearInput(by=sell_info['SELL_TITLE_INPUT_BY'], value=sell_info['SELL_TITLE_INPUT_VALUE'], inputText=input_sell_title)
        self.random_sleep


# ----------------------------------------------------------------------------------
# 商品説明

    def _input_game_explanation(self, sell_data: Dict, sell_info: Dict):
        input_game_explanation = sell_data['商品説明']
        self.logger.debug(f'input_game_explanation: {input_game_explanation}')
        self.element.clickClearInput(by=sell_info['SELL_EXPLANATION_INPUT_BY'], value=sell_info['SELL_EXPLANATION_INPUT_VALUE'], inputText=input_game_explanation)
        self.random_sleep


# ----------------------------------------------------------------------------------
# 課金総額
#! 使わない

    def _input_charge(self, sell_data: Dict, sell_info: Dict):
        input_charge = sell_data['課金総額']
        self.logger.debug(f'input_game_explanation: {input_charge}')
        self.element.clickClearInput(value=sell_info['CHARGE_VALUE'], inputText=input_charge)
        self.random_sleep


# ----------------------------------------------------------------------------------
# 買い手への初回msg

    def _input_first_msg(self, sell_data: Dict, sell_info: Dict):
        input_first_msg = sell_data['初回メッセージ']
        self.logger.debug(f'input_first_msg: {input_first_msg}')
        self.element.clickClearInput(by=sell_info['FIRST_MSG_BY'], value=sell_info['FIRST_MSG_VALUE'], inputText=input_first_msg)
        self.random_sleep


# ----------------------------------------------------------------------------------
# 案件の登録を通知

    def _input_sell_notify(self, sell_data: Dict, sell_info: Dict):
        input_sell_notify = sell_data['出品を通知']
        self.logger.debug(f'input_sell_notify: {input_sell_notify}')
        self.element.clickClearInput(value=sell_info['CHARGE_VALUE'], inputText=input_sell_notify)
        self.random_sleep


# ----------------------------------------------------------------------------------
# 出品方法
#! 使わない

    def _select_sell_method(self, sell_data: Dict, sell_info: Dict):
        select_sell_method = sell_data['出品方法']
        # TODO 出品方法から得た値を受け取って選択する
        if select_sell_method == 'タイムセール':
            self.element.clickElement(value=sell_info['SELL_METHOD_TIME_SALE_VALUE'])
        else:
            self.element.clickElement(value=sell_info['SELL_METHOD_FURIMA_VALUE'])
        self.random_sleep


# ----------------------------------------------------------------------------------
# 商品価格

    def _input_price(self, sell_data: Dict, sell_info: Dict):
        input_price = sell_data['商品価格']
        self.logger.debug(f'input_price: {input_price}')
        self.element.clickClearInput(value=sell_info['PRICE_VALUE'], inputText=input_price)
        self.random_sleep


# ----------------------------------------------------------------------------------
# 確認するをクリック

    def _check_click(self, sell_info: Dict):
        self.element.clickElement(value=sell_info['CHECK_VALUE'])
        self.random_sleep


# ----------------------------------------------------------------------------------
# 出品するをクリック

    def _sell_btn_click(self, sell_info: Dict):
        self.element.clickElement(value=sell_info['SELL_BTN'])
        self.random_sleep


# ----------------------------------------------------------------------------------
# POPを消す

    def _delete_popup_click(self, sell_info: Dict):
        self.element.clickElement(value=sell_info['POPUP_DELETE_BTN_VALUE'])
        self.random_sleep


# ----------------------------------------------------------------------------------
# マイページへ戻る

    def _my_page_click(self, sell_info: Dict):
        self.element.clickElement(value=sell_info['MY_PAGE_VALUE'])
        self.random_sleep


# ----------------------------------------------------------------------------------
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# テスト実施

if __name__ == '__main__':
    gss_info = GssInfo.MA_CLUB.value
    login_info = LoginInfo.SITE_PATTERNS.value['MA_CLUB']
    sell_info = SellInfo.MA_CLUB.value
    print(f"login_info: {login_info}")

    test_flow = FlowMAClubNewItem()
    asyncio.run(test_flow.process(gss_info=gss_info, login_info=login_info, sell_info=sell_info))
