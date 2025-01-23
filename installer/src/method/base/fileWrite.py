# coding: utf-8

# 2023/9/16  更新
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import

import os, csv, json, yaml, pickle
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any
from fpdf import FPDF
import aiofiles


# 自作モジュール
from .utils import Logger
from method.const_str import Extension, SubDir
from .path import BaseToPath
from .errorHandlers import FileWriteError
from .decorators import Decorators

decoInstance = Decorators()


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************
# ファイルに書き込みする基底クラス


class FileWrite:
    def __init__(self):
        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

        # インスタンス
        self.errorhandler = FileWriteError()
        self.path = BaseToPath()
        self.currentDate = datetime.now().strftime("%y%m%d_%H%M%S")

    # ----------------------------------------------------------------------------------

    def _existsCheck(self, fullPath):
        if fullPath.exists:
            self.logger.info(f"【存在確認済】テキストファイル書き込み完了: {fullPath}")
        else:
            self.logger.error(f"Fileの書込に失敗してます{__name__}, Path:{fullPath}")

    # ----------------------------------------------------------------------------------
    # text

    @decoInstance.fileRetryAction(maxRetry=2, delay=2)
    def writeToText(self, data: Any, fileName: str, extension: str = ".txt"):
        fullPath = self.path.getWriteFilePath(fileName=fileName)
        filePath = "".join([str(fullPath), f"{self.currentDate}{extension}"])
        print(f"filePath: {filePath}")

        if data and fileName:
            self.logger.debug(f"data:\n{data}")

        # データがリストだった場合の処理
        if isinstance(data, list):
            data = "\n".join(data)

            with open(filePath, "w", encoding="utf-8") as file:
                file.write(data)

            self._existsCheck(fullPath=fullPath)

    # ----------------------------------------------------------------------------------
    # csv

    @decoInstance.fileRetryAction(maxRetry=2, delay=2)
    def writeToCsv(self, data: Any, fileName: str, extension: str = ".csv"):
        fullPath = self.path.getWriteFilePath(fileName=fileName)
        filePath = os.path.join(fullPath, f"{self.currentDate}{extension}")

        # データがリストだった場合の処理
        if isinstance(data, list):
            data = "\n".join(data)

        if data and fileName:
            # ? newline=''→Windows環境にて余計な空行を防ぐOP
            with open(filePath, "w", newline="", encoding="utf-8") as file:
                csvWriter = csv.writer(file)  # CSV形式で書き込む
                csvWriter.writerows(
                    data
                )  # 通常は1行にまとめってしまうのを開業してきれいにしてくれる

            self._existsCheck(fullPath=fullPath)

    # ----------------------------------------------------------------------------------
    # json

    @decoInstance.fileRetryAction(maxRetry=2, delay=2)
    def writeToJson(self, data: Any, fileName: str, extension: str = ".json"):
        fullPath = self.path.getWriteFilePath(fileName=fileName)
        filePath = os.path.join(fullPath, f"{self.currentDate}{extension}")

        # データがリストだった場合の処理
        if isinstance(data, list):
            data = "\n".join(data)

        if data and fileName:
            with open(filePath, "w", encoding="utf-8") as file:
                # ? ensure_ascii=False→日本語をそのまま維持する
                # ? indent=4→改行とスペースを適正にしてjsonファイルを見やすくするため
                json.dump(data, file, ensure_ascii=False, indent=4)

            self._existsCheck(fullPath=fullPath)

    # ----------------------------------------------------------------------------------
    # pickle
    # ? picklesのディレクトリに入れたい場合にはoverrideさせていれる

    @decoInstance.fileRetryAction(maxRetry=2, delay=2)
    def writeToPickle(self, data: Any, fileName: str, extension: str = ".pkl"):
        fullPath = self.path.getWriteFilePath(fileName=fileName)
        filePath = os.path.join(fullPath, f"{self.currentDate}{extension}")

        # データがリストだった場合の処理
        if isinstance(data, list):
            data = "\n".join(data)

        if data and fileName:
            with open(filePath, "wb") as file:
                pickle.dump(data, file)

            self._existsCheck(fullPath=fullPath)

    # ----------------------------------------------------------------------------------
    # excel

    @decoInstance.fileRetryAction(maxRetry=2, delay=2)
    def writeToExcel(self, data: pd.DataFrame, fileName: str, extension: str = ".xlsx"):
        fullPath = self.path.getWriteFilePath(fileName=fileName)
        filePath = os.path.join(fullPath, f"{self.currentDate}{extension}")

        if data and fileName:
            data.to_excel(filePath, index=False)

            self._existsCheck(fullPath=fullPath)

    # ----------------------------------------------------------------------------------
    # YAML

    @decoInstance.fileRetryAction(maxRetry=2, delay=2)
    def writeToYaml(self, data: pd.DataFrame, fileName: str, extension: str = ".json"):
        fullPath = self.path.getWriteFilePath(fileName=fileName)
        filePath = os.path.join(fullPath, f"{self.currentDate}{extension}")

        if data and fileName:
            with open(filePath, "w", encoding="utf-8") as file:
                # ? allow_unicode=True→日本語をそのまま維持する
                yaml.dump(data, file, allow_unicode=True)

            self._existsCheck(fullPath=fullPath)


# ----------------------------------------------------------------------------------
# **********************************************************************************
# ファイルに書き込みする基底クラス


class LimitFileWrite:
    def __init__(self):

        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

        # インスタンス
        self.errorhandler = FileWriteError()
        self.path = BaseToPath()
        self.currentDate = datetime.now().strftime("%y%m%d")

    # ----------------------------------------------------------------------------------

    def _existsCheck(self, filePath: str):
        if os.path.exists(filePath):
            self.logger.info(f"【存在確認済】テキストファイル書き込み完了: {filePath}")
        else:
            self.logger.error(f"Fileの書込に失敗してます{__name__}, Path:{filePath}")

    # ----------------------------------------------------------------------------------

    def cleanWriteFiles(self, filePath, extension: str, keepWrites: int = 3):
        validPrefixes = tuple(str(i).zfill(4) for i in range(10000))

        writeFiles = [
            file
            for file in os.listdir(filePath)
            if file.startswith(validPrefixes) and file.endswith(extension)
        ]

        if len(writeFiles) > keepWrites:
            writeFiles.sort()

            oldFile = writeFiles[0]
            fileToRemove = os.path.join(filePath, oldFile)
            if os.path.exists(fileToRemove):
                os.remove(fileToRemove)
                self.logger.info(
                    f"{keepWrites}つ以上のファイルを検知: {oldFile} を削除"
                )

    # ----------------------------------------------------------------------------------
    # text

    @decoInstance.fileRetryAction(maxRetry=2, delay=2)
    def writeToText(
        self, data: Any, fileName: str, extension: str = Extension.text.value
    ):
        filePath = self.path.getResultFilePath(fileName=fileName)

        if data and fileName:
            with open(filePath, "w", encoding="utf-8") as file:
                file.write(data)

            self._existsCheck(filePath=filePath)
            self.cleanWriteFiles(filePath=filePath, extension=extension)

    # ----------------------------------------------------------------------------------
    # csv

    @decoInstance.fileRetryAction(maxRetry=2, delay=2)
    def writeToCsv(
        self, data: Any, subDirName: str, extension: str = Extension.csv.value
    ):
        filePath = self.path.writeFileDateNamePath(
            subDirName=subDirName, extension=extension
        )

        if data and subDirName:
            # ? newline=''→Windows環境にて余計な空行を防ぐOP
            with open(filePath, "w", newline="", encoding="utf-8") as file:
                csvWriter = csv.writer(file)  # CSV形式で書き込む
                csvWriter.writerows(
                    data
                )  # 通常は1行にまとめってしまうのを開業してきれいにしてくれる

            self._existsCheck(filePath=filePath)
            self.cleanWriteFiles(filePath=filePath, extension=extension)

    # ----------------------------------------------------------------------------------
    # json

    @decoInstance.fileRetryAction(maxRetry=2, delay=2)
    def writeToJson(
        self, data: Any, subDirName: str, extension: str = Extension.json.value
    ):
        filePath = self.path.writeFileDateNamePath(
            subDirName=subDirName, extension=extension
        )

        if data and subDirName:
            with open(filePath, "w", encoding="utf-8") as file:
                # ? ensure_ascii=False→日本語をそのまま維持する
                # ? indent=4→改行とスペースを適正にしてjsonファイルを見やすくするため
                json.dump(data, file, ensure_ascii=False, indent=4)

            self._existsCheck(filePath=filePath)
            self.cleanWriteFiles(filePath=filePath, extension=extension)

    # ----------------------------------------------------------------------------------
    # pickle
    # ? picklesのディレクトリに入れたい場合にはoverrideさせていれる

    @decoInstance.fileRetryAction(maxRetry=2, delay=2)
    def writeToPickle(
        self, data: Any, subDirName: str, extension: str = Extension.pickle.value
    ):
        filePath = self.path.writeFileDateNamePath(
            subDirName=subDirName, extension=extension
        )

        if data and subDirName:
            with open(filePath, "wb") as file:
                pickle.dump(data, file)

            self._existsCheck(filePath=filePath)
            self.cleanWriteFiles(filePath=filePath, extension=extension)

    # ----------------------------------------------------------------------------------
    # excel

    @decoInstance.fileRetryAction(maxRetry=2, delay=2)
    def writeToExcel(
        self,
        data: pd.DataFrame,
        subDirName: str,
        extension: str = Extension.excel.value,
    ):
        filePath = self.path.writeFileDateNamePath(
            subDirName=subDirName, extension=extension
        )

        if data and subDirName:
            data.to_excel(filePath, index=False)

            self._existsCheck(filePath=filePath)
            self.cleanWriteFiles(filePath=filePath, extension=extension)

    # ----------------------------------------------------------------------------------
    # YAML

    @decoInstance.fileRetryAction(maxRetry=2, delay=2)
    def writeToYaml(
        self, data: pd.DataFrame, subDirName: str, extension: str = Extension.yaml.value
    ):
        filePath = self.path.writeFileDateNamePath(
            subDirName=subDirName, extension=extension
        )

        if data and subDirName:
            with open(filePath, "w", encoding="utf-8") as file:
                # ? allow_unicode=True→日本語をそのまま維持する
                yaml.dump(data, file, allow_unicode=True)

            self._existsCheck(filePath=filePath)
            self.cleanWriteFiles(filePath=filePath, extension=extension)

    # ----------------------------------------------------------------------------------

    def cookieToPickle(
        self, cookie: Dict[str, Any], extension: str = Extension.cookie.value
    ):
        filePath = self.path.writeCookiesFileDateNamePath(extension)

        if cookie:
            with open(filePath, "wb") as file:
                pickle.dump(cookie, file)

            self._existsCheck(filePath=filePath)
            self.cleanWriteFiles(filePath=filePath, extension=extension)

    # ----------------------------------------------------------------------------------
    # cookies→text

    @decoInstance.fileRetryAction(maxRetry=2, delay=2)
    def cookiesWriteToText(
        self, cookies: List[Dict[str, Any]], extension: str = Extension.text.value
    ):
        filePath = self.path.writeCookiesFileDateNamePath(extension=extension)

        if cookies:
            self.logger.debug(f"cookies:\n{cookies[30:]}")

            with open(filePath, "w", encoding="utf-8") as file:
                for cookie in cookies:
                    if "expiry" in cookie:
                        expiryTimestamp = cookie["expiry"]
                        expiryDatetime = datetime.utcfromtimestamp(expiryTimestamp)

                        cookieExpiryTimestamp = f"Cookie: {cookie['name']} の有効期限は「{expiryDatetime}」\n"

                        file.write(cookieExpiryTimestamp)

            self._existsCheck(filePath=filePath)
            self.cleanWriteFiles(filePath=filePath, extension=extension)


# ----------------------------------------------------------------------------------
# **********************************************************************************


class PDFWhite(FPDF):
    def __init__(
        self,
        margin: int = 8,
        font: str = "ArialUnicode",
        fontSize: int = 12,
    ):
        super().__init__()

        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

        fontPath = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "fonts", "Arial Unicode.ttf"
        )

        # 初期設定
        # 自動でページの切替とmarginの設定
        self.set_auto_page_break(auto=True, margin=margin)
        self.add_page()

        # フォント設定（日本語フォントを使用）
        self.add_font(font, fname=fontPath, uni=True)
        self.add_font(font, fname=fontPath, uni=True, style="B")
        self.set_font(font, size=fontSize)

        self.font = font
        self.defaultFontSize = fontSize

        # タプルである必要がある→変更のできない確定した数値の列のイメージ
        # タプルをアンパックする際にはアスタリスクを変数の前にいれる必要がある
        self.blackColor = (0, 0, 0)

        # フォントとサイズの設定(基底)
        self.set_font(self.font, size=fontSize)

    # ----------------------------------------------------------------------------------
    # titleをPDFファイルへの書き込み

    def _setTitle(self, title: str, titleFontSize: int = 10):
        self.logger.info(f"********** _setTitle start **********")
        try:

            self.logger.debug(f"title: {title}")

            # titleのfontの設定
            self.set_font(self.font, "B", size=titleFontSize)

            # titleの色を指定
            self.set_text_color(*self.blackColor)

            # 配置とセルに追加
            # セルとはその素材が入る枠のこと（Excelのセルなどの自由に配置できるものという認識）
            #! 引数→self.cell(w, h, txt='', border=0, ln=0, align='', fill=False, link='')
            # 枠線(border)は0: 枠線なし、1: 四辺すべてに枠線あり、'L','T','R','B'で上下左右に設置
            self.cell(w=0, h=8, txt=title, align="L")

            # 空白を設置
            self.ln(4)

            # 初期値に戻す
            self.set_font(self.font, size=self.defaultFontSize)

            self.logger.info(f"********** _setTitle end **********")

        except Exception as e:
            self.logger.error(f"pdfタイトル処理中にエラー発生: {e}")

    # ----------------------------------------------------------------------------------
    # body部分をPDFへの書き込み

    def _setBody(
        self,
        body: str,
        beforeWord_blue: str,
        beforeWord_red: str,
        blueFontSize: int = 10,
        redFontSize: int = 10,
    ):
        self.logger.info(f"********** _setBody start **********")

        self.logger.debug(f"body: {body[50:]}")
        self.logger.debug(f"beforeWord_blue: {beforeWord_blue}")
        self.logger.debug(f"beforeWord_red: {beforeWord_red}")

        blue = 0
        red = 0

        # ここで行ごと（\n）になるようにしないと[for]が1文字ずつ区切ってしまう
        lines = body.split("\n")

        for line in lines:
            if beforeWord_blue in line:
                blue += 1
                self.set_font(self.font, size=self.defaultFontSize)
                self.multi_cell(w=0, h=8, txt=line, align="L")

            # blueのフラグを立てた次の行を赤字に変更
            elif blue == 1:
                self.logger.debug(f"blueLineParts: {line}")
                self.set_text_color(0, 0, 255)
                self.set_font(self.font, "B", size=blueFontSize)
                self.multi_cell(w=0, h=8, txt=line, align="L")

                # defaultにセット
                self.set_text_color(*self.blackColor)
                blue = 0

            elif beforeWord_red in line:
                red += 1
                self.multi_cell(w=0, h=8, txt=line, align="L")

            elif red == 1:
                self.logger.debug(f"redLineParts: {line}")
                self.set_text_color(255, 0, 0)
                self.set_font(self.font, "B", size=redFontSize)
                self.multi_cell(w=0, h=8, txt=line, align="L")

                # defaultにセット
                self.set_text_color(*self.blackColor)
                red = 0

            # なにもない場合には通常の書き込み
            else:
                self.set_font(self.font, size=self.defaultFontSize)
                self.multi_cell(w=0, h=8, txt=line, align="L")

        self.logger.info(f"********** _setBody end **********")

    # ----------------------------------------------------------------------------------
    # 実行

    def process(
        self,
        title: str,
        body: str,
        beforeWord_blue: str,
        beforeWord_red: str,
        outputPath: str,
    ):

        self.logger.info(f"********** _setBody start **********")
        try:
            # PDFへタイトル部分の書き込み
            self._setTitle(title=title)

            # pdfへbody部分の書き込み
            self._setBody(
                body=body,
                beforeWord_blue=beforeWord_blue,
                beforeWord_red=beforeWord_red,
            )
            self.output(outputPath)

            self.logger.info(f"********** _setBody end **********")

        except Exception as e:
            self.logger.error(f"pdf処理中にエラー発生: {e}")


# **********************************************************************************
# ファイルに書き込みする基底クラス
#! 書き込みするディレクトリのファイル数をマネージメントするクラス


class LimitSabDirFileWrite:
    def __init__(self):

        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

        # インスタンス
        self.errorhandler = FileWriteError()
        self.path = BaseToPath()
        self.currentDate = datetime.now().strftime("%y%m%d")

    # ----------------------------------------------------------------------------------

    def _existsCheck(self, filePath: str):
        if os.path.exists(filePath):
            self.logger.info(f"【存在確認済】テキストファイル書き込み完了: {filePath}")
        else:
            self.logger.error(f"Fileの書込に失敗してます{__name__}, Path:{filePath}")

    # ----------------------------------------------------------------------------------

    def cleanWriteFiles(self, filePath, extension: str, keepWrites: int = 3):
        dirName = os.path.dirname(filePath)
        validPrefixes = tuple(str(i).zfill(4) for i in range(10000))

        writeFiles = [
            file
            for file in os.listdir(dirName)
            if file.startswith(validPrefixes) and file.endswith(extension)
        ]

        if len(writeFiles) > keepWrites:
            writeFiles.sort()

            oldFile = writeFiles[0]
            fileToRemove = os.path.join(dirName, oldFile)
            if os.path.exists(fileToRemove):
                os.remove(fileToRemove)
                self.logger.info(
                    f"{keepWrites}つ以上のファイルを検知: {oldFile} を削除"
                )

    # ----------------------------------------------------------------------------------
    # text

    @decoInstance.fileRetryAction(maxRetry=2, delay=2)
    def writeSabDirToText(
        self,
        data: Any,
        subDirName: str,
        fileName: str,
        extension: str = Extension.text.value,
    ):
        filePath = self.path.getResultSubDirFilePath(
            subDirName=subDirName, fileName=fileName, extension=extension
        )

        # データがリストだった場合の処理
        if isinstance(data, list):
            data = "\n".join(data)

        if data and fileName:
            with open(filePath, "w", encoding="utf-8") as file:
                file.write(data)

            self._existsCheck(filePath=filePath)
            self.cleanWriteFiles(filePath=filePath, extension=extension)

    # ----------------------------------------------------------------------------------
    # pickle
    # ? picklesのディレクトリに入れたい場合にはoverrideさせていれる

    # @decoInstance.fileRetryAction(maxRetry=2, delay=2)
    def writeSabDirToPickle(
        self,
        data: Any,
        subDirName: str = SubDir.pickles.value,
        extension: str = Extension.pickle.value,
    ):
        filePath = self.path.getResultSubDirFilePath(
            subDirName=subDirName, fileName=self.currentDate, extension=extension
        )
        self.logger.debug(f"data: {data}")
        if data and subDirName:
            with open(filePath, "wb") as file:
                pickle.dump(data, file)

            self._existsCheck(filePath=filePath)
            self.cleanWriteFiles(filePath=filePath, extension=extension)


# ----------------------------------------------------------------------------------
# **********************************************************************************
# ファイルに書き込みする基底クラス
#! 書き込みするディレクトリのファイル数をマネージメントするクラス


class AsyncLimitSabDirFileWrite:
    def __init__(self):

        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

        # インスタンス
        self.errorhandler = FileWriteError()
        self.path = BaseToPath()
        self.currentDate = datetime.now().strftime("%y%m%d")

    # ----------------------------------------------------------------------------------

    def cleanWriteFiles(self, filePath, extension: str, keepWrites: int = 3):
        dirName = os.path.dirname(filePath)
        validPrefixes = tuple(str(i).zfill(4) for i in range(10000))

        writeFiles = [
            file
            for file in os.listdir(dirName)
            if file.startswith(validPrefixes) and file.endswith(extension)
        ]

        if len(writeFiles) > keepWrites:
            writeFiles.sort()

            oldFile = writeFiles[0]
            fileToRemove = os.path.join(dirName, oldFile)
            if os.path.exists(fileToRemove):
                os.remove(fileToRemove)
                self.logger.info(
                    f"{keepWrites}つ以上のファイルを検知: {oldFile} を削除"
                )

    # ----------------------------------------------------------------------------------
    # text

    @decoInstance.fileRetryAction(maxRetry=2, delay=2)
    async def asyncWriteSabDirToText(
        self,
        data: Any,
        subDirName: str,
        fileName: str,
        extension: str = Extension.text.value,
    ):
        filePath = self.path.getResultSubDirFilePath(
            subDirName=subDirName, fileName=fileName, extension=extension
        )

        # データがリストだった場合の処理
        if isinstance(data, list):
            data = "\n".join(data)

        if data and fileName:
            async with aiofiles.open(filePath, "w", encoding="utf-8") as file:
                await file.write(data)

            self._existsCheck(filePath=filePath)
            self.cleanWriteFiles(filePath=filePath, extension=extension)

    # ----------------------------------------------------------------------------------
    # pickle
    # ? picklesのディレクトリに入れたい場合にはoverrideさせていれる

    @decoInstance.fileRetryAction(maxRetry=2, delay=2)
    async def asyncWriteSabDirToPickle(
        self,
        data: Any,
        subDirName: str,
        fileName: str,
        extension: str = Extension.pickle.value,
    ):
        filePath = self.path.getResultSubDirFilePath(
            subDirName=subDirName, fileName=fileName, extension=extension
        )

        if data and subDirName:
            async with aiofiles.open(filePath, "wb") as file:
                binary_data = pickle.dumps(data)
                await file.write(binary_data)

            self._existsCheck(filePath=filePath)
            self.cleanWriteFiles(filePath=filePath, extension=extension)


# ----------------------------------------------------------------------------------
# ファイルに書き込みする基底クラス
#! 書き込みするディレクトリのファイル数をマネージメントするクラス


class AppendWrite:
    def __init__(self):

        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

        # インスタンス
        self.errorhandler = FileWriteError()
        self.path = BaseToPath()
        self.currentDate = datetime.now().strftime("%y%m%d")

    # ----------------------------------------------------------------------------------

    def _existsCheck(self, filePath: str):
        if os.path.exists(filePath):
            self.logger.info(
                f"【存在確認済】テキストファイルに追記の書き込み完了: {filePath}"
            )
        else:
            self.logger.error(f"Fileの書込に失敗してます{__name__}, Path:{filePath}")

    # ----------------------------------------------------------------------------------
    # Result > 0101 > fileName.txt 追記モード

    @decoInstance.fileRetryAction(maxRetry=2, delay=2)
    def append_result_text(
        self,
        data: Any,
        subDirName: str,
        fileName: str,
        extension: str = Extension.text.value,
    ):
        filePath = self.path.getResultSubDirFilePath(
            subDirName=subDirName, fileName=fileName, extension=extension
        )

        # データがリストだった場合の処理
        if isinstance(data, list):
            data = "\n".join(data)

        if data and fileName:
            with open(filePath, "a", encoding="utf-8") as file:
                file.write(data)

            self._existsCheck(filePath=filePath)


# ----------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------
