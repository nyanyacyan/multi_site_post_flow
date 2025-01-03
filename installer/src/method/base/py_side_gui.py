# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# export PYTHONPATH="/Users/nyanyacyan/Desktop/project_file/domain_search/installer/src"


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import unicodedata, threading, time
from typing import Dict, Callable, List, Any
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QDateTimeEdit, QMessageBox, QLabel, QGroupBox, QComboBox
from PySide6.QtCore import QDateTime, QRegularExpression
from PySide6.QtGui import QIntValidator, QRegExpValidator

# 自作モジュール
from base.utils import Logger



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
        validator = QRegExpValidator(QRegularExpression("[a-zA-Z0-9]+"))
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
# **********************************************************************************


class IntervalTimeForm(QGroupBox):
    def __init__(self, gui_info: Dict):
        super().__init__(gui_info['INTERVAL_TIME_GROUP_TITLE'])

        # レイアウトを設定
        self.setLayout(self._input_interval_time_group(gui_info=gui_info))


####################################################################################
# 値を取得

    def get_interval_info(self):
        try:
            min_value = self.interval_min_text.text().strip()
            max_value = self.interval_max_text.text().strip()

            if not min_value:
                self.error_label.setText("下限が入力されてません")
                raise ValueError("下限が入力されてません")

            if not max_value:
                self.error_label.setText("上限が入力されてません")
                raise ValueError("上限が入力されてません")

            if int(min_value) > int(max_value):
                self.error_label.setText("最小時間は最大時間以下である必要があります")
                raise ValueError("最小時間は最大時間以下である必要があります")

            # エラーがない場合はメッセージをクリア
            self.error_label.setText("")

            return {
                "min": min_value,
                "max": max_value,
            }

        except ValueError as e:
            self.error_label.setText(str(e))
            raise


####################################################################################

####################################################################################
# 実施間隔を入力

    def _input_interval_time_group(self, gui_info: Dict):
        interval_time_group_box = QGroupBox(gui_info['INTERVAL_TIME_GROUP_TITLE'])
        interval_time_group_layout = QVBoxLayout()  # 縦レイアウト

        # interval_minを入力
        self.interval_min_text = self._create_input_int_field(gui_info['INPUT_EXAMPLE_INTERVAL_MIN'])
        input_between_label = QLabel(gui_info['INPUT_BETWEEN_LABEL'])

        self.interval_max_text = self._create_input_int_field(gui_info['INPUT_EXAMPLE_INTERVAL_MAX'])
        input_last_label = QLabel(gui_info['INPUT_LAST_LABEL'])

        # 横に並びに配置
        interval_time_layout = QHBoxLayout()  # 横レイアウト
        interval_time_layout.addWidget(self.interval_min_text)
        interval_time_layout.addWidget(input_between_label)
        interval_time_layout.addWidget(self.interval_max_text)
        interval_time_layout.addWidget(input_last_label)

        # グループレイアウトに追加したいレイアウトいれる
        interval_time_group_layout.addLayout(interval_time_layout)

        # errorラベルを追加
        self.error_label = self._error_label()
        interval_time_group_layout.addWidget(self.error_label)

        # 定義したレイアウトをセット
        interval_time_group_box.setLayout(interval_time_group_layout)

        return interval_time_group_box


####################################################################################
    # ----------------------------------------------------------------------------------
    # ID入力欄→passwordを渡せば非表示

    def _create_input_int_field(self, input_example: str):
        input_field = QLineEdit()
        input_field.setPlaceholderText(input_example)  # input_exampleは入力例

        # 半角のみを許可する正規表現を設定
        validator = QRegExpValidator(QRegularExpression("[0-9]+"))
        input_field.setValidator(validator)

        return input_field


    # ----------------------------------------------------------------------------------
    # スプシからのデータを受けたドロップダウンメニュー

    def _error_label(self):
        error_label = QLabel("")
        error_label.setStyleSheet("color: red;")
        return error_label


    # ----------------------------------------------------------------------------------
# **********************************************************************************


class SetUptime(QGroupBox):
    def __init__(self, gui_info: Dict):
        super().__init__(gui_info['INTERVAL_TIME_GROUP_TITLE'])

        # レイアウトを設定
        self.setLayout(self._input_interval_time_group(gui_info=gui_info))


####################################################################################
# 値を取得

    def get_uptime_info(self):
        try:
            start_datetime_value = self.interval_min_text.text().strip()
            end_datetime_value = self.interval_max_text.text().strip()

            if not start_datetime_value:
                self.error_label.setText("下限が入力されてません")
                raise ValueError("下限が入力されてません")

            if not end_datetime_value:
                self.error_label.setText("上限が入力されてません")
                raise ValueError("上限が入力されてません")

            if int(start_datetime_value) > int(end_datetime_value):
                self.error_label.setText("最小時間は最大時間以下である必要があります")
                raise ValueError("最小時間は最大時間以下である必要があります")

            # エラーがない場合はメッセージをクリア
            self.error_label.setText("")

            return {
                "min": start_datetime_value,
                "max": end_datetime_value,
            }

        except ValueError as e:
            self.error_label.setText(str(e))
            raise


####################################################################################

####################################################################################





    # カレンダーから日時を選択
    # 実行されて初めて入力内容が確認できる→デバッグはこの関数が実行された後に
    # 値は見えるやすように処理する必要がある→ .dateTime().toString("yyyy-MM-dd HH:mm:ss")

    def _set_datetime(self, input_example: str):
        # 入力する部分のラベル
        label = QLabel(input_example, self)
        self.main_layout.addWidget(label)  # 入力する部分をメインフレームと結合

        edit_datetime = QDateTimeEdit(self)
        edit_datetime.setDateTime(QDateTime.currentDateTime())  # 現時刻をデフォルトにする
        edit_datetime.setCalendarPopup(True)  # カレンダー表示を有効化
        self.main_layout.addWidget(edit_datetime)  # レイアウトに追加
        return edit_datetime


    # ----------------------------------------------------------------------------------
    # buttonを定義

    def _action_btn(self, display_btn_name: str, action_func: Callable):
        action_btn = QPushButton(display_btn_name)
        action_btn.clicked.connect(action_func)  # 実行する処理
        return action_btn


    # ----------------------------------------------------------------------------------
