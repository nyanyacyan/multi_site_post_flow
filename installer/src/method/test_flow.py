# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# export PYTHONPATH="/Users/nyanyacyan/Desktop/project_file/multi_site_post_flow/installer/src"

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import base64, cv2, re
from pytesseract import image_to_string

# 自作モジュール
# from base.utils import Logger
from base.chrome import ChromeManager
from base.loginWithId import SingleSiteIDLogin
from base.seleniumBase import SeleniumBasicOperations
from base.elementManager import ElementManager
from base.time_manager import TimeManager

# const


# ----------------------------------------------------------------------------------
# **********************************************************************************
# 一連の流れ


class TestFlow:
    def __init__(self):
        # logger
        # self.getLogger = Logger()
        # self.logger = self.getLogger.getLogger()

        # chrome
        self.chromeManager = ChromeManager()
        self.chrome = self.chromeManager.flowSetupChrome()

        # インスタンス
        self.login = SingleSiteIDLogin(chrome=self.chrome)
        self.random_sleep = SeleniumBasicOperations(chrome=self.chrome)
        self.element = ElementManager(chrome=self.chrome)
        self.time_manager = TimeManager()
        self.selenium = SeleniumBasicOperations(chrome=self.chrome)
        # self.path = BaseToPath()

    ####################################################################################


    def _test_photo_data(self, url: str):
        # スプシにアクセス（Worksheet指定）

        # A欄の取得

        # B欄の取得

        # C欄の取得

        # E欄の取得

        # ページを開く
        self.chrome.get(url)

        # A欄のカテゴリにアクセス

        # B欄のカテゴリにアクセス

        # C欄のカテゴリにアクセス

        # 1位のURLを取得

        # 2位のURLを取得

        # 3位のURLを取得

        # 各ページの全体ランクを取得するMethod

        # 1〜3位までの全体ランキングを並列して行う値を取得

        # スプシに書込する


if __name__ == '__main__':

    url = "https://www.1-chome.com/elec"
    test_flow = TestFlow()
    test_flow._test_photo_data(url=url)
