# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# export PYTHONPATH="/Users/nyanyacyan/Desktop/project_file/domain_search/installer/src"

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import unicodedata, threading, time, _asyncio
from datetime import datetime, timedelta
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
from src.method.base.GUI.set_status_display import StatusManager



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
        self.radio_btn_form = UpdateSelect(gui_info=gui_info)
        self.action_btn_form = ActionBtn(gui_info=gui_info, process_func=process_func, cancel_func=cancel_func)
        self.status_label = StatusManager()

        # レイアウトに追加
        self.layout.addWidget(self.user_info_form)
        self.layout.addWidget(self.interval_form)
        self.layout.addWidget(self.uptime_form)
        self.layout.addWidget(self.radio_btn_form)
        self.layout.addWidget(self.action_btn_form)
        self.layout.addWidget(self.status_label)


        # フラグをセット（フラグを立てる場合には self.stop_event.set() を実施）
        self.stop_event = threading.Event()
        self.update_complete_event = threading.Event()

        # ここでupdateの要否を確認→bool
        self.update_bool = True  # 初期値を設定


    # ----------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------
    # start_event

    def start_event(self):
        try:
            # STARTボタンを押下したときのradio_btnを取得
            self.update_bool = self.radio_btn_form.get_update_info()

            if self.update_bool:
                self._update_task()

            user_info = self.user_info_form.get_user_info()
            interval_info = self.interval_form.get_interval_info()
            uptime_info = self.uptime_form.get_uptime_info()

            self.loop_process(user_info, interval_info, uptime_info)

        except Exception as e:
            self.status_label.update_status(msg=f"エラー: {e}", color="red")


    # ----------------------------------------------------------------------------------
    # 日付が変わるまでの時間を算出して待機する

    async def _monitor_date_change(self):
        # ストップフラグがis_setされるまでループ処理
        while not self.stop_event.is_set():
            now = datetime.now()
            next_day = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)

            total_sleep_time = (next_day - now).total_seconds()

            await _asyncio.sleep(total_sleep_time)

            if self.update_bool:
                self._update_task()


    # ----------------------------------------------------------------------------------
    # 更新処理

    def _update_task(self):
        # 出品処理を停止
        self.stop_event.set()

        # 更新処理ストップフラグをクリア→更新処理が実施できるようにする
        self.update_complete_event.clear()

        # ステータス変更
        self.status_label.update_status(msg="更新処理中...", color="black")

        # TODO 更新処理を実施
        self.update_process()

        # 更新作業完了フラグを立てる
        self.update_complete_event.set()

        self.status_label.update_status(msg="更新処理が完了しました。", color="blue")


    # ----------------------------------------------------------------------------------
    # 出品処理

    def loop_process(self):
        # ストップフラグがis_setされるまでループ処理
        while not self.stop_event.is_set():
            self.status_label.update_status(msg="更新処理が完了しました。", color="blue")

            # 更新作業が完了するまで待機
            self.update_complete_event.wait()

            if self.stop_event.is_set():
                break

            self.status_label.update_status(msg="実行処理中...", color="blue")

            # TODO 処理を実施
            self.process()




    # ----------------------------------------------------------------------------------
    # キャンセル処理

    def _cancel_process(self):
        self.status_label.update_status(msg="出品処理を停止ボタンが押されました", color="red")

        # 出品処理を停止
        self.stop_event.set()

        # 更新完了されたフラグもリセット
        self.update_complete_event.clear()

        self.status_label.update_status(msg="出品処理を停止しました。", color="red")


    # ----------------------------------------------------------------------------------

