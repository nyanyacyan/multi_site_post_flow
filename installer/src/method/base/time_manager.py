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
    # 現在の時間から指定時間の差分を出して待機時間を割出す

    def _start_wait_for_time(self, start_wait_time_info: Dict) -> float:
        # 指定時間を構成
        target_time = datetime(year=start_wait_time_info['year'], month=start_wait_time_info['month'], day=start_wait_time_info['day'], hour=start_wait_time_info['hour'], minute=start_wait_time_info['minute'])
        # 待機時間
        wait_seconds = int((target_time - self.now).total_seconds())
        self.logger.debug(f'wait_seconds: {wait_seconds}')
        return wait_seconds


    # ----------------------------------------------------------------------------------
    # ランダムな待機

    def _random_sleep(self, random_info: Dict):
        time.sleep(random.uniform(random_info['min'], random_info['max']))


    # ----------------------------------------------------------------------------------
