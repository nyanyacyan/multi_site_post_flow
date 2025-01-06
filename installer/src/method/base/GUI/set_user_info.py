# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# export PYTHONPATH="/Users/nyanyacyan/Desktop/project_file/domain_search/installer/src"


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
from typing import Dict, List
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLineEdit, QLabel, QGroupBox, QComboBox
from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator

# 自作モジュール



# ----------------------------------------------------------------------------------
# **********************************************************************************
# ユーザー情報のグループを設定

class UserInfoForm(QGroupBox):
    def __init__(self, gui_info: Dict, worksheet_info: List):
        super().__init__(gui_info['USER_INPUT_TITLE'])  # タイトルを設定

        # レイアウトを設定
        self.setLayout(self._create_user_info_layout(gui_info=gui_info, worksheet_info=worksheet_info))


    ####################################################################################
    # 値を取得

    def get_user_info(self):
        try:
            id_text = self.id_input.text().strip()
            pass_text = self.pass_input.text().strip()
            select_dropdown_text = self.dropdown_input.currentText()

            if not id_text:
                self.error_label.setText("IDが入力されていません")
                raise ValueError("IDが入力されていません")

            if not pass_text:
                self.error_label.setText("PASSが入力されていません")
                raise ValueError("PASSが入力されていません")

            if select_dropdown_text == "選択してください":
                self.error_label.setText("Worksheetが選択されてません")
                raise ValueError("Worksheetが選択されていません")

            # エラーがない場合はメッセージをクリア
            self.error_label.setText("")

            return {
                "id": id_text,
                "pass": pass_text,
                "worksheet": select_dropdown_text
            }

        except ValueError as e:
            self.error_label.setText(str(e))
            raise


    ####################################################################################

    ####################################################################################
    # ユーザー入力欄のグループ

    def _create_user_info_layout(self, gui_info: Dict, worksheet_info: List):
        group_layout = QVBoxLayout()

        # ID入力
        id_label = QLabel(gui_info['ID_LABEL'])
        self.id_input = self._create_input_field(gui_info['INPUT_EXAMPLE_ID'])

        # idのレイアウト作成
        id_layout = QHBoxLayout()  # 横レイアウト
        id_layout.addWidget(id_label)
        id_layout.addWidget(self.id_input)

        # グループにidレイアウトを追加
        group_layout.addLayout(id_layout)


        # Pass入力
        pass_label = QLabel(gui_info['PASS_LABEL'])
        self.pass_input = self._create_input_field(gui_info['INPUT_EXAMPLE_PASS'], is_password=True)

        # Passのレイアウト作成
        pass_layout = QHBoxLayout()  # 横レイアウト
        pass_layout.addWidget(pass_label)
        pass_layout.addWidget(self.pass_input)

        # グループにPassレイアウトを追加
        group_layout.addLayout(pass_layout)


        # Worksheetを選択
        dropdown_label = QLabel(gui_info['DROPDOWN_LABEL'])
        self.dropdown_input = self._dropdown_menu(dropdown_menu_list=worksheet_info)

        # worksheetのレイアウト作成
        dropdown_layout = QHBoxLayout()  # 横レイアウト
        dropdown_layout.addWidget(dropdown_label)
        dropdown_layout.addWidget(self.dropdown_input)

        # errorラベルを追加
        self.error_label = self._error_label()
        group_layout.addWidget(self.error_label)

        # グループにworksheetレイアウトを追加
        group_layout.addLayout(dropdown_layout)

        return group_layout


    ####################################################################################
    # ----------------------------------------------------------------------------------
    # ID入力欄→passwordを渡せば非表示

    def _create_input_field(self, input_example: str, is_password: bool = False):
        input_field = QLineEdit()
        input_field.setPlaceholderText(input_example)  # input_exampleは入力例

        # 半角のみを許可する正規表現を設定
        validator = QRegularExpressionValidator(QRegularExpression("[a-zA-Z0-9]+"))
        input_field.setValidator(validator)

        if is_password:
            input_field.setEchoMode(QLineEdit.Password)
        return input_field


    # ----------------------------------------------------------------------------------
    # スプシからのデータを受けたドロップダウンメニュー

    def _dropdown_menu(self, dropdown_menu_list: List):
        dropdown_menu = QComboBox()
        dropdown_menu.addItem("選択してください")  # 初期値を設定
        dropdown_menu.addItems(dropdown_menu_list)
        return dropdown_menu


    # ----------------------------------------------------------------------------------


    def _error_label(self):
        error_label = QLabel("")
        error_label.setStyleSheet("color: red;")
        return error_label


    # ----------------------------------------------------------------------------------
