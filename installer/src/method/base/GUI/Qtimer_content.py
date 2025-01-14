# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# export PYTHONPATH="/Users/nyanyacyan/Desktop/project_file/domain_search/installer/src"


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import threading
from datetime import timedelta
from typing import Dict, Callable
from PySide6.QtWidgets import QLabel
from PySide6.QtCore import QObject, QTimer, Signal


# 自作モジュール
from method.base.utils import Logger


# ----------------------------------------------------------------------------------
# **********************************************************************************


class CountDownQTimer(QObject):
    countdown_signal = Signal(int)
    def __init__(self, label: QLabel, uptime_info: Dict[int, int], start_event_flag: threading.Event):
        super().__init__()
        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

        self.label = label  # GUIのラベルを更新する

        self.countdown_timer = QTimer(self)
        self.uptime_info = uptime_info
        self.start_event_flag = start_event_flag


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

        try:
            self.countdown_timer.timeout.disconnect()  # 古い接続を解除してリセット
            # self.countdown_timer.setInterval(1000)  # 1秒ごとに発火
            self.countdown_timer.setInterval(10)  # テスト用

        except RuntimeError:
            self.logger.debug(f'タイマー接続なしのためスキップ')

        self.countdown_timer.timeout.connect(self.update_label)
        self.countdown_timer.start()



    ####################################################################################
    # ----------------------------------------------------------------------------------
    # ラベルを更新

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
            self.start_event_flag.set()  # スタートフラグをON
            self.logger.debug('スタートフラグをON')


    # ----------------------------------------------------------------------------------
    # uptime_info を更新する

    def update_uptime_info(self, uptime_info: Dict[str, timedelta]):
        self.logger.debug(f"uptime_info を更新: {uptime_info}")
        self.uptime_info = uptime_info


    # ----------------------------------------------------------------------------------
# **********************************************************************************


class CheckFlag(QObject):
    def __init__(self):
        super().__init__()

        self.check_timer = None  # 初期化

        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()


    ####################################################################################
    # QTimerでフラグを監視

    def _check_flag(self, flag: threading.Event, event_func: Callable, interval: int = 500):

        if hasattr(self, "check_timer") and self.check_timer and self.check_timer.isActive():
            self.logger.warning("既存のタイマーが動作中です。新しいタイマーを作成しません")
            return

        self.check_timer = QTimer()
        self.logger.debug(f"タイマー作成: {id(self.check_timer)}")

        self.check_timer.setInterval(interval)
        self.check_timer.timeout.connect(lambda: self._check_flag_and_start(flag, event_func, self.check_timer))
        self.check_timer.start()


    # ----------------------------------------------------------------------------------


    def _check_flag_and_start(self, flag: threading.Event, event_func: Callable, check_timer: QTimer):
        if flag.is_set():
            self.logger.info("フラグが立ちました！指定の関数を実行します")

            # そのまま動いていることを検知してTimerのtaskを消去してメモリを開放
            if check_timer.isActive():  # Timerがまだ動いているのか確認
                check_timer.stop()  # 動いていたら止める
                check_timer.deleteLater()  # ストップする予約
            del self.check_timer  # check_timerのtaskを消去

            # 処理開始
            event_func()
        else:
            self.logger.warning("フラグはまだ立っていません")


    # ----------------------------------------------------------------------------------
