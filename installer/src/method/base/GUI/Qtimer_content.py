# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# export PYTHONPATH="/Users/nyanyacyan/Desktop/project_file/domain_search/installer/src"


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
from datetime import timedelta
from typing import Dict
from PySide6.QtWidgets import QLabel
from PySide6.QtCore import QObject, QTimer, Signal


# 自作モジュール
from method.base.utils import Logger
from method.base.GUI.set_status_display import StatusManager


# ----------------------------------------------------------------------------------
# **********************************************************************************


class CountDownQTimer(QObject):
    countdown_signal = Signal(int)
    def __init__(self, label: QLabel, uptime_info: Dict[int, int]):
        super().__init__()
        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

        self.label = label  # GUIのラベルを更新する

        # インスタンス
        self.status_label = StatusManager()

        self.countdown_timer = QTimer(self)
        self.uptime_info = uptime_info


    ####################################################################################


    def countdown_event(self):
        self.logger.debug(f'self.uptime_info: {self.uptime_info}')
        if 'start_diff' not in self.uptime_info:
            self.label.setText("カウントダウン情報が不足しています")
            return

        wait_seconds = int(self.uptime_info['start_diff'])
        self.logger.debug(f'wait_seconds: {wait_seconds}')
        if wait_seconds <= 0:
            self.label.setText("待機時間なし")
            return

        self.logger.debug(f"カウントダウン開始: {wait_seconds} 秒")
        self.countdown_timer.timeout.disconnect()  # 古い接続を解除してリセット
        self.countdown_timer.setInterval(1000)  # 1秒ごとに発火
        self.countdown_timer.timeout.connect(self.update_label)
        self.countdown_timer.start()



    ####################################################################################
    # ----------------------------------------------------------------------------------


    def update_label(self):
        self.logger.debug(f'self.uptime_info: {self.uptime_info}')
        wait_seconds = int(self.uptime_info['start_diff'])
        if wait_seconds > 0:
            minutes, seconds = divmod(wait_seconds, 60)
            msg = f"残り時間: {minutes} 分 {seconds} 秒" if minutes > 0 else f"残り時間: {seconds} 秒"
            self.logger.debug(f'msg: {msg}')
            self.label.setText(msg)
            self.uptime_info['start_diff'] -= 1  # 残り時間を減少
            self.logger.debug(f"更新された待機時間: {self.uptime_info['start_diff']}")
        else:
            self.label.setText("カウントダウン終了")
            self.countdown_timer.stop()


    # ----------------------------------------------------------------------------------
    # uptime_info を更新する

    def update_uptime_info(self, uptime_info: Dict[str, timedelta]):
        self.logger.debug(f"uptime_info を更新: {uptime_info}")
        self.uptime_info = uptime_info


    # ----------------------------------------------------------------------------------
