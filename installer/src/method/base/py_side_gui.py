# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# export PYTHONPATH="/Users/nyanyacyan/Desktop/project_file/domain_search/installer/src"


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import unicodedata, threading, time, _asyncio
from typing import Dict, Callable, List, Any
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QDateTimeEdit, QRadioButton, QLabel, QGroupBox, QComboBox
from PySide6.QtCore import QDateTime, QRegularExpression
from PySide6.QtGui import QIntValidator, QRegularExpressionValidator

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
        interval_time_group_layout = QVBoxLayout()

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

        return interval_time_group_layout


    ####################################################################################
    # ----------------------------------------------------------------------------------
    # ID入力欄→passwordを渡せば非表示

    def _create_input_int_field(self, input_example: str):
        input_field = QLineEdit()
        input_field.setPlaceholderText(input_example)  # input_exampleは入力例

        # 半角のみを許可する正規表現を設定
        validator = QRegularExpressionValidator(QRegularExpression("[0-9]+"))
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
        self.setLayout(self._create_uptime_input_group(gui_info=gui_info))


    ####################################################################################
    # 値を取得

    def get_uptime_info(self):
        try:
            uptime_start_time = self.uptime_start_time.dateTime()
            uptime_end_time = self.uptime_end_time.dateTime()
            if not uptime_start_time:
                self.error_label.setText("開始日時の設定がされてません")
                raise ValueError("開始日時の設定がされてません")

            if not uptime_end_time:
                self.error_label.setText("終了日時の設定がされてません")
                raise ValueError("終了日時の設定がされてません")

            if uptime_start_time >= uptime_end_time:
                self.error_label.setText("開始日時は終了日時より前に設定する必要があります")
                raise ValueError("開始日時は終了日時より前に設定する必要があります")

            # エラーがない場合はメッセージをクリア
            self.error_label.setText("")

            return {
                "uptime_start_time": uptime_start_time,
                "uptime_end_time": uptime_end_time,
            }

        except ValueError as e:
            self.error_label.setText(str(e))
            raise


    ####################################################################################
    # 開始と終了の時刻入力

    def _create_uptime_input_group(self, gui_info: Dict):
        uptime_layout = QVBoxLayout()

        # start_uptimeを入力
        input_start_uptime_label = QLabel(gui_info['INPUT_START_UPTIME_TITLE'])
        self.uptime_start_time = self._set_datetime()

        # start_uptimeのレイアウト作成
        start_uptime_layout = QHBoxLayout()  # 横レイアウト
        start_uptime_layout.addWidget(input_start_uptime_label)
        start_uptime_layout.addWidget(self.uptime_start_time)

        # start_uptimeグループに追加
        uptime_layout.addLayout(start_uptime_layout)

        # end_uptimeを入力
        input_last_label = QLabel(gui_info['INPUT_END_UPTIME_TITLE'])
        self.uptime_end_time = self._set_datetime()

        # end_uptimeのレイアウト作成
        end_uptime_layout = QHBoxLayout()  # 横レイアウト
        end_uptime_layout.addWidget(input_last_label)
        end_uptime_layout.addWidget(self.uptime_end_time)

        # end_uptimeをグループに追加
        uptime_layout.addLayout(end_uptime_layout)

        # errorラベルを追加
        self.error_label = self._error_label()
        uptime_layout.addWidget(self.error_label)

        return uptime_layout


    ####################################################################################


    # カレンダーから日時を選択
    # 実行されて初めて入力内容が確認できる→デバッグはこの関数が実行された後に
    # 値は見えるやすように処理する必要がある→ .dateTime().toString("yyyy-MM-dd HH:mm:ss")

    def _set_datetime(self):
        edit_datetime = QDateTimeEdit(self)
        edit_datetime.setDateTime(QDateTime.currentDateTime())  # 現時刻をデフォルトにする
        edit_datetime.setCalendarPopup(True)  # カレンダー表示を有効化
        return edit_datetime


    # ----------------------------------------------------------------------------------
    # スプシからのデータを受けたドロップダウンメニュー

    def _error_label(self):
        error_label = QLabel("")
        error_label.setStyleSheet("color: red;")
        return error_label


    # ----------------------------------------------------------------------------------
# **********************************************************************************


class UpdateSelect(QGroupBox):
    def __init__(self, gui_info: Dict) -> None:
        super().__init__(gui_info['UPDATE_SELECT_GROUP_TITLE'])

        # レイアウトを設定
        self.setLayout(self._create_update_select_group(gui_info=gui_info))


    ####################################################################################
    # 値を取得

    def get_update_info(self):
        if self.update_true.isChecked():
            return True
        else:
            return False


    ####################################################################################
    # ラジオボタンの設計

    def _create_update_select_group(self, gui_info: Dict):
        update_layout = QVBoxLayout()

        # ラジオボタンを設置
        self.update_true = QRadioButton(gui_info['RADIO_BTN_TRUE_TITLE'])
        self.update_false = QRadioButton(gui_info['RADIO_BTN_FALSE_TITLE'])

        # デフォルトでチェックを入れておく
        self.update_true.setChecked(True)

        # end_updateのレイアウト作成
        update_select_layout = QHBoxLayout()  # 横レイアウト
        update_select_layout.addWidget(self.update_true)
        update_select_layout.addWidget(self.update_false)

        # end_updateをグループに追加
        update_layout.addLayout(update_select_layout)

        return update_layout


    ####################################################################################

# **********************************************************************************


class ActionBtn(QGroupBox):
    def __init__(self, gui_info: Dict, process_func: Callable, cancel_func: Callable):
        super().__init__()

        # 処理関数をここで所持
        self.process_func = process_func
        self.cancel_func = cancel_func

        # レイアウトを設定
        self.setLayout(self._create_action_btn_group(gui_info=gui_info))


    ####################################################################################
    # アクションを実行

    def _create_action_btn_group(self, gui_info: Dict, process_func: Callable, cancel_func: Callable):
        action_btn_layout = QVBoxLayout()

        # ボタンを設置
        self.process_btn = self._action_btn(name_in_btn=gui_info['PROCESS_BTN_NAME'], action_func=process_func)
        self.cancel_btn = self._action_btn(name_in_btn=gui_info['CANCEL_BTN_NAME'], action_func=cancel_func)


        # end_updateのレイアウト作成
        btn_layout = QHBoxLayout()  # 横レイアウト
        btn_layout.addWidget(self.process_btn)
        btn_layout.addWidget(self.cancel_btn)

        # end_updateをグループに追加
        action_btn_layout.addLayout(btn_layout)

        # status_labelを追加
        self.status_label = self._status_label()
        action_btn_layout.addWidget(self.status_label)

        # 各ボタンのクリックイベントを定義
        self.process_btn.clicked.connect(self._start_processing)
        self.cancel_btn.clicked.connect(self._cancel_processing)

        return action_btn_layout


    ####################################################################################
    # ----------------------------------------------------------------------------------
    # buttonを定義

    def _action_btn(self, name_in_btn: str):
        action_btn = QPushButton(name_in_btn)
        return action_btn


    # ----------------------------------------------------------------------------------
    # スプシからのデータを受けたドロップダウンメニュー

    def _status_label(self):
        status_label = QLabel("待機中...")
        status_label.setStyleSheet("color: green;")
        return status_label


    # ----------------------------------------------------------------------------------
    # process_btnを実行した際のアクション

    def _start_processing(self):
        # ラベルにコメントを追記
        self.status_label.setText("出品処理中...")

        self.process_btn.setEnabled(False)  # 開始ボタンを押せないSTS変更
        self.cancel_btn.setEnabled(True)  # キャンセルボタンを押せるSTS変更

        self.process_func()


    # ----------------------------------------------------------------------------------
    # cancel_btnを実行した際のアクション

    def _cancel_processing(self):

        self.status_label.setText("処理を中断してます...")

        self.process_btn.setEnabled(True)  # 開始ボタンを押せる状態にSTS変更
        self.cancel_btn.setEnabled(False)  # キャンセルボタンを押せないSTS変更

        self.cancel_func()

        # キャンセル処理完了後に「待機中」に戻す
        self.status_label.setText("待機中...")

    # ----------------------------------------------------------------------------------
# **********************************************************************************


class StatusManager(QGroupBox):
    def __init__(self):
        super().__init__()

        self.status_label = QLabel("待機中...")
        self.status_label.setStyleSheet("color: green;")

        # レイアウトを設定
        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        self.setLayout(layout)


    ####################################################################################
    # アクションを実行

    def update_status(self, msg: str, color: str= "green"):
        self.status_label.setText(msg)
        self.status_label.setStyleSheet(f"color: {color};")


    ####################################################################################
