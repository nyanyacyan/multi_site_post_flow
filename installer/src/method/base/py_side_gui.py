# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# export PYTHONPATH="/Users/nyanyacyan/Desktop/project_file/domain_search/installer/src"


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import asyncio, threading, time
from typing import Dict, Callable, List
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QDateTimeEdit, QMessageBox, QLabel, QGroupBox, QComboBox
from PySide6.QtCore import QDateTime

# 自作モジュール
from base.utils import Logger
from base.chrome import ChromeManager
from base.loginWithId import SingleSiteIDLogin
from base.seleniumBase import SeleniumBasicOperations
from base.spreadsheetRead import GetDataGSSAPI
from base.elementManager import ElementManager
from base.decorators import Decorators
from base.jumpTargetPage import JumpTargetPage
from base.time_manager import TimeManager

# const
from const_element import LoginInfo, GssInfo, SellInfo

deco = Decorators()

# ----------------------------------------------------------------------------------
# **********************************************************************************


class PySideGui(QWidget):
    def __init__(self, gui_info: Dict, worksheet_info: List):
        super().__init__()
        # GUIの配置

        # windowタイトル
        self.setWindowTitle(gui_info['main_window_title'])

        # メインレイアウト
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)  # メインフレームとして定義

        # 入力ボックスを作成して追加
        input_group = self._input_user_info_group(gui_info, worksheet_info)
        self.main_layout.addWidget(input_group)




    ####################################################################################
    # ----------------------------------------------------------------------------------
    # buttonを定義

    def _action_btn(self, display_btn_name: str, action_func: Callable):
        action_btn = QPushButton(display_btn_name)
        action_btn.clicked.connect(action_func, self)  # 実行する処理
        return action_btn


    # ----------------------------------------------------------------------------------
    # ID入力欄（入力文字表示）

    def _input_section(self, input_example: str):
        input_field = QLineEdit()
        input_field.setPlaceholderText(input_example)  # input_exampleは入力例
        return input_field


    # ----------------------------------------------------------------------------------
    # pass入力（入力文字を非表示）

    def _pass_input_section(self, input_example: str):
        input_field = QLineEdit()
        input_field.setPlaceholderText(input_example)  # input_exampleは入力例
        input_field.setEchoMode(QLineEdit.Password)
        return input_field


    # ----------------------------------------------------------------------------------
    # スプシからのデータを受けたドロップダウンメニュー

    def _dropdown_menu(self, dropdown_menu_list: List):
        dropdown_menu = QComboBox()
        dropdown_menu.addItems(dropdown_menu_list)
        return dropdown_menu


    # ----------------------------------------------------------------------------------
    # ユーザー入力欄のグループ

    def _input_user_info_group(self, gui_info: Dict, worksheet_info: List):
        # グループとしてのボックスを定義
        group_box = QGroupBox(gui_info['USER_INPUT_TITLE'])
        group_layout = QVBoxLayout()  # 縦レイアウト

        # ID入力
        id_label = QLabel(gui_info['ID_LABEL'])
        id_input = self._input_section(gui_info['INPUT_EXAMPLE_ID'])

        # idのレイアウト作成
        id_layout = QHBoxLayout()  # 横レイアウト
        id_layout.addWidget(id_label)
        id_layout.addWidget(id_input)

        # グループにidレイアウトを追加
        group_layout.addLayout(id_layout)


        # Pass入力
        pass_label = QLabel(gui_info['PASS_LABEL'])
        pass_input = self._pass_input_section(gui_info['INPUT_EXAMPLE_PASS'])

        # Passのレイアウト作成
        pass_layout = QHBoxLayout()  # 横レイアウト
        pass_layout.addWidget(pass_label)
        pass_layout.addWidget(pass_input)

        # グループにPassレイアウトを追加
        group_layout.addLayout(pass_layout)


        # Worksheetを選択
        dropdown_label = QLabel(gui_info['DROPDOWN_LABEL'])
        dropdown_input = self._dropdown_menu(dropdown_menu_list=worksheet_info)

        # worksheetのレイアウト作成
        dropdown_layout = QHBoxLayout()  # 横レイアウト
        dropdown_layout.addWidget(dropdown_label)
        dropdown_layout.addWidget(dropdown_input)

        # グループにworksheetレイアウトを追加
        group_layout.addLayout(dropdown_layout)


        # レイアウトをグループBOXに設定
        group_box.setLayout(group_layout)
        return group_box


    # ----------------------------------------------------------------------------------
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





    # ----------------------------------------------------------------------------------
