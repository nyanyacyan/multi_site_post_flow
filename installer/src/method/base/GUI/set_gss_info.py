# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# export PYTHONPATH="/Users/nyanyacyan/Desktop/project_file/domain_search/installer/src"


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
from typing import Dict, List, Callable
from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QLabel,
    QGroupBox,
    QComboBox,
    QPushButton,
)
from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator

# 自作モジュール
from method.base.spreadsheetRead import GetDataGSSAPI
from method.base.search_dir_contents import FolderChecker


# ----------------------------------------------------------------------------------
# **********************************************************************************
# ユーザー情報のグループを設定


class GSSInfoForm(QGroupBox):
    def __init__(self, gui_info: Dict):
        super().__init__(gui_info["GSS_INPUT_TITLE"])  # タイトルを設定

        self.gui_info = gui_info

        # タイトルのスタイルを設定
        self.setStyleSheet(
            """
            QGroupBox {
                font-size: 12px;  /* 文字の大きさ */
                font-weight: bold;  /* 太字 */
                text-decoration: underline;  /* 下線 */
            }
        """
        )

        # レイアウトを設定
        self.setLayout(self._create_user_info_layout(gui_info=gui_info))



    ####################################################################################
    # ドロップダウンメニューで選択した値を返す

    def get_gss_info(self):
        select_worksheet = self.dropdown_menu.currentText()
        if select_worksheet == "--選択してください--":
            return None

        self._set_error_msg(None)
        return select_worksheet

    # ----------------------------------------------------------------------------------
    # ここにWorksheetの値を受けて、フォルダーチェックをする

    def _folder_check(self, worksheet_name: str):
        sub_dir_name = self.gui_info["FOLDER_NAME"]
        df = self._get_gss_df(worksheet_name=worksheet_name)
        col_name = self.gui_info["COL_NAME"]
        folder_checker = FolderChecker()
        error_msg = folder_checker.folder_error_check(sub_dir_name=sub_dir_name, df=df, col_name=col_name)
        return error_msg


    ####################################################################################
    # ユーザー入力欄のグループ

    def _create_user_info_layout(self, gui_info: Dict):
        group_layout = QVBoxLayout()

        group_layout.setContentsMargins(15, 15, 15, 15)
        group_layout.setSpacing(15)

        # gss_url入力
        gss_url_label = QLabel(gui_info["GSS_URL_LABEL"])
        self.gss_url_input = self._create_input_field(gui_info["INPUT_EXAMPLE_GSS_URL"], fixed_width=160)
        gss_url_btn = self._action_btn(name_in_btn=gui_info["GSS_URL_BTN"], action_func=self._on_url_input_finished)

        # gss_urlのレイアウト作成
        gss_url_layout = QHBoxLayout()  # 横レイアウト
        gss_url_layout.addWidget(gss_url_label)
        gss_url_layout.addWidget(self.gss_url_input)
        gss_url_layout.addWidget(gss_url_btn)

        # グループにgss_urlレイアウトを追加
        group_layout.addLayout(gss_url_layout)

        # Worksheetを選択
        dropdown_label = QLabel(gui_info["DROPDOWN_LABEL"])
        self.dropdown_input = self._dropdown_menu()
        gss_worksheet_btn = self._action_btn(name_in_btn=gui_info["GSS_FOLDER_CHECK_BTN"], action_func=self._on_folder_check)


        # worksheetのレイアウト作成
        dropdown_layout = QHBoxLayout()  # 横レイアウト
        dropdown_layout.addWidget(dropdown_label)
        dropdown_layout.addWidget(self.dropdown_input)
        dropdown_layout.addWidget(gss_worksheet_btn)


        # グループにworksheetレイアウトを追加
        group_layout.addLayout(dropdown_layout)

        # errorラベルを追加
        self.error_label = self._error_label()
        group_layout.addWidget(self.error_label)

        return group_layout

    ####################################################################################
    # ----------------------------------------------------------------------------------
    # ID入力欄→passwordを渡せば非表示

    def _create_input_field(
        self, input_example: str, fixed_width: int = 200):
        input_field = QLineEdit()
        input_field.setPlaceholderText(input_example)  # input_exampleは入力例

        # 半角のみを許可する正規表現を設定
        validator = QRegularExpressionValidator(QRegularExpression(".+"))
        input_field.setValidator(validator)

        # 入力欄の幅を調整
        input_field.setFixedWidth(fixed_width)

        return input_field

    # ----------------------------------------------------------------------------------
    # スプシからのデータを受けたドロップダウンメニュー

    def _dropdown_menu(self, fixed_width: int = 150):
        self.dropdown_menu = QComboBox()
        self.dropdown_menu.setEnabled(False)
        self.dropdown_menu.addItem("--選択してください--")  # 初期値を設定

        # 入力幅の調整
        self.dropdown_menu.setFixedWidth(fixed_width)

        return self.dropdown_menu

    # ----------------------------------------------------------------------------------
    # エラーラベル（通常時は非表示）

    def _error_label(self):
        error_label = QLabel("")  # 最初は空に設定
        error_label.setStyleSheet("color: red;")
        error_label.hide()
        return error_label

    # ----------------------------------------------------------------------------------
    # メッセージが合ったときに表示させる

    def _set_error_msg(self, msg: str):
        # エラーあり
        if msg:
            self.error_label.setText(msg)
            self.error_label.show()

        # エラーなし
        else:
            self.error_label.clear()
            self.error_label.hide()

    # ----------------------------------------------------------------------------------
    # Worksheetのリストを取得

    def _get_worksheet_list(self, sheet_url: str):
        gss_read = GetDataGSSAPI()
        worksheet_list = gss_read._get_all_worksheet_to_gui(gui_info=self.gui_info, sheet_url=sheet_url, sort_word_list=self.gui_info['SORT_WORD_LIST'])
        print(f'worksheet_list: {worksheet_list}')
        return worksheet_list


    # ----------------------------------------------------------------------------------
    # buttonを定義

    def _action_btn(self, name_in_btn: str, action_func: Callable):
        action_btn = QPushButton(name_in_btn)
        action_btn.clicked.connect(action_func)
        return action_btn


    # ----------------------------------------------------------------------------------
    # ドロップダウンメニューにWorksheet情報を更新

    def _update_dropdown_menu(self, worksheet_list: List):
        self.dropdown_menu.clear()  # 既存で残ってしまってるWorksheetデータをクリアする
        self.dropdown_menu.addItem("--選択してください--")
        self.dropdown_menu.addItems(worksheet_list)
        self.dropdown_menu.setEnabled(True)
        self._set_error_msg("")


    # ----------------------------------------------------------------------------------
    # スプシURLからWorksheetを取得してドロップダウンメニューにわたす

    def _on_url_input_finished(self):
        sheet_url = self.gss_url_input.text().strip()

        if not sheet_url:
            self._set_error_msg("Spreadsheet URLが入力されていません")
            return

        try:
            # URLからWorksheetを取得する
            worksheet_list = self._get_worksheet_list(sheet_url=sheet_url)

            # ドロップダウンメニューに取得したWorksheetを反映させる
            self._update_dropdown_menu(worksheet_list=worksheet_list)

        except Exception as e:
            self._set_error_msg(f"Worksheetの取得に失敗しました: {e}")
            print(f"Worksheetの取得に失敗しました: {e}")


    # ----------------------------------------------------------------------------------
    # スプシデータをdf

    def _get_gss_df(self, worksheet_name: str):
        gss_read = GetDataGSSAPI()
        sheet_url = self.gss_url_input.text()  # 今のスプシの入力された値
        gss_df = gss_read._get_gss_df_to_gui(gui_info=self.gui_info, sheet_url=sheet_url, worksheet_name=worksheet_name)
        return gss_df


    # ----------------------------------------------------------------------------------
    # ドロップダウンメニューで選択した値を返す

    def _on_folder_check(self):
        select_worksheet = self.dropdown_menu.currentText()
        if select_worksheet == "--選択してください--":
            return None

        error_msg = self._folder_check(worksheet_name=select_worksheet)
        if error_msg:
            self._set_error_msg(error_msg)
            return None

        self._set_error_msg(None)
        return select_worksheet

    # ----------------------------------------------------------------------------------
