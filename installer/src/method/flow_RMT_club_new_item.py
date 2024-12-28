# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# export PYTHONPATH="/Users/nyanyacyan/Desktop/project_file/domain_search/installer/src"


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import asyncio
from typing import Dict
from selenium.webdriver.common.keys import Keys

# 自作モジュール
from base.utils import Logger
from base.chrome import ChromeManager
from base.loginWithId import SingleSiteIDLogin
from base.seleniumBase import SeleniumBasicOperations
from base.spreadsheetRead import GetDataGSSAPI
from base.elementManager import ElementManager
from base.popup import Popup
from base.decorators import Decorators

# const
from const_element import LoginInfo, GssInfo, SellInfo

deco = Decorators()

# ----------------------------------------------------------------------------------
# **********************************************************************************
# 一連の流れ

class FlowRMTClubNewItem:
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
        self.element = ElementManager(chrome=self.chrome)
        self.popup = Popup()

        # ランダム待機
        self.random_sleep = self.random_sleep._random_sleep()

        # 必要info
        self.gss_info = GssInfo.RMT_CLUB.value
        self.login_info = LoginInfo.SITE_PATTERNS.value['RMT_CLUB']
        self.sell_info = SellInfo.RMT_CLUB.value


####################################################################################
# ----------------------------------------------------------------------------------
#todo 各メソッドをまとめる

    async def process(self):
        # スプシの読み込み（辞書でoutput）
        df = self.gss_read.getDataFrameFromGss(gss_info=self.gss_info)

        # dfの中からチェックがあるものだけ抽出
        process_df = df[df['チェック'] == 'TRUE'].reset_index(drop=True)
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

            self.row_process(sell_data=sell_data)

            self.logger.info(f'{i + 1}/{df_row_num} 目の処理 END')

        self.logger.info(f"{self.login_info['site_name']}すべての処理完了: {sell_data['管理コード']}")


# ----------------------------------------------------------------------------------
# ログイン〜出品処理

    @deco.funcBase
    def row_process(self, sell_data: Dict):
        # IDログイン
        self.login.flowLoginID(login_info=self.login_info, timeout=120)

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
        self._sell_btn_click()

        # マイページへ戻る
        self._my_page_click()


# ----------------------------------------------------------------------------------
# 出品ボタンをクリック

    def _sell_btn_click(self):
        self.element.clickElement(value=self.sell_info['SELL_BTN'], wait_by=)


# ----------------------------------------------------------------------------------
# 売りたいをクリック

    def _sell_select_btn_click(self):
        self.element.clickElement(value=self.sell_info['SELL_SELECT_BTN'])


# ----------------------------------------------------------------------------------
# ゲームタイトル入力
# EnterKeyが必要かも→アカウント種別などが変わる

    def _input_game_title(self, sell_data: Dict):
        input_game_title = sell_data['ゲームタイトル']
        self.logger.debug(f'input_game_title: {input_game_title}')
        element = self.element.clickClearInput(value=self.sell_info['GAME_TITLE_INPUT_VALUE'], inputText=input_game_title)
        element.send_keys(Keys.RETURN)


# ----------------------------------------------------------------------------------
# カテゴリ選択

    def _category_select(self, sell_data: Dict):
        if sell_data['カテゴリ'] == 'アイテム・通貨':
            element = self.element.clickElement(value=self.sell_info['CATEGORY_ITEM_SELECT_VALUE'])
            self.logger.debug(f'「アイテム・通貨」を選択: {element}')
            self.random_sleep
        elif sell_data['カテゴリ'] == 'リセマラ':
            element = self.element.clickElement(value=self.sell_info['CATEGORY_ITEM_SELECT_VALUE'])
            self.logger.debug(f'「リセマラ」を選択: {element}')
            self.random_sleep
        elif sell_data['カテゴリ'] == '代行':
            element = self.element.clickElement(value=self.sell_info['CATEGORY_DAIKO_SELECT_VALUE'])
            self.logger.debug(f'「代行」を選択: {element}')
            self.random_sleep
        else:
            element = self.element.clickElement(value=self.sell_info['CATEGORY_ACCOUNT_SELECT_VALUE'])
            self.logger.debug(f'「アカウント」を選択: {element}')
            self.random_sleep


# ----------------------------------------------------------------------------------
# 掲載タイトルの入力

    def _input_comment_title(self, sell_data: Dict):
        input_comment_title = sell_data['掲載タイトル']
        self.logger.debug(f'input_comment_title: {input_comment_title}')
        self.element.clickClearInput(by=self.sell_info['COMMENT_TITLE_BY'], value=self.sell_info['COMMENT_TITLE_VALUE'], inputText=input_comment_title)
        self.random_sleep


# ----------------------------------------------------------------------------------
# タグ欄への入力

    def _input_tag(self, sell_data: Dict):
        input_tag = sell_data['タグ']
        if not input_tag:
            self.logger.warning(f'「タグ」入力なし: {input_tag}')
            return

        self.logger.debug(f'input_tag: {input_tag}')
        self.element.clickClearInput(by=self.sell_info['TAG_BY'], value=self.sell_info['TAG_VALUE'], inputText=input_tag)
        self.random_sleep


# ----------------------------------------------------------------------------------
# 詳細内容の入力

    def _input_sell_explanation(self, sell_data: Dict):
        input_sell_explanation = sell_data['詳細内容']
        self.logger.debug(f'input_sell_explanation: {input_sell_explanation}')
        self.element.clickClearInput(by=self.sell_info['SELL_EXPLANATION_INPUT_BY'], value=self.sell_info['SELL_EXPLANATION_INPUT_VALUE'], inputText=input_sell_explanation)
        self.random_sleep


# ----------------------------------------------------------------------------------
# 画像添付

    def _photo_files_input(self, sell_data: Dict):
        file_path_list = self.element._get_all_files_path_list(subDirName=self.sell_info['INPUT_PHOTO_FOLDER_NAME'], subSubDirName=sell_data['画像フォルダ'])
        self.element.files_input(by=self.sell_info['FILE_INPUT_BY'], value=self.sell_info['FILE_INPUT_VALUE'], check_by=self.sell_info['CHECK_BY'], check_value=self.sell_info['CHECK_VALUE'], file_path_list=file_path_list)


# ----------------------------------------------------------------------------------
# 「ユーザーに出品を通知」に入力

    def _user_notify(self, sell_data: Dict):
        user_notify = sell_data['ユーザーに出品を通知する']
        if not user_notify:
            self.logger.warning(f'「ユーザーに出品を通知する」入力なし: {user_notify}')
            return

        self.logger.debug(f'user_notify: {user_notify}')
        self.element.clickClearInput(by=self.sell_info['USER_NOTIFY_BY'], value=self.sell_info['USER_NOTIFY_VALUE'], inputText=user_notify)
        self.random_sleep


# ----------------------------------------------------------------------------------
# 取引価格

    def _input_price(self, sell_data: Dict):
        input_price = sell_data['取引価格']
        self.logger.debug(f'input_price: {input_price}')
        self.element.clickClearInput(by=self.sell_info['PRICE_BY'], value=self.sell_info['PRICE_VALUE'], inputText=input_price)
        self.random_sleep


# ----------------------------------------------------------------------------------
# 確認するをクリック

    def _click_check(self):
        self.element.clickElement(value=self.sell_info['CHECK_VALUE'])
        self.random_sleep


# ----------------------------------------------------------------------------------
# 「同意する」にレ点

    def _click_agree(self):
        self.element.clickElement(value=self.sell_info['AGREE_VALUE'])
        self.random_sleep


# ----------------------------------------------------------------------------------
# 出品するをクリック

    def _click_sell_btn(self):
        self.element.clickElement(value=self.sell_info['SELL_BTN'])
        self.random_sleep


# ----------------------------------------------------------------------------------
# マイページへ戻る

    def _my_page_click(self):
        self.element.clickElement(value=self.sell_info['MY_PAGE_VALUE'])
        self.random_sleep


# ----------------------------------------------------------------------------------
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# テスト実施

if __name__ == '__main__':
    test_flow = FlowRMTClubNewItem()
    asyncio.run(test_flow.process())
