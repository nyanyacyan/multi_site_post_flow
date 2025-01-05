# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import time, random
from typing import Dict
from selenium.webdriver.chrome.webdriver import WebDriver
from datetime import datetime


# 自作モジュール
from .utils import Logger


# const




# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************


class TimeManager:
    def __init__(self):
        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()


        self.now = datetime.now()


    # ----------------------------------------------------------------------------------
    # ランダムな待機

    def _random_sleep(self, random_info: Dict):
        time.sleep(random.uniform(random_info['min'], random_info['max']))


    # ----------------------------------------------------------------------------------
