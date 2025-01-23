# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# 2023/6/14 更新
# テストOK
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import logging
import os
import shutil
from datetime import datetime

# 自作モジュール
from pathlib import Path
from method.const_str import FileName


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$%$$$$$$$$$$$$$$$$$$$
# **********************************************************************************


class LoggerBasicColor(logging.Formatter):
    COLORS = {
        "DEBUG": "\033[90m",  # グレー
        "INFO": "\033[94m",  # 青色
        "WARNING": "\033[93m",  # 黄色
        "ERROR": "\033[91m",  # 赤色
        "CRITICAL": "\033[95m",  # マゼンダ
    }

    RESET = "\033[0m"
# ----------------------------------------------------------------------------------


    def format(self, record):
        message = super().format(record)
        color = self.COLORS.get(record.levelname, "")
        return f"{color}{message}{self.RESET}"


# ----------------------------------------------------------------------------------
# **********************************************************************************


class Logger:
    def __init__(self, debugMode: bool=True):
        # このメソッド名のLoggerを生成
        file_name = FileName.LOG_FILE_NAME.value
        self.logger = logging.getLogger(file_name)

        self.debugMode = debugMode

        # インスタンス
        self.currentDate = datetime.now().strftime('%y%m%d')
        self.setUpToLogger()  # addHandlerにて追加したものを反映


# ----------------------------------------------------------------------------------


    def loggingLevel(self):
        if self.debugMode == True:
            return logging.DEBUG
        else:
            return logging.INFO


# ----------------------------------------------------------------------------------
# Loggerは、ログメッセージを生成、Handlerは、そのメッセージをどこに送るかを決定
# 1つのLoggerに複数のHandlerを追加できる。
# ConsoleHandler: コンソールへの出力設定
# FileHandler: logFileへの書き込み設定
# Handlerは、ログメッセージの「出力先」を定義→ログメッセージの配送係みたいなイメージ


    # keepLogsは指定した数字分の日付のを古い順にしてlogは残しておくようにしてある
    def setUpToLogger(self, keepLogs: int=5):
        if not self.logger.handlers:
            # ログレベルをセットする
            loggingLevel = self.loggingLevel()
            self.logger.setLevel(loggingLevel)

            # ログをコンソール（ターミナル）に表示させる設定
            consoleHandler = logging.StreamHandler()
            consoleHandler.setLevel(loggingLevel)

            # ログメッセージの基本フォーマット→時間→ログレベル→エラーメッセージ
            consoleHandler.setFormatter(LoggerBasicColor("%(asctime)s - %(levelname)s - %(message)s"))
            self.logger.addHandler(consoleHandler)

            # Handlerは、ログFileを出力を定義→ログメッセージの配送係みたいなイメージ
            fileHandler = logging.FileHandler(self.logsFileName, encoding="utf-8")
            fileHandler.setLevel(logging.DEBUG)
            fileHandler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
            self.logger.addHandler(fileHandler)

            self.logger.propagate = False

        self.cleanLogs(keepLogs=keepLogs)


# ----------------------------------------------------------------------------------

    @property
    def logsFileName(self):
        logDir = self.toLogsPath()
        # {self.logger.name}→標準モジュール
        logFileName = f"{logDir}/{self.logger.name}Debug.log"
        return logFileName


# ----------------------------------------------------------------------------------


    def cleanLogs(self, keepLogs: int=5):
        logsDir = self.toLogsPath()
        logsDirs = [
            logDir for logDir in os.listdir(logsDir)
            if len(logDir) ==4 and logDir.isdigit()
        ]

        if len(logsDirs) > keepLogs:
            logsDirs.sort()

            oldDir = logsDirs[0]
            dirToRemove = os.path.join(logsDir, oldDir)
            if os.path.exists(dirToRemove):
                shutil.rmtree(dirToRemove)  # ディレクトリごと消去できる
                self.logger.info(f"{keepLogs}つ以上のログファイルを検知: {oldDir} を削除")


# ----------------------------------------------------------------------------------


    def getLogger(self):
        return self.logger


# ----------------------------------------------------------------------------------
# logsFileを取得

    def toLogsPath(self, levelsUp: int = 4, dirName: str = 'resultOutput', subDirName: str = 'logs'):
        resultOutputPath = self.getResultOutputPath(levelsUp=levelsUp, dirName=dirName)

        logsPath = resultOutputPath / subDirName / self.currentDate

        self.isDirectoryExists(path=logsPath)
        # self.logger.debug(f"logsPath: {logsPath}")

        return logsPath


# ----------------------------------------------------------------------------------


    @property
    def currentDir(self):
        currentDirPath = Path(__file__).resolve()
        return currentDirPath


# ----------------------------------------------------------------------------------


    def getResultOutputPath(self, levelsUp: int = 4, dirName: str = 'resultOutput'):
        currentDirPath = self.currentDir

        # スタートが0で1つ上の階層にするため→levelsUpに１をいれたら１個上の階層にするため
        resultOutputPath = currentDirPath.parents[levelsUp - 1] / dirName
        # self.logger.debug(f"{dirName}: {resultOutputPath}")
        return resultOutputPath


# ----------------------------------------------------------------------------------
# # ディレクトリがない可能性の箇所に貼る関数

    def isDirectoryExists(self, path: Path):
        if not path.exists():
            # 親のディレクトリも作成、指定していたディレクトリが存在してもエラーを出さない
            path.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"{path.name} がないため作成")

        return path


# ----------------------------------------------------------------------------------
