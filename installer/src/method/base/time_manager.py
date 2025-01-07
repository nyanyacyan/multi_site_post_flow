# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import time, random
from typing import Dict, Callable
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
    # カウントダウン（コールバック関数にてmsgを受け取る）

    def _countdown_timer(self, wait_seconds: int, update_callback: Callable):
        while wait_seconds > 0:
            minutes, seconds = divmod(wait_seconds, 60)

            if minutes > 0:
                msg = f"実行開始まで {minutes} 分 {seconds} 秒"
            else:
                msg = f"実行開始まで {seconds} 秒"

            update_callback(msg)

            time.sleep(1)

            wait_seconds -= 1


    # ----------------------------------------------------------------------------------
