# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# export PYTHONPATH="/Users/nyanyacyan/Desktop/project_file/domain_search/installer/src"


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import threading
from typing import Dict, Callable
from PySide6.QtWidgets import QLabel
from PySide6.QtCore import QObject, QTimer


# 自作モジュール
from method.base.utils import Logger
from method.base.event.update_label import UpdateLabel
from method.base.event.loop_process import LoopProcess
from method.base.GUI.Qtimer_content import CheckFlag


# ----------------------------------------------------------------------------------
# **********************************************************************************


class CountdownEvent(QObject):
    def __init__(self):
        super().__init__()
        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

        # Timerの設置
        self.countdown_timer = QTimer(self)

        # インスタンス
        self.update_label = UpdateLabel()
        self.loop_process = LoopProcess()
        self.check_flag = CheckFlag()


    ####################################################################################
    # 開始時間までの待機イベント

    def entry_event(self, uptime_info: Dict, label: QLabel, start_event_flag: threading.Event, event_func: Callable):
        self.logger.info(f'開始ボタンが押されました!\nuptime_info: {uptime_info}')

        if 'start_diff' not in uptime_info:
            comment = f"カウントダウン情報が不足しています: {uptime_info['start_diff']}"
            self.update_label._update_label(label=label, comment=comment)
            self.logger.error(comment)
            return  # スキップ

        self.wait_seconds = uptime_info['start_diff']
        self.logger.debug(f'wait_seconds: {self.wait_seconds}')

        # 待機時間が現時刻以下の場合
        if self.wait_seconds <= 0:
            comment = "待機時間なし"
            self.update_label._update_label(label=label, comment=comment)
            self.logger.info(comment)

            self.countdown_timer.timeout.connect(lambda: self._countdown_event(label=label, start_event_flag=start_event_flag))
            self.countdown_timer.start()

        self.logger.debug(f"カウントダウン開始: {self.wait_seconds} ")

        # start_event_flagを監視
        self.check_flag._check_flag(flag=start_event_flag, event_func=event_func)

        try:
            self.countdown_timer.timeout.disconnect()  # 古い接続を解除してリセット
            # self.countdown_timer.setInterval(1000)  # 1秒ごとに発火
            self.countdown_timer.setInterval(10)  # テスト用

        except RuntimeError:
            self.logger.debug(f'タイマー接続なしのためスキップ')

        # カウントダウンのイベントをセット
        self.countdown_timer.timeout.connect(lambda: self._countdown_event(label=label, start_event_flag=start_event_flag))
        self.countdown_timer.start()

    ####################################################################################

    # ----------------------------------------------------------------------------------
    # Qtimerを使ったカウントダウン

    def _countdown_event(self, label: QLabel, start_event_flag: threading.Event):
        self.logger.debug(f'wait_seconds: {self.wait_seconds}')
        # 待機時間がある場合
        if self.wait_seconds > 0:
            minutes, seconds = divmod(self.wait_seconds, 60)
            msg = f"残り時間: {minutes} 分 {seconds} 秒" if minutes > 0 else f"残り時間: {seconds} 秒"
            self.logger.debug(f"カウントダウン開始: {msg} ")

            self.update_label._update_label(label=label, comment=msg)
            self.wait_seconds -= 1  # 時間を減少させる
            self.logger.debug(f"更新された待機時間: {self.wait_seconds}")


        # 待機時間を過ぎてからの処理
        else:
            comment = "カウントダウン終了"
            self.update_label._update_label(label=label, comment=comment)
            self.countdown_timer.stop()  # Timerをストップ
            start_event_flag.set()  # スタートフラグをON
            if start_event_flag.is_set():
                self.logger.debug('スタートフラグをON')


    # ----------------------------------------------------------------------------------
