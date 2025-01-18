# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import time, re
import pandas as pd
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

    def _get_photo_folder_path(self, sub_dir_name: str):
        dir_path = self.path._get_input_photo_subdir_path(subDirName=sub_dir_name)
        self.logger.debug(f'dir_path: {dir_path}')
        return dir_path


    # ----------------------------------------------------------------------------------
    # input_photoにあるフォルダ名を取得

    def _get_dir_all_folder(self):


    # ----------------------------------------------------------------------------------
    # 特定のディレクトリにあるディレクトリのリストの整合する

    def _match_dir_list(self):
        pass


    # ----------------------------------------------------------------------------------
    # 各ディレクトリにファイルがあるかどうかを確認する

    def _is_file_in_dir(self):
        pass

    # ----------------------------------------------------------------------------------
    # データフレームを受け取って特定の値のリストを返す

    def _get_list_in_df(self, df: pd.DataFrame):
        pass
