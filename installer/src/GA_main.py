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
from src.method.base.GUI.set_radio_btn import RadioSelect
from src.method.base.GUI.set_action_btn import ActionBtn
from src.method.base.GUI.set_status_display import StatusManager
from src.method.base.time_manager import TimeManager



# ----------------------------------------------------------------------------------
# **********************************************************************************


class MainApp(QWidget):
    def __init__(self, gui_info: Dict, worksheet_info: List, process_func: Callable):
        super().__init__()

        self.windowTitle(gui_info['MAIN_WINDOW_TITLE'])

        # メインレイアウトの設定
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # 各GUIパーツを追加
        self.user_info_form = UserInfoForm(gui_info=gui_info, worksheet_info=worksheet_info)
        self.interval_form = IntervalTimeForm(gui_info=gui_info)
        self.uptime_form = SetUptime(gui_info=gui_info)
        self.radio_btn_form = RadioSelect(gui_info=gui_info)
        self.action_btn_form = ActionBtn(gui_info=gui_info, process_func=self.start_event, cancel_func=self.cancel_event)
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

        # メインの処理を受け取る
        self.process_func = process_func

        # ここでupdateの要否を確認→bool
        self.update_bool = True  # 初期値を設定

        # インスタンス
        self.time_manager = TimeManager()


    ####################################################################################
    # start_event

    def start_event(self):
        try:
            # STARTボタンを押下したときのradio_btnを取得
            self.update_bool = self.radio_btn_form.get_radio_info()

            # 更新処理がある場合には実施
            if self.update_bool:
                self._update_task()

            user_info = self.user_info_form.get_user_info()
            interval_info = self.interval_form.get_interval_info()
            uptime_info = self.uptime_form.get_uptime_info()

            # 終了時間の監視taskをスタート
            threading.Thread(target=self._monitor_end_time, args=(uptime_info,), daemon=True).start()

            # メイン処理実施
            self.loop_process(user_info=user_info, interval_info=interval_info, uptime_info=uptime_info)

        except Exception as e:
            self.status_label.update_status(msg=f"エラー: {e}", color="red")


    ####################################################################################

    ####################################################################################
    # キャンセル処理

    def cancel_event(self):
        self.status_label.update_status(msg="出品処理を停止中です。", color="red")

        # 出品処理を停止
        self.stop_event.set()

        # 更新完了されたフラグもリセット
        self.update_complete_event.clear()

        self.status_label.update_status(msg="待機中...", color="red")


    ####################################################################################
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
    # 設定している時間になったら設定したtaskを実行

    def _monitor_end_time(self, uptime_info: Dict[str, timedelta]):
        try:
            end_diff = uptime_info['end_diff']

            if end_diff.total_seconds() > 0:
                # 終了時間まで待機
                threading.Timer(end_diff.total_seconds(), self._end_time_task).start()

        except Exception as e:
            self.status_label.update_status(msg=f"終了時間の設定などによるエラー: {e}", color="red")


    # ----------------------------------------------------------------------------------
    # 終了時に行うtask

    def _end_time_task(self):
            # 処理を停止
            self.stop_event.set()
            self.status_label.update_status(msg="終了時間に達したため処理を停止しました。", color="red")


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

    def loop_process(self, user_info: Dict, interval_info: Dict, uptime_info: Dict[str, timedelta]):

        # 開始時間まで待機
        start_diff = uptime_info['start_diff']
        time.sleep(start_diff.total_seconds())


        # ストップフラグがis_setされるまでループ処理
        while not self.stop_event.is_set():
            self.status_label.update_status(msg="更新処理が完了しました。", color="blue")

            # 更新作業が完了するまで待機
            self.update_complete_event.wait()

            if self.stop_event.is_set():
                break

            self.status_label.update_status(msg="実行処理中...", color="blue")

            # 処理を実施
            self.process_func(id_text=user_info['id'], pass_text=user_info['pass'], worksheet_name=user_info['worksheet'])

            # 設定した待機をランダムで実行
            self.time_manager._random_sleep(random_info=interval_info)


    # ----------------------------------------------------------------------------------






