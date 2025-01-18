# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import time, re
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import Select
from datetime import datetime
from typing import Dict, Any, List, Tuple
from selenium.common.exceptions import ElementClickInterceptedException, ElementNotInteractableException, NoSuchElementException, TimeoutException

from pathlib import Path



# 自作モジュール
from .utils import Logger
from .path import BaseToPath
from .popup import Popup

from .decorators import Decorators
from .textManager import TextManager
from .driverDeco import ClickDeco
from .driverWait import Wait

# const
from ..const_str import ErrorComment

decoInstance = Decorators()


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************


class IsFileInDf:
    def __init__(self):
        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

        # インスタンス
        self.path = BaseToPath()


    # ----------------------------------------------------------------------------------
    # データフレームから特定の値のディレクトリにファイルが存在するのかを確認

    def get_is_file(self):
        pass


    # ----------------------------------------------------------------------------------
    # ディレクトリを指定

    def _get_path(self, sub_dir_name: str):
        pass

    # ----------------------------------------------------------------------------------
    # スプシからDFを取得

    def _get_df_gss(self):
        pass

    # ----------------------------------------------------------------------------------
    # 特定のディレクトリにあるディレクトリのリストの整合する


    # ----------------------------------------------------------------------------------
    # 各ディレクトリにファイルがあるかどうかを確認する

    # ----------------------------------------------------------------------------------
