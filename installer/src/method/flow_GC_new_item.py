# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# export PYTHONPATH="/Users/nyanyacyan/Desktop/project_file/domain_search/installer/src"


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import os, time, asyncio
from typing import Dict, List
import pandas as pd


# 自作モジュール
from base.utils import Logger
from base.chrome import ChromeManager
from base.loginWithId import SingleSiteIDLogin
from base.seleniumBase import SeleniumBasicOperations
from base.spreadsheetRead import GetDataGSSAPI
from base.elementManager import ElementManager

# const
from const_element import LoginInfo, GssInfo, SellInfo

# ----------------------------------------------------------------------------------
# **********************************************************************************
# 一連の流れ

class FlowGCNewItem:
    def __init__(self, debugMode=True):

        # logger
        self.getLogger = Logger(__name__, debugMode=debugMode)
        self.logger = self.getLogger.getLogger()

        # chrome
        self.chromeManager = ChromeManager(debugMode=debugMode)
        self.chrome = self.chromeManager.flowSetupChrome()


        # インスタンス
        self.login = SingleSiteIDLogin(chrome=self.chrome, debugMode=debugMode)
        self.random_sleep = SeleniumBasicOperations(chrome=self.chrome, debugMode=debugMode)
        self.gss_read = GetDataGSSAPI(debugMode=debugMode)
        self.element = ElementManager(chrome=self.chrome, debugMode=debugMode)

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
            self.row_process(login_info=login_info, sell_data=sell_data, sell_info=sell_info)

            self.logger.info(f'{i + 1}/{df_row_num} 目の処理 終了')

        self.logger.info(f"{login_info['site_name']}すべての処理完了: {sell_data['管理コード']}")


# ----------------------------------------------------------------------------------


    def row_process(self, login_info: Dict, sell_data: Dict, sell_info: Dict):
        # IDログイン
        self.login.flowLoginID(login_info=login_info, timeout=120)

        # 出品処理
        self.sell_process(sell_data=sell_data, sell_info=sell_info)


# ----------------------------------------------------------------------------------


    def sell_process(self, sell_data: Dict, sell_info: Dict):
        # 出品ボタンをクリック
        self.element.clickElement(value=sell_info['SELL_BTN'])

        # 画像添付
        self.element.files_input(by=sell_info['FILE_INPUT_BY'], value=sell_info['FILE_INPUT_VALUE'], check_by=sell_info['CHECK_BY'], check_value=sell_info['CHECK_VALUE'], file_path_list=sell_data[])

        # ゲームタイトルクリック
        self.element.clickElement(value=sell_info['TITLE_CLICK_VALUE'])
        self.random_sleep

        # POPUPタイトル入力
        input_game_title = sell_data['ゲームタイトル']
        self.logger.debug(f'input_game_title: {input_game_title}')
        self.element.clickClearInput(value=sell_info['GAME_TITLE_INPUT_VALUE'], inputText=input_game_title)
        self.random_sleep

        # タイトルを選択
        # TODO ゲームタイトルを'name'にいれる
        self.element.clickElement(value=sell_info['GAME_TITLE_SELECT_VALUE'])
        self.random_sleep

        # カテゴリ選択
        self.element.clickElement(value=sell_info['CATEGORY_SELECT_VALUE'])
        self.random_sleep

        # 出品タイトル
        input_sell_title = sell_data['出品タイトル']
        self.logger.debug(f'input_sell_title: {input_sell_title}')
        self.element.clickClearInput(value=sell_info['SELL_TITLE_INPUT_VALUE'], inputText=input_sell_title)
        self.random_sleep

        # 商品説明
        input_game_explanation = sell_data['商品説明']
        self.logger.debug(f'input_game_explanation: {input_game_explanation}')
        self.element.clickClearInput(value=sell_info['SELL_EXPLANATION_INPUT_VALUE'], inputText=input_game_explanation)
        self.random_sleep

        # 課金総額
        input_game_explanation = sell_data['商品説明']
        self.logger.debug(f'input_game_explanation: {input_game_explanation}')
        self.element.clickClearInput(value=sell_info['SELL_EXPLANATION_INPUT_VALUE'], inputText=input_game_explanation)
        self.random_sleep

        # 買い手への初回msg
        input_first_msg = sell_data['初回メッセージ']
        self.logger.debug(f'input_first_msg: {input_first_msg}')
        self.element.clickClearInput(value=sell_info['FIRST_MSG_VALUE'], inputText=input_first_msg)
        self.random_sleep

        # 出品を通知
        input_game_explanation = sell_data['商品価格']
        self.logger.debug(f'input_game_explanation: {input_game_explanation}')
        self.element.clickClearInput(value=sell_info['SELL_EXPLANATION_INPUT_VALUE'], inputText=input_game_explanation)
        self.random_sleep

        # 出品方法
        select_sell_method = sell_data['出品方法']
        # TODO 出品方法から得た値を受け取って選択する
        if select_sell_method == 'タイムセール':
            self.element.clickElement(value=sell_info['SELL_METHOD_TIME_SALE_VALUE'])
        else:
            self.element.clickElement(value=sell_info['SELL_METHOD_FURIMA_VALUE'])
        self.random_sleep

        # 商品価格
        input_price = sell_data['商品価格']
        self.logger.debug(f'input_price: {input_price}')
        self.element.clickClearInput(value=sell_info['PRICE_VALUE'], inputText=input_price)
        self.random_sleep

        # 確認する
        self.element.clickElement(value=sell_info['CHECK_VALUE'])
        self.random_sleep



# ----------------------------------------------------------------------------------
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# テスト実施

if __name__ == '__main__':
    gss_info = GssInfo.GAME_CLUB.value
    login_info = LoginInfo.SITE_PATTERNS.value['GAME_CLUB']
    Sell_info = SellInfo.GAME_CLUB.value
    print(f"login_info: {login_info}")
    test_flow = FlowGCNewItem()
    asyncio.run(test_flow.process(gss_info=gss_info, login_info=login_info, sell_info=Sell_info))
