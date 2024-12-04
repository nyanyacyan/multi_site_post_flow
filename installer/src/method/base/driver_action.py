# coding: utf-8
# ----------------------------------------------------------------------------------
# 2023/4/19 更新

# ----------------------------------------------------------------------------------


import os
import time
import pyautogui
import pyperclip

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import (NoSuchElementException)

# 自作モジュール
from .utils import Logger, NoneChecker
from .driver_utils import Wait


# ----------------------------------------------------------------------------------
####################################################################################


class Action:
    def __init__(self, chrome, debug_mode=False):
        self.chrome = chrome
        self.logger = self.setup_logger(debug_mode=debug_mode)
        self.none = NoneChecker(debug_mode=debug_mode)
        self.driver_wait = Wait(chrome=self.chrome, debug_mode=debug_mode)


####################################################################################
# ----------------------------------------------------------------------------------
# Loggerセットアップ

    def setup_logger(self, debug_mode=False):
        debug_mode = os.getenv('DEBUG_MODE', 'False') == 'True'
        logger_instance = Logger(__name__, debug_mode=debug_mode)
        return logger_instance.get_logger()


# ----------------------------------------------------------------------------------
# 移動してクリックするアクション

    def click_action(self, element, x_adjust_int, y_adjust_int, field_name) -> None:
        try:
            self.logger.debug(f"*****{field_name} 操作 開始*****")
            self.logger.debug(f"{field_name} element: {element}")

            # 画面領域のサイズ
            page_size = pyautogui.size()
            self.logger.debug(f"page_size {page_size}")

            # 要素の座標  必ず正しいわけではない
            location = element.location
            self.logger.debug(f"location {location}")


            # 要素のサイズ
            size = element.size
            self.logger.debug(f"size {size}")

            # 要素の中心座標
            #! OSによって調整が必要
            element_center_x = location['x'] + size['width'] // 2+ x_adjust_int
            element_center_y = location['y'] + size['height'] // 2 + y_adjust_int


            self.logger.debug(f"element_center_x: {element_center_x}, element_center_y: {element_center_y}")

            # 現在の座標を示す
            position = pyautogui.position()
            self.logger.debug(f"現在のマウスの位置 {position}")

            # 選択した要素の中心に移動
            self.logger.debug(f"{field_name} マウスカーソルへの移動 開始")
            pyautogui.moveTo(element_center_x, element_center_y)

            time.sleep(1)

            # クリック
            pyautogui.click()

            self.logger.debug(f"*****{field_name} 操作 終了*****")

        except NoSuchElementException as e:
            self.logger.error(f"{field_name} 見つからない: {e}")


        except Exception as e:
            self.logger.error(f"{field_name} 処理中にエラーが発生: {e}")



# ----------------------------------------------------------------------------------
# ドラックアンドドロップアクション

    def drag_and_drop_action(self, element, field_name, x_adjust_int=0, y_adjust_int=0, drop_x_int=0, drop_x_adjust_int=0, drop_y_int=0, drop_y_adjust_int=0):
        try:
            self.logger.debug(f"*****{field_name} 操作 開始*****")
            self.logger.debug(f"{field_name} element: {element}")

            # 画面領域のサイズ
            page_size = pyautogui.size()
            self.logger.debug(f"page_size {page_size}")

            # 要素の座標  必ず正しいわけではない
            location = element.location
            self.logger.debug(f"location {location}")


            # 要素のサイズ
            size = element.size
            self.logger.debug(f"size {size}")

            # 要素の中心座標
            #! OSによって調整が必要
            element_center_x = location['x'] + size['width'] // 2+ x_adjust_int
            element_center_y = location['y'] + size['height'] // 2 + y_adjust_int


            self.logger.debug(f"element_center_x: {element_center_x}, element_center_y: {element_center_y}")

            # dropする座標
            #! OSによって調整が必要
            drop_x = drop_x_int + drop_x_adjust_int
            drop_y = drop_y_int + drop_y_adjust_int


            # 現在の座標を示す
            position = pyautogui.position()
            self.logger.debug(f"現在のマウスの位置 {position}")

            # 選択した要素の中心に移動
            self.logger.debug(f"{field_name} マウスカーソルへの移動 開始")
            pyautogui.moveTo(element_center_x, element_center_y)

            time.sleep(1)

            # ドラックアンドドロップ
            # 時間とクリック指定（左クリックと右クリック）
            pyautogui.dragTo(drop_x, drop_y, time=1.5, button='left')

            self.logger.debug(f"*****{field_name} 操作 終了*****")

        except NoSuchElementException as e:
            self.logger.error(f"{field_name} 見つからない: {e}")


        except Exception as e:
            self.logger.error(f"{field_name} 処理中にエラーが発生: {e}")



# ----------------------------------------------------------------------------------
# ロケーター選択→直接文字列で入れ込むことができない

    def _locator_select(self, locator) -> None:
        mapping = {
            'ID' : By.ID,
            'XPATH' : By.XPATH,
            'CLASS' : By.CLASS_NAME,
            'CSS' : By.CSS_SELECTOR,
            'TAG' : By.TAG_NAME,
            'NAME' : By.NAME,
            'LINK_TEXT': By.LINK_TEXT,  # リンクテキスト全体に一致する要素を見つける
            'PARTIAL_LINK_TEXT': By.PARTIAL_LINK_TEXT  # リンクテキストの一部に一致する要素を見つける
        }

        # 入力された文字を大文字に直して選択
        return mapping.get(locator.upper())


# ----------------------------------------------------------------------------------
# 要素を選択する関数

    def _find_element(self, by_pattern, xpath):
        element = self.chrome.find_element((self._locator_select(by_pattern), xpath))

        return element

# ----------------------------------------------------------------------------------
# tabキーを入力して入力フィールドにコピペで入力

    def tab_to_input_action(self, input_int, input_word, field_name):
        self.logger.info(f"*********** tab_to_input_action 処理 開始 ***********")

        self.logger.debug(f"{field_name} input_int: {input_int}  input_word: {input_word}")

        pyperclip.copy(input_word)

        for _ in range(input_int):
            pyautogui.press('tab')
            time.sleep(0.5)

        actions = ActionChains(self.chrome)
        actions.key_down(Keys.COMMAND).send_keys('v').key_up(Keys.COMMAND).perform()


        self.logger.info(f"*********** tab_to_input_action 処理 終了 ***********")


# ----------------------------------------------------------------------------------
# tabキーを入力してEnterKeyを入力

    def tab_to_enter_action(self, input_int, field_name):
        self.logger.info(f"*********** tab_to_enter_action 処理 開始 ***********")


        self.logger.debug(f"{field_name} input_int: {input_int}")

        for _ in range(input_int):
            pyautogui.press('tab')
            time.sleep(0.5)

        time.sleep(2)

        pyautogui.press('enter')


        self.logger.info(f"*********** tab_to_enter_action 処理 終了 ***********")


# ----------------------------------------------------------------------------------
# EnterKeyのみを入力

    def enter_action(self):
        self.logger.info(f"*********** enter_action 処理 開始 ***********")


        pyautogui.press('enter')


        self.logger.info(f"*********** enter_action 処理 終了 ***********")


# ----------------------------------------------------------------------------------
# tabキーを入力してしたあとに選択EnterKeyを入力

    def tab_input_enter_action(self, input_int, input_key, field_name):
        self.logger.info(f"*********** tab_to_enter_action 処理 開始 ***********")


        self.logger.debug(f"{field_name} input_int: {input_int}")

        for _ in range(input_int):
            pyautogui.press('tab')
            time.sleep(0.5)

        time.sleep(2)

        pyautogui.press(input_key)
        self.logger.debug(f"{field_name} input_intを入力しました。")

        time.sleep(2)

        pyautogui.press('enter')


        self.logger.info(f"*********** tab_to_enter_action 処理 終了 ***********")


# ----------------------------------------------------------------------------------