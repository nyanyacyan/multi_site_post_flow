# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# export PYTHONPATH="/Users/nyanyacyan/Desktop/project_file/domain_search/installer/src"


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import asyncio, threading, time
from typing import Dict, Callable
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QDateTimeEdit, QMessageBox
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
# 一連の流れ


class PySideGui(QWidget):
    def __init__(self, main_window_title: str):
        super().__init__()
        # windowタイトル
        self.setWindowTitle(main_window_title)

        # メインレイアウト
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)  # メインフレームとして定義




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
    # カレンダーから日時を選択
    # 実行されて初めて入力内容が確認できる→デバッグはこの関数が実行された後に
    # 値は見えるやすように処理する必要がある→ .dateTime().toString("yyyy-MM-dd HH:mm:ss")

    def _set_datetime(self):
        edit_datetime = QDateTimeEdit(self)
        edit_datetime.setDateTime(QDateTime.currentDateTime())  # 現時刻をデフォルトにする
        edit_datetime.setCalendarPopup(True)  # カレンダー表示を有効化
        self.main_layout.addWidget(edit_datetime)  # レイアウトに追加
        return edit_datetime


    # ----------------------------------------------------------------------------------


    # ----------------------------------------------------------------------------------
