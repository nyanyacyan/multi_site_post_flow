# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# 2023/9/14 更新
# テストOK
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

# import
import os
from pathlib import Path
from datetime import datetime

# 自作モジュール
# import const
from .utils import Logger
from const_str import Dir, SubDir, Extension
from .errorHandlers import AccessFileNotFoundError



# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************
# 利用するメソッドがBaseだったときのクラス

class BaseToPath:
    def __init__(self, debugMode=True):

        # logger
        self.getLogger = Logger(__name__, debugMode=debugMode)
        self.logger = self.getLogger.getLogger()

        # インスタンス
        self.fileNotFoundError = AccessFileNotFoundError(debugMode=debugMode)
        self.currentDate = datetime.now().strftime('%y%m%d')
        self.fullCurrentDate = datetime.now().strftime('%y%m%d_%H%M%S')


# ----------------------------------------------------------------------------------
# logsFileを取得

    def toLogsPath(self, levelsUp: int = 4, subDirName: str = 'logs'):
        resultOutputPath = self.getResultOutputPath(levelsUp=levelsUp, dirName=self.resultBox)
        logsPath = resultOutputPath / subDirName / self.currentDate
        self.isDirExists(path=logsPath)
        self.logger.debug(f"logsPath: {logsPath}")

        return logsPath


# ----------------------------------------------------------------------------------
# inputDataの中にあるFilePathを取得

    def getInputDataFilePath(self, fileName: str, levelsUp: int = 2):
        try:
            inputDataPath = self.getInputDataPath(levelsUp=levelsUp, dirName=self.inputBox)

            accessFilePath = inputDataPath / fileName
            self.logger.debug(f"{fileName} を発見: {accessFilePath}")

            return accessFilePath

        except Exception as e:
            self.fileNotFoundError.accessFileNotFoundError(fileName=fileName, e=e)

# ----------------------------------------------------------------------------------
# pickleFileを取得

    def getPickleFilePath(self, pklName: str, levelsUp: int = 4, subDirName: str = 'pickles'):
        picklesPath = self.toPicklesPath(levelsUp=levelsUp, dirName=self.resultBox, subDirName=subDirName)
        pickleFilePath = picklesPath / f'{pklName}.pkl'
        self.logger.debug(f"pickleFilePath: {pickleFilePath}")
        return pickleFilePath


# ----------------------------------------------------------------------------------

    @property
    def currentDir(self):
        currentDirPath = Path(__file__).resolve()
        return currentDirPath


# ----------------------------------------------------------------------------------
# resultOutputの大元の定義
#! ディレクトリの変更があった場合にはレベルを調整

    def getResultOutputPath(self, levelsUp: int = 4, dirName: str=Dir.result.value):
        currentDirPath = self.currentDir
        self.logger.info(f"levelsUp の型: {type(levelsUp)}: {levelsUp}")

        # スタートが0で1つ上の階層にするため→levelsUpに１をいれたら１個上の階層にするため
        resultOutputPath = currentDirPath.parents[levelsUp - 1] / dirName
        self.logger.debug(f"{dirName}: {resultOutputPath}")
        return resultOutputPath


# ----------------------------------------------------------------------------------
# inputDataへの大元の定義
#! ディレクトリの変更があった場合にはレベルを調整

    def getInputDataPath(self, levelsUp: int = 2, dirName: str=Dir.input.value):
        currentDirPath = self.currentDir

        # スタートが0で1つ上の階層にするため→levelsUpに１をいれたら１個上の階層にするため
        inputDataPath = currentDirPath.parents[levelsUp - 1] / dirName
        self.logger.debug(f"{dirName}: {inputDataPath}")
        return inputDataPath


# ----------------------------------------------------------------------------------
# File名を付け足して書込時に拡張子を付け足す


    def getWriteFilePath(self, fileName: str):
        resultOutputPath = self.getResultOutputPath()
        filePath = resultOutputPath / fileName
        return filePath


# ----------------------------------------------------------------------------------
# ディレクトリがない可能性の箇所に貼る関数

    def isDirExists(self, path: Path):
        if not path.exists():
            # 親のディレクトリも作成、指定していたディレクトリが存在してもエラーを出さない
            path.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"{path.name} がないため作成")
        else:
            self.logger.debug(f"{path.name} 発見")
        return path


# ----------------------------------------------------------------------------------
# ディレクトリがない可能性の箇所に貼る関数

    def isFileExists(self, path: Path):
        if not path.exists():
            path.touch()
            self.logger.info(f"{path.name} がないため作成")
        else:
            self.logger.debug(f"{path.name} 発見")
        return path


# ---------------------------------------------------------------------------------
# Input > File

    def getInputDataFilePath(self, fileName: str):
        inputDataPath = self.getInputDataPath()
        FilePath = inputDataPath / fileName
        self.logger.debug(f"FilePath: {FilePath}")
        return FilePath


# ----------------------------------------------------------------------------------
# Result > File

    def getResultFilePath(self, fileName: str):
        resultOutputPath = self.getResultOutputPath()
        FilePath = resultOutputPath / fileName
        self.isDirExists(path=FilePath)
        self.logger.debug(f"FilePath: {FilePath}")
        return FilePath


# ----------------------------------------------------------------------------------
# Result > SubDir > File

    def getResultSubDirFilePath(self, subDirName: str, fileName: str, extension: str):
        resultOutputPath = self.getResultOutputPath()
        dirPath = resultOutputPath / subDirName
        file = fileName + extension
        FilePath = dirPath / file
        self.logger.warning(f"FilePath: {FilePath}")
        self.logger.debug(f"FilePathの型: {type(FilePath)}")
        self.isDirExists(path=dirPath)
        self.logger.debug(f"FilePath: {FilePath}")
        return FilePath


# ----------------------------------------------------------------------------------
# Result > SubDir > FileName0101.txt

    def getResultSubDirDateFilePath(self, subDirName: str, fileName: str, extension: str):
        resultOutputPath = self.getResultOutputPath()
        dirPath = resultOutputPath / subDirName
        file = fileName + self.fullCurrentDate + extension
        FilePath = dirPath / file
        self.logger.warning(f"FilePath: {FilePath}")
        self.logger.debug(f"FilePathの型: {type(FilePath)}")
        self.isDirExists(path=dirPath)
        self.logger.debug(f"FilePath: {FilePath}")
        return FilePath


# ----------------------------------------------------------------------------------

# Result > SubDir > 0101.db

    def getResultDBDirPath(self, subDirName: str=SubDir.DBSubDir.value):
        resultOutputPath = self.getResultOutputPath()
        dirPath = resultOutputPath / subDirName
        self.isDirExists(path=dirPath)
        self.logger.debug(f"dirPath: {dirPath}")

        return dirPath


# ----------------------------------------------------------------------------------
# resultOutput > 0101 > 0101.txt

    def writeFileDateNamePath(self, extension: str, subDirName: str):
        resultOutputPath = self.getResultOutputPath()
        fileFullPath = resultOutputPath / subDirName / self.currentDate / f'{self.currentDate}{extension}'
        self.isDirExists(path=fileFullPath)
        self.logger.debug(f"fileFullPath: {fileFullPath}")
        return fileFullPath


# ----------------------------------------------------------------------------------
# resultOutput > 0101 > fileName.txt

    def writeFileNamePath(self, subDirName: str, fileName: str, extension: str):
        resultOutputPath = self.getResultOutputPath()
        fileFullPath = resultOutputPath / subDirName / self.currentDate / f'{fileName}{extension}'
        self.isDirExists(path=fileFullPath)
        self.logger.debug(f"fileFullPath: {fileFullPath}")
        return fileFullPath


# ----------------------------------------------------------------------------------
# resultOutput > 0101 > 0101.pkl

    def writePicklesFileDateNamePath(self, extension: str=Extension.pickle.value, subDirName: str=SubDir.pickles.value):
        resultOutputPath = self.getResultOutputPath()
        pickleFullPath = resultOutputPath / subDirName / self.currentDate / f'{self.currentDate}{extension}'
        self.isDirExists(path=pickleFullPath)
        self.logger.debug(f"pickleFullPath: {pickleFullPath}")
        return pickleFullPath


# ----------------------------------------------------------------------------------
# resultOutput > 0101 > 0101.txt

    def writeCookiesFileDateNamePath(self, extension: str=Extension.cookie.value, subDirName: str=SubDir.cookies.value):
        resultOutputPath = self.getResultOutputPath()
        cookieFullPath = resultOutputPath / subDirName / self.currentDate / f'{self.currentDate}{extension}'
        self.isDirExists(path=cookieFullPath)
        self.logger.debug(f"cookieFullPath: {cookieFullPath}")
        return cookieFullPath


# ----------------------------------------------------------------------------------
# resultOutput > 0101.pkl

    def getPickleDirPath(self, subDirName: str=SubDir.pickles.value):
        resultOutputPath = self.getResultOutputPath()
        return os.path.join(resultOutputPath, subDirName)


# ----------------------------------------------------------------------------------
# resultOutput > 0101cookie.pkl

    def getCookieDirPath(self, subDirName: str=SubDir.cookies.value):
        resultOutputPath = self.getResultOutputPath()
        return os.path.join(resultOutputPath, subDirName)


# ----------------------------------------------------------------------------------
