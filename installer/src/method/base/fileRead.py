# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# 2024/9/17 更新

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import os, json, yaml, cv2, zipfile, pickle
import pandas as pd
from PyPDF2 import PdfReader
from PIL import Image
import aiofiles

# 自作モジュール
from .utils import Logger
from method.const_str import Encoding
from .path import BaseToPath
from .decorators import Decorators


decoInstance = Decorators()


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************


class ResultFileRead:
    def __init__(self):

        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

        # インスタンス
        self.path = BaseToPath()

    # ----------------------------------------------------------------------------------

    @decoInstance.fileRead
    def readTextResult(self, fileName: str):
        getFullPath = self.path.getResultFilePath(fileName=fileName)

        with open(getFullPath, "r", encoding=Encoding.utf8.value) as file:
            return file.read()

    # ----------------------------------------------------------------------------------

    @decoInstance.fileRead
    def readCsvResult(self, fileName: str):
        getFullPath = self.path.getResultFilePath(fileName=fileName)
        return pd.read_csv(getFullPath)

    # ----------------------------------------------------------------------------------

    @decoInstance.fileRead
    def readJsonResult(self, fileName: str):
        getFullPath = self.path.getResultFilePath(fileName=fileName)
        with open(getFullPath, "r") as file:
            return json.load(file)

    # ----------------------------------------------------------------------------------

    @decoInstance.fileRead
    def readExcelResult(self, fileName: str):
        getFullPath = self.path.getResultFilePath(fileName=fileName)
        return pd.read_excel(getFullPath)

    # ----------------------------------------------------------------------------------

    @decoInstance.fileRead
    def readYamlResult(self, fileName: str):
        getFullPath = self.path.getResultFilePath(fileName=fileName)
        with open(getFullPath, "r") as file:
            return yaml.safe_load_all(file)

    # ----------------------------------------------------------------------------------

    @decoInstance.fileRead
    def readPdfResult(self, fileName: str):
        getFullPath = self.path.getResultFilePath(fileName=fileName)
        reader = PdfReader(getFullPath)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text

    # ----------------------------------------------------------------------------------

    @decoInstance.fileRead
    def readImageResult(self, fileName: str):
        getFullPath = self.path.getResultFilePath(fileName=fileName)
        return Image.open(getFullPath)

    # ----------------------------------------------------------------------------------

    @decoInstance.fileRead
    def readVideoResult(self, fileName: str):
        getFullPath = self.path.getResultFilePath(fileName=fileName)
        return cv2.VideoCapture(getFullPath)

    # ----------------------------------------------------------------------------------

    @decoInstance.fileRead
    def readZipResult(self, fileName: str):
        getFullPath = self.path.getResultFilePath(fileName=fileName)
        zipName = fileName.split(".")[0]
        with zipfile.ZipFile(getFullPath, "r") as zip:
            zip.extractall(zipName)

    # ----------------------------------------------------------------------------------
    # 日付名の一番新しいフォルダ名のPathを取得

    def getLatestFolderPath(self, path: str):
        self.logger.debug(f"path: {path}")
        files = [
            f
            for f in os.listdir(path)
            if os.path.isfile(os.path.join(path, f)) and f.endswith(".pkl")
        ]
        self.logger.debug(f"files: {files}")
        latestFolder = sorted(files, reverse=True)[0]
        return os.path.join(path, latestFolder)

    # ----------------------------------------------------------------------------------
    # pickleの読込

    def readPickleLatestResult(self):
        picklesPath = self.path.getPickleDirPath()
        latestPickleFilePath = self.getLatestFolderPath(path=picklesPath)
        self.logger.debug(
            f"picklesPath: {picklesPath}\nlatestPickleFilePath: {latestPickleFilePath}"
        )

        with open(latestPickleFilePath, "rb") as file:
            data = pickle.load(file)
            self.logger.debug(f"Loaded data from pickle: {data}")
            return data

    # ----------------------------------------------------------------------------------
    # cookieの読込

    def readCookieLatestResult(self):
        CookiesPath = self.path.getCookieDirPath()
        latestCookieFilePath = self.getLatestFolderPath(path=CookiesPath)
        return pickle.load(latestCookieFilePath)


# ----------------------------------------------------------------------------------
# **********************************************************************************


class InputDataFileRead:
    def __init__(self):

        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

        # インスタンス
        self.path = BaseToPath()

    # ----------------------------------------------------------------------------------

    @decoInstance.fileRead
    def readTextToInput(self, fileName: str):
        getFullPath = self.path.getInputDataFilePath(fileName=fileName)

        with open(getFullPath, "r", encoding=Encoding.utf8.value) as file:
            return file.read()

    # ----------------------------------------------------------------------------------

    @decoInstance.fileRead
    def readCsvInput(self, fileName: str):
        getFullPath = self.path.getInputDataFilePath(fileName=fileName)
        return pd.read_csv(getFullPath)

    # ----------------------------------------------------------------------------------

    @decoInstance.fileRead
    def readJsonInput(self, fileName: str):
        getFullPath = self.path.getInputDataFilePath(fileName=fileName)
        with open(getFullPath, "r") as file:
            return json.load(file)

    # ----------------------------------------------------------------------------------

    @decoInstance.fileRead
    def readExcelInput(self, fileName: str):
        getFullPath = self.path.getInputDataFilePath(fileName=fileName)
        return pd.read_excel(getFullPath)

    # ----------------------------------------------------------------------------------

    @decoInstance.fileRead
    def readYamlInput(self, fileName: str):
        getFullPath = self.path.getInputDataFilePath(fileName=fileName)
        with open(getFullPath, "r") as file:
            return yaml.safe_load_all(file)

    # ----------------------------------------------------------------------------------

    @decoInstance.fileRead
    def readPdfInput(self, fileName: str):
        getFullPath = self.path.getInputDataFilePath(fileName=fileName)
        reader = PdfReader(getFullPath)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text

    # ----------------------------------------------------------------------------------

    @decoInstance.fileRead
    def readImageInput(self, fileName: str):
        getFullPath = self.path.getInputDataFilePath(fileName=fileName)
        return Image.open(getFullPath)

    # ----------------------------------------------------------------------------------

    @decoInstance.fileRead
    def readVideoInput(self, fileName: str):
        getFullPath = self.path.getInputDataFilePath(fileName=fileName)
        return cv2.VideoCapture(getFullPath)

    # ----------------------------------------------------------------------------------

    @decoInstance.fileRead
    def readZipInput(self, fileName: str):
        getFullPath = self.path.getInputDataFilePath(fileName=fileName)
        zipName = fileName.split(".")[0]
        with zipfile.ZipFile(getFullPath, "r") as zip:
            zip.extractall(zipName)


# ----------------------------------------------------------------------------------
# **********************************************************************************


class AsyncResultFileRead:
    def __init__(self):

        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

        # インスタンス
        self.path = BaseToPath()

    # ----------------------------------------------------------------------------------
    # pickleの読込

    async def asyncWriteSabDirToPickle(self):
        picklesPath = await self.path.getPickleDirPath()
        latestPickleFilePath = await self.getLatestFolderPath(path=picklesPath)
        async with aiofiles.open(latestPickleFilePath, "rb") as file:
            binary_data = await file.read()

        return pickle.loads(binary_data)


# ----------------------------------------------------------------------------------
