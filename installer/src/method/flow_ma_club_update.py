# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# export PYTHONPATH="/Users/nyanyacyan/Desktop/project_file/domain_search/installer/src"


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
from typing import List
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.webdriver import WebDriver


# 自作モジュール
from method.base.utils import Logger
from method.base.chrome import ChromeManager
from method.base.loginWithId import SingleSiteIDLogin
from method.base.seleniumBase import SeleniumBasicOperations
from method.base.elementManager import ElementManager
from method.base.decorators import Decorators
from method.base.time_manager import TimeManager
from method.base.jumpTargetPage import JumpTargetPage

# const
from method.const_element import LoginInfo, UpdateInfo

deco = Decorators()

# ----------------------------------------------------------------------------------
# **********************************************************************************
# 一連の流れ

class FlowMAClubUpdate:
    def __init__(self):
        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()


        # 必要info
        self.login_info = LoginInfo.SITE_PATTERNS.value["MA_CLUB"]
        self.update_info = UpdateInfo.MA_CLUB.value


    ####################################################################################
    # ----------------------------------------------------------------------------------
    # アップロードプロセス

    @deco.funcBase
    def process(self, id_text: str, pass_text: str):

        # chrome
        chromeManager = ChromeManager()
        chrome = chromeManager.flowSetupChrome()

        # インスタンス
        self.login = SingleSiteIDLogin(chrome=chrome)
        self.random_sleep = SeleniumBasicOperations(chrome=chrome)
        self.element = ElementManager(chrome=chrome)
        self.time_manager = TimeManager()
        self.jump_target_page = JumpTargetPage(chrome=chrome)

        # idログイン
        self._id_login(id_text=id_text, pass_text=pass_text)

        # ウォッチリストへ移動
        self._click_watch_list_btn()

        # 出品中になっているリンクをすべて取得（上限あり）
        link_list = self._get_title_link()

        # すべてのリンク先にジャンプして更新を実行
        self._update_all_process(link_list=link_list, max_num=5, chrome=chrome)

        self._random_sleep()


    # ----------------------------------------------------------------------------------
    # idログイン

    def _id_login(self, id_text: str, pass_text: str):
        self.login._flow_recapcha_handle_id_login( login_info=self.login_info, id_text=id_text, pass_text=pass_text, timeout=120, )


    # ----------------------------------------------------------------------------------
    # ウォッチリストをクリック

    def _click_watch_list_btn(self):
        value = self.update_info["WATCH_LIST_VALUE"]
        self.logger.debug(f"value: {value}")
        self.element.clickElement(value=value)
        self._random_sleep()


    # ----------------------------------------------------------------------------------
    # すべてリンクを取得

    def _get_title_link(self, max_update: int=5):
        all_title_link = []

        while len(all_title_link) < max_update:
            # if all_title_link:
            #     self._get_next_page()

            # 一度出品中のある要素に絞り込みをする。
            item_rows = self.element.getElements(by=self.update_info['ITEM_ROWS_BY'], value=self.update_info['ITEM_ROWS_VALUE'])
            self.logger.debug(f'item_rows: {item_rows}')

            if item_rows:
                for item_row in item_rows:
                    status_element = self.element.filterElements(parentElement=item_row, by=self.update_info["ITEM_ROW_BY"], value=self.update_info["ITEM_ROW_VALUE"])
                    self.logger.debug(f'status_element: {status_element}')
                    active_status = any(status.text == '出品中' for status in status_element)
                    self.logger.debug(f'active_status: {active_status}')

                    if active_status:
                        link_element = self.element.filterElement(parentElement=item_row, by=self.update_info["TITLE_LINK_BY"], value=self.update_info["TITLE_LINK_VALUE"])
                        self.logger.debug(f'link_element: {link_element}')
                        element_link = link_element.get_attribute('href')
                        self.logger.debug(f'element_link: {element_link}')
                        all_title_link.append(element_link)

            else:
                comment = f'【更新処理スキップ】ウォッチリストに登録されているものがありません'
                self.logger.info(comment)
                self._random_sleep()
                break

        self.logger.info(f'すべてのアップデート情報の取得を行いました\n{all_title_link}')
        return all_title_link

    # ----------------------------------------------------------------------------------
    # 次のページへ移行

    def _get_next_page(self):
        value = self.update_info["NEXT_BTN_VALUE"]
        self.logger.debug(f"value: {value}")
        self.element.clickElement(value=value)
        self._random_sleep()

    # ----------------------------------------------------------------------------------
    # 課金されている場合

    def _charge_update_process(self):
        try:
            value = self.update_info["CHARGE_UPDATE_BTN_VALUE"]
            charge_element = self.element.getElement(value=value)
            if charge_element:
                self.logger.info(f'課金されているPOPUPを発見: {charge_element}')
                self.element._click_only(web_element=charge_element)
                self._random_sleep()

        except NoSuchElementException:
            self.logger.info(f'課金のPOPUPはありませんでした。')


    # ----------------------------------------------------------------------------------
    # リンク先にジャンプして更新ボタンを押下

    def _update_process(self, targetUrl: str):
        self.jump_target_page.flowJumpTargetPage(targetUrl=targetUrl)
        value = self.update_info["UPDATE_BTN_VALUE"]
        self.logger.debug(f"value: {value}")
        self.element.clickElement(value=value)
        self._random_sleep()

        # 課金されてる場合に出てくるPOPUPがあるか確認
        self._charge_update_process()


    # ----------------------------------------------------------------------------------
    # すべてのリンク先にアップデートプロセスを実施

    def _update_all_process(self, link_list: List, max_num: int, chrome: WebDriver):
        if link_list:
            try:
                for i, link in enumerate(link_list[:max_num]):
                    self.logger.info(f'{i +1} 個目の更新作業実施')
                    self._update_process(targetUrl=link)

                self.logger.info(f'すべての更新完了')
                return chrome.quit()

            # 更新ボタンが押せなくなった処理
            except NoSuchElementException:
                self.logger.info(f'更新の上限に達しました: 実施回数 {i + 1}回、Update実施')
                return chrome.quit()

            except Exception as e:
                self.logger.error(f"アップデート実施中になにかしらのエラー発生(止めずにそのまま処理を続行): {e}")
                return chrome.quit()

        else:
            self.logger.warning(f'【更新処理スキップ】ウォッチリストに出品中のものが登録されていません。')
            return chrome.quit()


    # ----------------------------------------------------------------------------------
    # 日時が古い順を選択

    def _select_old_datetime(self):
        value = self.update_info["ITEM_SORT_BTN_VALUE"]
        select_value = self.update_info["SELECT_VALUE"]
        self.logger.debug(f"value: {value}\nselect_value: {select_value}")
        self.element._select_element(value=value, select_value=select_value)
        self._random_sleep()


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
# テスト実施

if __name__ == "__main__":
    id_text = LoginInfo.SITE_PATTERNS.value["MA_CLUB"]["ID_TEXT"]
    pass_text = LoginInfo.SITE_PATTERNS.value["MA_CLUB"]["PASS_TEXT"]
    print(
        f"id_text: {id_text}\npass_text: {pass_text}"
    )


    test_flow = FlowMAClubUpdate()
    test_flow.process(id_text=id_text, pass_text=pass_text)
