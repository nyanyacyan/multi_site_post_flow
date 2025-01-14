# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# export PYTHONPATH="/Users/nyanyacyan/Desktop/project_file/domain_search/installer/src"


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import threading, time
from datetime import timedelta, datetime
from typing import Dict, Callable
from PySide6.QtWidgets import QLabel, QApplication
from PySide6.QtCore import QObject, QMetaObject, Qt, QTimer, Q_ARG, QCoreApplication, QThread


# 自作モジュール
from method.base.utils import Logger
from method.base.event.update_label import UpdateLabel
from method.base.event.update_event import UpdateEvent

# ----------------------------------------------------------------------------------
# **********************************************************************************


class ThreadEvent(QObject):
    def __init__(self):
        super().__init__()
        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

        # インスタンス
        self.update_label = UpdateLabel()
        self.update_event = UpdateEvent()


    ####################################################################################
    # 設定している時間になったら設定したtaskを実行

    def _monitor_end_time(self, uptime_info: Dict[int, int], stop_event: threading.Event, label: QLabel):
        try:
            self.logger.debug(f"_monitor_end_time のスレッドID: {threading.get_ident()}")
            end_diff = uptime_info['end_diff']

            if end_diff > 0:
                self.logger.debug(f"終了時間まで {end_diff} 秒待機します (threading.Timer を使用)")
                # 終了時間まで待機
                threading.Timer(end_diff, lambda: self._end_time_task(stop_event, label)).start()

        except Exception as e:
            comment = f"終了時間の設定などによるエラー: {e}"
            self.update_label._update_label(label=label, comment=comment)
            self.logger.error(comment)


    ####################################################################################
    # ----------------------------------------------------------------------------------
    # 終了時に行うtask

    def _end_time_task(self, stop_event: threading.Event, label: QLabel):
            # 処理を停止
            stop_event.set()
            if stop_event.is_set:
                comment = "終了時間に達したため処理を停止しました。"
                self.update_label._update_label(label=label, comment=comment)
                self.logger.info("終了タスクが正常に実行されました。")

                # 処理完了後に「待機中...」を設定
                QTimer.singleShot(0, lambda: self.update_label._update_label(label=label, comment="待機中..."))


    # ----------------------------------------------------------------------------------
    ####################################################################################
    # 日付が変わるまで秒数待機（GCとMAのみ）

    def _monitor_date_change(self, stop_event: threading.Event, label: QLabel, update_event: threading.Event, update_bool: bool, user_info: Dict):
        try:
            self.logger.debug(f"_monitor_date_change のスレッドID: {threading.get_ident()}")

            # 今の時間から日付が変わるまでの秒数を算出
            now = datetime.now()
            next_day = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            next_day_total_time = (next_day - now).total_seconds()
            self.logger.info(f'\n現時刻: {now}\n翌日の時刻（24時換算): {next_day}\n日付が変わるまでの秒数: {next_day_total_time}')

            # 日付が変わるまで秒数待機
            threading.Timer(next_day_total_time, lambda: self._date_end_time_task(stop_event=stop_event, label=label, update_event=update_event, update_bool=update_bool, user_info=user_info)).start()

        except Exception as e:
            comment = f"処理中にエラーが発生: {e}"
            self.update_label._update_label(label=label, comment=comment)
            self.logger.error(comment)


    ####################################################################################
    # ----------------------------------------------------------------------------------
    # 終了時に行うtask

    def _date_end_time_task(self, update_bool: bool, stop_event: threading.Event, label: QLabel, update_event: threading.Event, update_func: Callable, user_info: Dict):
        # 更新処理がありの場合に処理
        if update_bool:
            self.update_event._update_task(stop_event=stop_event, label=label, update_event=update_event, update_func=update_func, user_info=user_info)
        else:
            self.logger.info("更新処理「なし」のため更新処理なし")


    # ----------------------------------------------------------------------------------
