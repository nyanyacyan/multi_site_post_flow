# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# export PYTHONPATH="/Users/nyanyacyan/Desktop/project_file/domain_search/installer/src"


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import os, time, random
from selenium.webdriver.chrome.webdriver import WebDriver
from datetime import datetime


# 自作モジュール
from .utils import Logger
from .driverDeco import jsCompleteWaitDeco
from .path import BaseToPath

from method.const_str import SubDir, Extension

jsComplete = jsCompleteWaitDeco()

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************


class SeleniumBasicOperations:
    def __init__(self, chrome: WebDriver):
        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

        self.chrome = chrome

        self.jsComplete = jsCompleteWaitDeco()
        self.path = BaseToPath()
        self.currentDate = datetime.now().strftime("%y%m%d_%H%M%S")

    # ----------------------------------------------------------------------------------

    # @jsComplete.jsCompleteWaitRetry
    def openSite(self, url: str):
        self.logger.debug(f"url: {url}")
        return self.chrome.get(url)

    # ----------------------------------------------------------------------------------

    def currentUrl(self):
        return self.chrome.current_url()

    # ----------------------------------------------------------------------------------

    def newOpenWindow(self):
        return self.chrome.execute_script("window.open('');")

    # ----------------------------------------------------------------------------------

    def switchWindow(self, url: str):
        # 開いてるWindow数を確認
        if len(self.chrome.window_handles) > 1:
            self.chrome.switch_to.window(self.chrome.window_handles[1])
            self.chrome.get(url)
        else:
            self.logger.error("既存のWindowがないため、新しいWindowに切替ができません")

    # ----------------------------------------------------------------------------------
    # スクショ撮影

    def screenshot_limit(self, photo_name: str):
        extension = Extension.PNG.value
        full_path = self.path.getResultSubDirDateFilePath(
            fileName=photo_name,
            subDirName=SubDir.SCREEN_SHOT.value,
            extension=extension,
        )
        self.chrome.save_screenshot(str(full_path))
        self.logger.debug(f"full_path: {full_path}")

        self._existsCheck(filePath=full_path)
        self.cleanWriteFiles(filePath=full_path, extension=extension)
        return full_path

    # ----------------------------------------------------------------------------------
    # ファイル生成確認

    def _existsCheck(self, filePath: str):
        if os.path.exists(filePath):
            self.logger.info(f"【存在確認済】テキストファイル書き込み完了: {filePath}")
        else:
            self.logger.error(f"Fileの書込に失敗してます{__name__}, Path:{filePath}")

    # ----------------------------------------------------------------------------------
    # 対象フォルダに指定数より多かったら削除

    def cleanWriteFiles(self, filePath: str, extension: str, keepWrites: int = 3):
        dirName = os.path.dirname(filePath)

        # 指定する拡張子が同じファイルのフルパスをリスト化
        writeFiles = [
            os.path.join(dirName, file)
            for file in os.listdir(dirName)
            if file.endswith(extension)
        ]

        # ファイルの作成された日時でSortする
        writeFiles.sort(key=os.path.getmtime)

        # 既存ファイルが多かったら削除する
        if len(writeFiles) > keepWrites:
            # [:len(writeFiles) - keepWrites]→[:3]→3までのファイルを削除
            for oldFile in writeFiles[: len(writeFiles) - keepWrites]:
                if os.path.exists(oldFile):
                    os.remove(oldFile)
                    self.logger.info(
                        f"{keepWrites}つ以上のファイルを検知: {oldFile} を削除"
                    )

    # ----------------------------------------------------------------------------------
    # ランダムな待機

    def _random_sleep(self, min_num: int = 1, max_num: int = 3):
        time.sleep(random.uniform(min_num, max_num))

