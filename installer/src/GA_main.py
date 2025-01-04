# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# export PYTHONPATH="/Users/nyanyacyan/Desktop/project_file/domain_search/installer/src"


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import unicodedata, threading, time, _asyncio
from typing import Dict, Callable, List, Any
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QDateTimeEdit, QRadioButton, QLabel, QGroupBox, QComboBox
from PySide6.QtCore import QDateTime, QRegularExpression
from PySide6.QtGui import QIntValidator, QRegExpValidator

# 自作モジュール
from src.method.base.utils import Logger
from installer.src.method.base.GUI.set_user_info import UserInfoForm
from installer.src.method.base.GUI.set_interval_time import IntervalTimeForm
from src.method.base.GUI.set_uptime import SetUptime
from src.method.base.GUI.set_radio_btn import UpdateSelect
from src.method.base.GUI.set_action_btn import ActionBtn



# ----------------------------------------------------------------------------------
# **********************************************************************************


class MainApp(QWidget):
    def __init__(self, gui_info: Dict, worksheet_info: List):
        super().__init__()

        self.windowTitle(gui_info['MAIN_WINDOW_TITLE'])

        # メインレイアウトの設定
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # 各GUIパーツを追加
        self.user_info_form = UserInfoForm(gui_info=gui_info, worksheet_info=worksheet_info)
        self.interval_form = IntervalTimeForm(gui_info=gui_info)
        self.uptime_form = SetUptime(gui_info=gui_info)
        self.radio_btn = UpdateSelect(gui_info=gui_info)
        self.action_btn = ActionBtn(gui_info=gui_info, process_func=process_func, cancel_func=cancel_func)

        # レイアウトに追加
        self.layout.addWidget(self.user_info_form)
        self.layout.addWidget(self.interval_form)
        self.layout.addWidget(self.uptime_form)
        self.layout.addWidget(self.radio_btn)
        self.layout.addWidget(self.action_btn)


        # フラグをセット（フラグを立てる場合には self.stop_event.set() を実施）
        self.stop_event = threading.Event()
