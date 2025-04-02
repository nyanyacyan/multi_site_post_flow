# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# export PYTHONPATH="/Users/nyanyacyan/Desktop/project_file/domain_search/installer/src"

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import time
from typing import Dict
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import concurrent.futures

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
        self.time_manager = TimeManager()

    ####################################################################################
    # ----------------------------------------------------------------------------------
    # 各メソッドをまとめる

    def process(self, worksheet_name: str, gss_url: str, id_text: str, pass_text: str, interval_info: Dict):
        gss_read = GetDataGSSAPI()

        # スプシの読み込み（辞書でoutput）
        df = gss_read._get_df_in_gui(gss_info=self.gss_info, worksheet_name=worksheet_name, gss_url=gss_url)

        # dfの中からチェックがあるものだけ抽出
        process_df = df[df["チェック"] == "TRUE"].reset_index(drop=True)
        df_row_num = len(process_df)
        df_columns = process_df.shape[1]
        self.logger.debug(process_df.head)
        self.logger.debug(f"スプシの全行数: {df_row_num}行\nスプシの全column数: {df_columns}")

        # DFの各行に対して処理を行う
        for i, row in process_df.iterrows():
            chrome = None  # ✅ `chrome` を最初に `None` で定義（finally で確実に閉じるため）

            try:
                # rowの情報を辞書化
                sell_data = row.to_dict()
                self.logger.debug(f"sell_data: {sell_data}")
                self.logger.info(f"{i + 1}/{df_row_num} タイトル: {sell_data['ゲームタイトル']}")
                self.logger.info(f"{i + 1}/{df_row_num} タイトル: {sell_data['出品タイトル']}")
                self.logger.info(f"{i + 1}/{df_row_num} タイトル: {sell_data['商品説明']}")
                self.logger.info(f"{i + 1}/{df_row_num} タイトル: {sell_data['商品価格']}")
                self.logger.info(f"{i + 1}/{df_row_num} 処理開始")

                # ✅ 出品間隔時間の待機
                random_wait_time = self.time_manager._random_sleep(random_info=interval_info)
                self.logger.info(f'スプシ {i + 1}行目開始: 待機時間 {int(random_wait_time)} 秒間待機完了')

                if not i == 0:
                    time.sleep(random_wait_time)
                    self.logger.info(f" {random_wait_time} 秒間待機完了 ")

                # ✅ インスタンス
                item_processor = FlowRMTClubNewItem()

                # ✅ ログイン〜処理実施まで
                item_processor.row_process(index=i, id_text=id_text, pass_text=pass_text, sell_data=sell_data)
                self.logger.info(f"{i + 1}/{df_row_num} 処理完了")

            except SystemExit:
                self.logger.error(f"{i + 1}/{df_row_num} ⚠️ スレッドが強制終了されました。Chrome を閉じます！")
                raise  # **SystemExit は再スローしてスレッドを正常に終了させる**

            except Exception as e:
                self.logger.error(f"{i + 1}/{df_row_num} ❌ 予期しないエラーが発生: {e}")


        self.logger.info(f"すべての処理完了")

    # ----------------------------------------------------------------------------------
# **********************************************************************************
# 一連の流れ

class FlowRMTClubNewItem:
    def __init__(self):
        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()


        self.time_manager = TimeManager()

        # 必要info
        self.login_info = LoginInfo.SITE_PATTERNS.value['RMT_CLUB']
        self.sell_info = SellInfo.RMT_CLUB.value


    ####################################################################################


    def row_process(self, index: int, id_text: str, pass_text: str, sell_data: Dict, max_retry: int = 3):
        for i in range(max_retry):
            self.logger.info(f"リトライ: {i + 1}回目 出品開始")
            try:
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(self._internal_row_process, index, id_text, pass_text, sell_data)
                    future.result(timeout=300)  # タイムアウトを300秒に設定

                self.logger.info(f"{index} 回目の出品処理が成功しました")
                return  # 成功したらループを抜ける

            except concurrent.futures.TimeoutError:
                self.logger.warning(f"⚠️ 出品処理がタイムアウトしました。リトライします ({i + 1}/{max_retry})")

            except Exception as e:
                self.logger.error(f"❌ 出品処理中にエラーが発生:念の為リトライ {e}")

        self.logger.error(f'❌【処理失敗】 リトライの上限に達しました: ({i + 1}/{max_retry})')
        return

    # ----------------------------------------------------------------------------------
    # ログイン〜出品処理

    @deco.funcBase
    def _internal_row_process(self, index: int, id_text: str, pass_text: str, sell_data: Dict):
        try:
            self.logger.debug(f"row_processを開始: {index}")

            # chrome
            chrome_manager = ChromeManager()
            self.chrome = chrome_manager.flowSetupChrome()

            # インスタンス
            self.login = SingleSiteIDLogin(chrome=self.chrome)
            self.random_sleep = SeleniumBasicOperations(chrome=self.chrome)
            self.element = ElementManager(chrome=self.chrome)
            self.jump_target_page = JumpTargetPage(chrome=self.chrome)

            # idログイン
            self.login.flow_login_id_input_gui( login_info=self.login_info, id_text=id_text, pass_text=pass_text)

            # 出品処理
            self.sell_process(sell_data=sell_data)
            self.logger.info(f"出品処理を完了: {index}")

        except Exception as e:
            self.logger.error(f"出品処理中にエラーが発生: {e}")

        finally:
            # ✅ 例外が発生しても `chrome.quit()` を確実に実行
            if self.chrome is not None:
                try:
                    self.logger.info(f"🔴 Chrome を終了します")
                    self.chrome.quit()
                except Exception as e:
                    self.logger.error(f"⚠️ Chrome を閉じる際にエラー: {e}")

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
        self._random_sleep(3, 10)


# ----------------------------------------------------------------------------------
# 画像添付

    def _photo_files_input(self, sell_data: Dict):
        file_path_list = self.element._get_all_files_path_list(subDirName=self.sell_info['INPUT_PHOTO_FOLDER_NAME'], subSubDirName=sell_data['画像フォルダ'])
        self.element.files_input(value=self.sell_info['FILE_INPUT_VALUE'], file_path_list=file_path_list)
        self._random_sleep(3, 5)


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
        self._random_sleep(3, 5)


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
        self._random_sleep(2, 5)


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
    print( f"worksheet_name: {worksheet_name}\nid_text: {id_text}\npass_text: {pass_text}" )

    test_flow = FlowRMTProcess()
    test_flow.process(worksheet_name=worksheet_name, id_text=id_text, pass_text=pass_text)
