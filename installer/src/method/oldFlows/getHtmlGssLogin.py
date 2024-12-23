#  coding: utf-8
# 2024/6/17 更新
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import

import pandas as pd
from ..const import GssSheetId, KeyFile, GssSheetName

# 自作モジュール
from ..base.spreadsheetRead import SpreadsheetRead
from ..base.LoginWithCookie import AutoLogin
from ..base.getHtml import GetHtml
from ..base.utils import Logger
from ..base.spreadsheetRead import GSSAPILogin

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
####################################################################################
# URLとtitle取得　オーバーライド


class OverrideSpreadsheet(SpreadsheetRead):
    def __init__(self, sheet_url, account_id, debugMode=True):
        super().__init__(sheet_url, account_id, debugMode)

    # URLを取得
    def get_url_in_gss(self):
        return super().get_url_in_gss()

    # 名称（title）を取得
    def get_name_in_gss(self):
        return super().get_name_in_gss()


####################################################################################
# ログイン オーバーライド


class OverrideAutoLogin(AutoLogin):
    def __init__(self, chrome, debugMode=True):
        super().__init__(chrome, debugMode)

    # titleとサイトが開いてるかどうかでサイトが開いてるかを確認
    def site_open_title_check(self, gss_url, gss_title, field_name, token, notifyFunc):
        return super().site_open_title_check(
            gss_url, gss_title, field_name, token, notifyFunc
        )


####################################################################################
# requests オーバーライド


class OverrideGetHtml(GetHtml):
    def __init__(self, debugMode=True):
        super().__init__(debugMode)

    def organized_html(
        self,
        url: str,
        keep_element: str,
        remove_tags_elements: str,
        remove_class_names: str,
    ):
        return super().organized_html(
            url, keep_element, remove_tags_elements, remove_class_names
        )


####################################################################################
# **********************************************************************************
# スプシからURL、titleを取得、そのhtmlデータを取得


class GetHtmlGssLogin:
    def __init__(self, chrome, sheet_url, account_id, debugMode=True):
        self.chrome = chrome
        self.account_id = account_id

        # logger
        self.getLogger = Logger(
            moduleName=FileName.LOG_FILE_NAME.value, debugMode=debugMode
        )
        self.logger = self.getLogger.getLogger()

        # インスタンス
        self.get_in_gss = OverrideSpreadsheet(
            sheet_url=sheet_url, account_id=account_id, debugMode=debugMode
        )
        self.login = OverrideAutoLogin(chrome=chrome, debugMode=debugMode)
        self.get_html = OverrideGetHtml(debugMode=debugMode)
        self.spreadsheet = GSSAPILogin(debugMode=debugMode)

    # ----------------------------------------------------------------------------------
    # クラスの除外リストをスプシより取得

    def _get_remove_class_gsslist(self):
        self.logger.info(f"******** _get_remove_class_gsslist start ********")

        sheet_df = self.spreadsheet.get_df_in_gss(
            sheet_name=GssSheetName.sheet_name_a.value,
            jsonKeyName=KeyFile.json_key_file.value,
            spreadsheetId=GssSheetId.sheet_id.value,
        )
        self.logger.debug(f"sheet_df: {sheet_df.head()}")

        remove_class_list = []

        for index, row in sheet_df.iterrows():
            class_name = row[1]

            if pd.notna(class_name):
                self.logger.debug(f"{index} class_name: {class_name}")

                remove_class_list.append({"class_name": class_name})

        self.logger.info(f"******** _get_remove_class_gsslist end ********")

        self.logger.debug(f"exclusion_list:\n{remove_class_list}")

        return remove_class_list

    # ----------------------------------------------------------------------------------
    # flowの定義

    def process(self, url, notifyFunc, token: str):
        try:
            self.logger.info(f"******** get_html_gss_login_process start ********")

            name = self.get_in_gss.get_name_in_gss()
            remove_class_names = self._get_remove_class_gsslist()

            # ログインチェック
            self.login.site_open_title_check(
                gss_url=url,
                gss_title=name,
                field_name=self.account_id,
                notifyFunc=notifyFunc,
                token=token,
            )

            # htmlを取得して欲しい情報に整理
            organized_html = self.get_html.organized_html(
                url=url,
                keep_element="body",
                remove_tags_elements="a",
                remove_class_names=remove_class_names,
            )
            self.logger.info(f"******** get_html_gss_login_process end ********")

            return organized_html

        except Exception as e:
            self.logger.error(f"get_html_gss_login_process 処理中にエラーが発生{e}")
            raise


# ----------------------------------------------------------------------------------
# **********************************************************************************
