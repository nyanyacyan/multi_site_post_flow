# coding: utf-8
# 2023/7/16  更新
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import

import difflib
import pandas as pd
from datetime import datetime
from typing import Callable
from ..const import GssSheetId, KeyFile, GssSheetName

from ..base.utils import Logger
from ..base.fileWrite import FileWrite

from ..base.spreadsheetRead import GSSAPILogin


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************
# htmlの差分を出す


class DiffHtml:
    def __init__(self, exclusion_sheet_url):
        self.exclusion_sheet_url = exclusion_sheet_url

        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

        # インスタンス
        self.spreadsheet = GSSAPILogin()
        self.fileWhite = FileWrite()
        self.timestamp = datetime.now().strftime("%m-%d_%H-%M")

    # ----------------------------------------------------------------------------------
    # 除外リストのスプシを読み込む（シートは別のもの）

    def get_exclusion_list(self):
        self.logger.info(f"********** get_exclusion_list start **********")

        # スプシからDataFrameを取得
        sheet_df = self.spreadsheet.get_df_in_gss(
            sheet_name=GssSheetName.sheet_name_b.value,
            jsonKeyName=KeyFile.json_key_file.value,
            spreadsheetId=GssSheetId.sheet_id.value,
        )
        self.logger.debug(f"exclusion_sheet_url: {self.exclusion_sheet_url}")
        self.logger.debug(f"sheet_df: {sheet_df.head()}")

        exclusion_list = []

        for index, row in sheet_df.iterrows():
            element = row[1]
            position = row[2]

            if pd.notna(element) and pd.notna(position):
                self.logger.debug(f"{index} element: {element}")
                self.logger.debug(f"{index} position: {position}")

                exclusion_list.append({"element": element, "position": position})

        self.logger.info(f"********** get_exclusion_list end **********")

        self.logger.debug(f"exclusion_list:\n{exclusion_list}")

        return exclusion_list

    # ----------------------------------------------------------------------------------

    # それぞれのhtmlを行ごとにして差分を出す

    def _get_html_diff(self, old_html: str, new_html: str):
        self.logger.info(f"********** _get_html_diff start **********")

        if old_html and new_html:
            # htmlソースを行ごとに区切るように編集
            old_lines = old_html.splitlines()
            new_lines = new_html.splitlines()

        # 特殊な編集を行う
        # Diff with newlines:
        # --- old_html
        # +++ new_html
        # イテレータとしての出力になる→一度使ってしまうと消失してしまうデータ
        diff = difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile="old_html",
            tofile="new_html",
        )

        self.logger.info(f"********** _get_html_diff start **********")

        # 再利用できるようにするためにリストへ変換
        diff_list = list(diff)

        self.logger.warning(f"diff_list: {diff_list}")

        return diff_list

    # ----------------------------------------------------------------------------------
    # 必要な部分を抽出

    def _get_clean_diff(self, diff_list: list, exclusion_list: list):
        self.logger.info(f"********** _get_clean_diff start **********")

        if diff_list:
            clean_diff = []
            exclusion_line_lst = []
            for line in diff_list:
                exclude = False
                for exclusion in exclusion_list:
                    if exclusion["position"] == "開始されてるもの" and line.startswith(
                        exclusion["element"]
                    ):
                        exclude = True
                        exclusion_line_lst.append(line)
                        break
                    elif (
                        exclusion["position"] == "中にあるもの"
                        and exclusion["element"] in line
                    ):
                        exclude = True
                        exclusion_line_lst.append(line)
                        break

                if (not exclude) and (line.startswith("-") or line.startswith("+")):
                    clean_diff.append(line)

            self.logger.info(f"********** _get_clean_diff end **********")

            self.logger.debug(f"clean_diff: \n{clean_diff}")
            self.logger.warning(f"除外したものリスト: \n{exclusion_line_lst}")
            return clean_diff

    # ----------------------------------------------------------------------------------
    # 差分データを辞書データにして出力（後に抽出しやすいようにするため）

    def diff_dict_create(self, clean_diff: list):
        self.logger.info(f"********** diff_dict_create start **********")

        changes_list = []
        removed_line = None

        for line in clean_diff:
            if line.startswith("-"):
                # -を除外するために２つ目を選択。.stripにて前後にある空白を除去
                removed_line = line[1:].strip()
                changes_list.append({"old": removed_line, "new": None})

            elif line.startswith("+"):
                # ＋を除外するために２つ目を選択。.stripにて前後にある空白を除去
                added_line = line[1:].strip()

                # [-1]はリストにある最後の要素を示す
                # oldが入ってること、newに入ってないことを条件に追加
                if (
                    changes_list
                    and changes_list[-1]["new"] is None
                    and changes_list[-1]["old"] is not None
                ):
                    changes_list[-1]["new"] = added_line

                # もし条件に当てはまってないケース（古いデータがなにもない箇所に追記された場合）
                else:
                    changes_list.append({"old": f"データなし", "new": added_line})

            else:
                self.logger.debug(f"line: {line}")
                raise ValueError(f"値が期待されてるデータと違う可能性がある")

        self.logger.debug(f"changes_list: \n{changes_list}")

        self.logger.info(f"********** diff_dict_create end **********")

        return changes_list

    # ----------------------------------------------------------------------------------
    # テキストファイルに書き込むフォーマットに修正

    def textWhiteFormat(self, changes_list: list):
        self.logger.info(f"********** textWhiteFormat start **********")

        # {'old': removed_line, 'new': added_line}
        if changes_list:
            textFormatList = []
            for index, change_dict in enumerate(changes_list):
                old_html = (
                    f"{index + 1}箇所目 今までの書かれていた内容:\n{change_dict['old']}"
                )
                new_html = (
                    f"{index + 1}箇所目 書き換えられた内容:\n{change_dict['new']}"
                )

                separator = "\n\n"

                Format = separator.join([old_html, new_html])

                self.logger.debug(f"{index + 1}箇所目 Format: {Format}")

                textFormatList.append(Format)

                separator_2 = "\n****************************************\n\n"

            textWhiteFormat = separator_2.join(textFormatList)

            self.logger.info(f"textWhiteFormat: \n{textWhiteFormat}")

        else:
            return None

        self.logger.info(f"********** textWhiteFormat end **********")

        return textWhiteFormat

    # ----------------------------------------------------------------------------------
    # diff_htmlのflow

    def process(
        self,
        old_html: str,
        new_html: str,
        file_name: str,
        notifyFunc: Callable[[str, str], None],
        dNotifyFunc: Callable[[str], None],
        token: str,
        diffMessage: str,
        noDiffMessage: str,
    ):

        try:
            self.logger.info(f"********** process start **********")

            # それぞれのhtmlを行ごとにして差分を出す
            diff_list = self._get_html_diff(old_html=old_html, new_html=new_html)

            self.logger.warning(diff_list)

            if diff_list is None or not diff_list:
                self.logger.warning(f"差異なし: {diff_list}")

                # 処理なしの通知
                if notifyFunc:
                    notifyFunc(token, message=noDiffMessage)

                if dNotifyFunc:
                    dNotifyFunc(message=noDiffMessage)

            else:
                exclusion_list = self.get_exclusion_list()

                # 必要な部分を抽出
                clean_diff = self._get_clean_diff(
                    diff_list=diff_list, exclusion_list=exclusion_list
                )

                # 差分データを辞書データにして出力（後に抽出しやすいようにするため）
                changes_list = self.diff_dict_create(clean_diff=clean_diff)

                # テキストファイルに書き込むフォーマットに修正
                textData = self.textWhiteFormat(changes_list=changes_list)

                if textData is None or not textData:

                    self.logger.warning(f"差異なし: {diff_list}")

                    # 処理なしの通知
                    if notifyFunc:
                        notifyFunc(token, message=noDiffMessage)

                    if dNotifyFunc:
                        dNotifyFunc(message=noDiffMessage)

                else:
                    # テキストファイルに書き込む
                    self.fileWhite.write_to_text(data=textData, fileName=file_name)

                    separator = "\n\n\n********  ここから内容  ********\n\n\n"

                    diffText = separator.join([diffMessage, textData[:750]])

                    # 処理が実施された際の通知
                    if notifyFunc:
                        notifyFunc(token, message=diffText)

                    if dNotifyFunc:
                        dNotifyFunc(message=diffText)

            self.logger.info(f"********** process end **********")

        except ValueError as ve:
            self.logger.error(f"ValueError: {ve}")

        except Exception as e:
            self.logger.error(f"処理中にエラーが発生: {e}")


# ----------------------------------------------------------------------------------
# **********************************************************************************
