# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# export PYTHONPATH="/Users/nyanyacyan/Desktop/project_file/domain_search/installer/src"


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import threading, time
from datetime import timedelta, datetime
from typing import Dict, Callable
from PySide6.QtWidgets import QLabel
from PySide6.QtCore import QObject, Signal


# 自作モジュール
from method.base.utils import Logger
from method.base.event.update_label import UpdateLabel
from method.base.event.update_event import UpdateEvent
# from method.base.event.loop_process import LoopProcessOrder, LoopProcessOrderNoUpdate

# ----------------------------------------------------------------------------------
# **********************************************************************************


class ThreadEvent(QObject):
    update_label_signal = Signal(str)  # クラス変数

    def __init__(self):
        super().__init__()
        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

        # インスタンス
        self.update_label = UpdateLabel()
        self.update_event = UpdateEvent()
        # self.loop_process = LoopProcessOrder()

        self.timer = None  # 🔹 Timerを管理する変数を追加

    ####################################################################################
    # 設定している時間になったら設定したtaskを実行

    def _monitor_end_time( self, uptime_info: Dict[int, int], finish_event: threading.Event, main_thread: Callable[[], None]):
        try:
            self.logger.debug( f"_monitor_end_time のスレッドID: {threading.get_ident()}" )
            end_diff = uptime_info["end_diff"]

            if end_diff > 0:
                self.logger.debug( f"終了時間まで {end_diff} 秒待機します (threading.Timer を使用)" )
                # 終了時間まで待機
                threading.Timer( end_diff, lambda: self._end_time_task(finish_event=finish_event, main_thread=main_thread) ).start()
        except Exception as e:
            comment = f"終了時間の設定などによるエラー: {e}"
            self.logger.error(comment)

    ####################################################################################
    # ----------------------------------------------------------------------------------
    # 終了時に行うtask

    def _end_time_task(self, finish_event: threading.Event, main_thread: threading.Thread):
        # 処理を停止
        finish_event.set()
        if finish_event.is_set():
            comment = "終了時間に達したため処理を停止しました。"
            self.logger.warning(comment)
            self.update_label_signal.emit(comment)

        # threadにあるmain_threadがあったら終わるまで待機する
        if main_thread and main_thread.is_alive():
            self.logger.info('`main_task` の処理が完了するまで待機中...: ')
            main_thread.join()  # main_threadが終了するまで待機

        # 処理完了後に「待機中...」を設定
        self.update_label_signal.emit("待機中...")

    # ----------------------------------------------------------------------------------
    ####################################################################################
    # 日付が変わるまで秒数待機（GCとMAのみ）

    def _monitor_date_change( self, stop_event: threading.Event, finish_event:threading.Event, main_thread: threading.Thread ):
        try:
            self.logger.debug( f"_monitor_date_change のスレッドID: {threading.get_ident()}" )

            while not finish_event.is_set():
                # 今の時間から日付が変わるまでの秒数を算出
                now = datetime.now()
                next_day = (now + timedelta(days=1)).replace( hour=0, minute=0, second=0, microsecond=0 )


                # next_day_total_time = (next_day - now).total_seconds()  # TODO 本番環境
                next_day_total_time = 30  # TODO テスト環境

                self.logger.info( f"\n現時刻: {now}\n翌日の時刻（24時換算): {next_day}\n日付が変わるまでの秒数: {next_day_total_time}" )

                # 日付が変わるまで秒数待機
                self.logger.info('日付が変わるまで待機するthreadスタート')
                self.logger.critical(f'{self.__class__.__name__} 待ち時間終了: {next_day_total_time}')

                finish_event.wait(next_day_total_time)

                # 待機したあとにメインメソッドの繰り返しを止める
                stop_event.set()

                if main_thread.is_alive():
                    self.logger.info(f'`main_task_thread` の処理が完了するまで待機中...{main_thread}')

                    main_thread.join()
                    self.logger.info('最後の`main_task_thread` が終了しました')

                self._restart_main_task(stop_event=stop_event)

            self.logger.warning(f'{self.__class__.__name__} finish_eventのフラグを検知')

        except Exception as e:
            self.logger.error(f"処理中にエラーが発生: {e}")

    # ----------------------------------------------------------------------------------

    def _restart_main_task(self, stop_event: threading.Event):
        self.logger.info("【日付変更】`main_task` の再起動を開始")

        self.logger.info("`main_task_thread` が終了しました。新しいタスクを開始します。")

        # 🟢 新しい `main_task` を開始
        stop_event.clear()
        self._restart_main_thread()


    # ----------------------------------------------------------------------------------
    # 新しいメインスレッドの実行

    def _restart_main_thread(self):
            # メイン処理を別スレッドの定義
            self.main_task_thread = threading.Thread(
                target=self.main_task,
                kwargs={
                    "update_bool": self.update_bool,
                    "stop_event": self.stop_flag,
                    "label": self.process_label,
                    "update_event": self.update_flag,
                    "update_func": self.update_func,
                    "process_func": self.process_func,
                    "user_info": self.user_info,
                    "gss_info": self.gss_info,
                    "interval_info": self.interval_info,
                }, daemon=True )

            # 各スレッドスタート
            self.main_task_thread.start()

    # ----------------------------------------------------------------------------------

# **********************************************************************************


class ThreadEventNoUpdate(QObject):
    update_label_signal = Signal(str)  # クラス変数

    def __init__(self):
        super().__init__()
        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

        # インスタンス
        self.update_label = UpdateLabel()
        # self.update_event = UpdateEvent()
        # self.loop_process = LoopProcessOrderNoUpdate()

    ####################################################################################
    # 設定している時間になったら設定したtaskを実行

    def _monitor_end_time(
        self, uptime_info: Dict[int, int], stop_event: threading.Event
    ):
        try:
            self.logger.debug(
                f"_monitor_end_time のスレッドID: {threading.get_ident()}"
            )
            end_diff = uptime_info["end_diff"]

            if end_diff > 0:
                self.logger.debug(
                    f"終了時間まで {end_diff} 秒待機します (threading.Timer を使用)"
                )
                # 終了時間まで待機
                threading.Timer(
                    end_diff, lambda: self._end_time_task(stop_event)
                ).start()

        except Exception as e:
            comment = f"終了時間の設定などによるエラー: {e}"
            self.logger.error(comment)

    ####################################################################################
    # ----------------------------------------------------------------------------------
    # 終了時に行うtask

    def _end_time_task(self, stop_event: threading.Event):
        # 処理を停止
        stop_event.set()
        if stop_event.is_set():
            comment = "終了時間に達したため処理を停止しました。"
            self.update_label_signal.emit(comment)
            self.logger.info("終了タスクが正常に実行されました。")

            # 処理完了後に「待機中...」を設定
            self.update_label_signal.emit("待機中...")

    # ----------------------------------------------------------------------------------
    ####################################################################################
    # 日付が変わるまで秒数待機（GCとMAのみ）

    def _monitor_date_change(
        self,
        stop_event: threading.Event,
        label: QLabel,
        process_func: Callable,
        user_info: Dict,
        gss_info: str,
        interval_info: Dict,
    ):
        try:
            self.logger.debug(
                f"_monitor_date_change のスレッドID: {threading.get_ident()}"
            )

            # 今の時間から日付が変わるまでの秒数を算出
            now = datetime.now()
            next_day = (now + timedelta(days=1)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            next_day_total_time = (next_day - now).total_seconds()
            self.logger.info(
                f"\n現時刻: {now}\n翌日の時刻（24時換算): {next_day}\n日付が変わるまでの秒数: {next_day_total_time}"
            )

            # 日付が変わるまで秒数待機
            threading.Timer(
                next_day_total_time,
                lambda: self._date_end_time_task(
                    stop_event=stop_event,
                    label=label,
                    process_func=process_func,
                    user_info=user_info,
                    gss_info=gss_info,
                    interval_info=interval_info,
                ),
            ).start()

        except Exception as e:
            comment = f"処理中にエラーが発生: {e}"
            self.logger.error(comment)

    ####################################################################################
    # ----------------------------------------------------------------------------------

