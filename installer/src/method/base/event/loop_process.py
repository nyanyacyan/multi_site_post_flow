# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# export PYTHONPATH="/Users/nyanyacyan/Desktop/project_file/domain_search/installer/src"


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import ctypes, psutil, os
from datetime import datetime, timedelta
from queue import Queue, Empty
import threading, time
from functools import partial
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from typing import Dict, Callable
from PySide6.QtWidgets import QLabel
from PySide6.QtCore import QObject, Signal
from selenium.common.exceptions import UnexpectedAlertPresentException

# 自作モジュール
from method.base.utils import Logger
from method.base.event.update_label import UpdateLabel
from method.base.event.update_event import UpdateEvent
from method.base.time_manager import TimeManager
from method.base.event.thread_event import ThreadEvent


# ----------------------------------------------------------------------------------
# **********************************************************************************

class LoopProcessOrder(QObject):
    update_label_signal = Signal(str)  # クラス変数

    def __init__(self):
        super().__init__()
        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

        # インスタンス
        self.update_label = UpdateLabel()
        self.update_event = UpdateEvent()
        self.time_manager = TimeManager()
        self.thread_event = ThreadEvent()

        self.new_main_task_thread = None
        self.TEST_MODE = False

    ####################################################################################
    # start_eventに使用するmain処理

    def main_task(self, update_bool: bool, stop_event: threading.Event, label: QLabel, update_event: threading.Event, update_func: Callable, process_func: Callable, user_info: Dict, gss_info: Dict, interval_info: Dict):
        # 更新処理がある場合
        if update_bool:
            update_comment = "更新処理中..."
            self.update_label_signal.emit(update_comment)
            self.logger.warning(f'update_comment: {update_comment}')

            self.update_event._update_task(stop_event=stop_event, update_event=update_event, update_func=update_func, user_info=user_info)

            comp_comment = "更新処理が完了しました。"
            self.update_label_signal.emit(comp_comment)
            self.logger.debug(comp_comment)

            self.logger.warning(f'stop_eventの状態: {stop_event.is_set()}')
            self.logger.warning(f'update_eventの状態: {update_event.is_set()}')
        else:
            self.logger.info("更新処理「なし」のため更新処理なし")

        self.logger.info("これからmainloop処理を開始")
        self.new_item_process(stop_event=stop_event, process_func=process_func, user_info=user_info, gss_info=gss_info, label=label, interval_info=interval_info)

    # ----------------------------------------------------------------------------------
    ####################################################################################
    # 直列処理に変更（並列処理はなし）

    def new_item_process(self, stop_event: threading.Event, process_func: Callable, user_info: Dict, gss_info: Dict, label: QLabel, interval_info: Dict):
        task_id = 1
        try:
            while not stop_event.is_set():
                if not task_id == 1:
                    self.logger.debug(f'task_id: {task_id}')
                    # 🔹 出品間隔時間を待機
                    random_wait_time = self.time_manager._random_sleep(random_info=interval_info)

                    hours = int(random_wait_time // 3600)
                    minutes = int((random_wait_time % 3600) // 60)
                    seconds = int(random_wait_time % 60)

                    time_str = f"{hours}時間 {minutes}分 {seconds}秒" if hours >= 1 else f"{minutes}分 {seconds}秒"
                    self.logger.warning(f'stop_eventの状態: {stop_event.is_set()}')

                    random_wait_comment = f'出品間隔に合わせて、{time_str} 待機してます'
                    self.logger.info(random_wait_comment)
                    self.update_label_signal.emit(random_wait_comment)
                    stop_event.wait(random_wait_time)

                # 直接タスクを実行
                self._task_contents(task_id=task_id, label=label, process_func=process_func, user_info=user_info, gss_info=gss_info, interval_info=interval_info)
                task_id += 1

        except KeyboardInterrupt:
            self.logger.info("停止要求を受け付けました")

        finally:
            end_comment = "stop_eventを検知認め終了"
            self.logger.info(end_comment)
            self.update_label_signal.emit("待機中...")

    ####################################################################################
    # タスクの実行

    def _task_contents(self, task_id: int, label: QLabel, process_func: Callable, user_info: Dict, gss_info: Dict, interval_info: Dict):
        comment = f"新規出品 処理中 {task_id} 回目 ..."
        self.update_label._update_label(label=label, comment=comment)
        self.update_label_signal.emit(comment)

        # 開始時刻
        start_time = datetime.now()
        start_time_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
        self.logger.info(f"【start】実行処理開始: ({task_id}回目) [{start_time_str}]")

        self.logger.debug(f"\nid: {user_info['id']}\npass: {user_info['pass']}\nworksheet_name: {gss_info}")

        try:
            # 処理を実施
            process_func(id_text=user_info['id'], pass_text=user_info['pass'], worksheet_name=gss_info['select_worksheet'], gss_url=gss_info['sheet_url'], interval_info=interval_info)

        except UnexpectedAlertPresentException as e:
            alert_comment = "再出品の間隔が短いため処理中断"
            self.logger.error(f"再出品の間隔が短いため、エラー 処理中断: {e}")
            self.update_label_signal.emit(alert_comment)

        except Exception as e:
            self.logger.error(f"タスク実行中にエラーが発生 この処理をスキップ: {e}")

        # 処理時間計測
        end_time = datetime.now()
        diff_time = end_time - start_time
        minutes, seconds = divmod(diff_time.total_seconds(), 60)
        diff_time_str = f"{int(minutes)} 分 {int(seconds)} 秒" if minutes > 0 else f"{int(seconds)} 秒"

        self.logger.info(f"【complete】実行処理完了: ({task_id}回目) [処理時間: {diff_time_str}]")

    # ----------------------------------------------------------------------------------
    # 日付が変わるまで秒数待機（GCとMAのみ）

    def _monitor_date_change(self, stop_event: threading.Event, finish_event: threading.Event, main_thread: threading.Thread, update_bool: bool, label: QLabel, update_event: threading.Event, update_func: Callable, process_func: Callable, user_info: Dict, gss_info: Dict, interval_info: Dict):
        try:
            self.logger.debug(f"_monitor_date_change のスレッドID: {threading.get_ident()}")

            while not finish_event.is_set():
                now = datetime.now()
                if self.TEST_MODE:
                    next_day = now + timedelta(seconds=300)  # ✅ テスト用：30秒後に処理
                else:
                    next_day = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)  # ✅ 本番用

                self.logger.info(f"\n現時刻: {now}\n次のチェック時間: {next_day}")

                # ループ内で next_day_total_time を計算
                while not finish_event.is_set():
                    now = datetime.now()
                    next_day_total_time = (next_day - now).total_seconds()

                    if next_day_total_time <= 0:
                        self.logger.critical("日付変更を検知！ `next_day` を更新してループを継続します。")
                        break  # ✅ 日付が変わったのでループを抜ける

                    sleep_time = min(next_day_total_time, 60)  # ✅ 最大60秒ごとに待機（テスト時は最大30秒）
                    self.logger.info(f'【日にち切替確認】次のチェックまで {sleep_time} 秒待機...')
                    finish_event.wait(sleep_time)  # ✅ `finish_event` がセットされると即時終了

                self.logger.critical(f'{self.__class__.__name__} 日付が変わりました。main_taskを再起動します')

                # メインスレッドの終了処理
                if main_thread and main_thread.is_alive():
                    self.logger.info(f'`main_task_thread` の処理が完了するまで待機中...')
                    self.update_label_signal.emit("日付が変わったことを検知...最後の処理が完了するまで待機")
                    stop_event.set()
                    main_thread.join(timeout=2)

                if main_thread and main_thread.is_alive():
                    self.logger.warning(f'{self.__class__.__name__} メインスレッドが終了しないため、強制終了します。')
                    self._async_raise(main_thread.ident, SystemExit)

                # ✅ `threading.enumerate()` でスレッドが完全終了したかチェック
                for thread in threading.enumerate():
                    if thread is main_thread and thread.is_alive():
                        self.logger.warning("🚨 メインスレッドが完全に終了していないため、参照を解除します。")
                        main_thread = None
                        break

                # 2回目以降のスレッドも完了するまで待機
                if self.new_main_task_thread and self.new_main_task_thread.is_alive():
                    self.logger.info(f'`new_main_task_thread` の処理が完了するまで待機中...')
                    stop_event.set()
                    self.new_main_task_thread.join(timeout=2)

                if self.new_main_task_thread and self.new_main_task_thread.is_alive():
                    self.logger.warning(f'{self.__class__.__name__} `new_main_task_thread` が終了しないため、強制終了します。')
                    self._async_raise(self.new_main_task_thread.ident, SystemExit)

                # ✅ `threading.enumerate()` で完全にスレッドが終了したか確認
                for thread in threading.enumerate():
                    if thread is self.new_main_task_thread and thread.is_alive():
                        self.logger.warning("🚨 `new_main_task_thread` が完全に終了していないため、参照を解除します。")
                        del self.new_main_task_thread
                        break

                # ✅ 再スタート処理
                if not finish_event.is_set():
                    restart_comment = "日付が変わったため更新処理からリスタート処理を実施"
                    self.logger.info(restart_comment)
                    self.update_label_signal.emit(restart_comment)
                    self._restart_main_task(stop_event, finish_event, update_bool, label, update_event, update_func, process_func, user_info, gss_info, interval_info)
                else:
                    self.logger.critical(f'finish_eventがあるため最後の処理をスキップしてます: {finish_event.is_set()}')

        except Exception as e:
            self.logger.error(f"処理中にエラーが発生: {e}")

        finally:
            self.logger.info(f'finish_eventを検知しました。')
            self.update_label_signal.emit("待機中...")
            stop_event.clear()
            finish_event.clear()



    # ----------------------------------------------------------------------------------
    # 指定したスレッドに例外を送信して強制終了

    def _async_raise(self, main_thread, exctype):
        if not isinstance(exctype, type) or not issubclass(exctype, BaseException):
            raise ValueError("exctype は BaseException のサブクラスである必要")

        # ✅ ここで `exctype` を送ることで例外を発生させる
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(main_thread), ctypes.py_object(exctype))

        if res == 0:
            raise ValueError("スレッドIDが無効です")

        elif res > 1:
            self.logger.error(f'{self.__class__.__name__} main_threadが1つ以上あります: {main_thread}')
            ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(main_thread), None)  # ✅ 送った例外を取り消す
            raise SystemError("PyThreadState_SetAsyncExc failed")

    # ----------------------------------------------------------------------------------


    def kill_chrome(self):
        for process in psutil.process_iter(attrs=["pid", "name"]):
            try:
                if "chrome" in process.info["name"].lower() or "chromedriver" in process.info["name"].lower():
                    self.logger.info(f"Chromeを強制終了: {process.info['name']} (PID: {process.info['pid']})")
                    os.kill(process.info["pid"], 9) # ✅ 強制終了
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

    # ----------------------------------------------------------------------------------

    def _restart_main_task(self, stop_event: threading.Event, finish_event: threading.Event, update_bool: bool, label: QLabel, update_event: threading.Event, update_func: Callable, process_func: Callable, user_info: Dict, gss_info: Dict, interval_info: Dict):
        self.logger.info("【日付変更】`main_task` の再起動を開始")

        # 🟢 新しい `main_task` を開始
        stop_event.clear()
        finish_event.clear()
        self.logger.info("stop_eventを元の状態に戻しました。")

        self._restart_main_thread(update_bool, stop_event, label, update_event, update_func,process_func, user_info, gss_info, interval_info)


    # ----------------------------------------------------------------------------------
    # 新しいメインスレッドの実行

    def _restart_main_thread(self, update_bool: bool, stop_event: threading.Event, label: QLabel, update_event: threading.Event, update_func: Callable, process_func: Callable, user_info: Dict, gss_info: Dict, interval_info: Dict):
            # メイン処理を別スレッドの定義
            self.new_main_task_thread = threading.Thread(
                target=self.main_task,
                kwargs={
                    "update_bool": update_bool,
                    "stop_event": stop_event,
                    "label": label,
                    "update_event": update_event,
                    "update_func": update_func,
                    "process_func": process_func,
                    "user_info": user_info,
                    "gss_info": gss_info,
                    "interval_info": interval_info,
                }, daemon=True )

            # 各スレッドスタート
            self.new_main_task_thread.start()

    # ----------------------------------------------------------------------------------
    # 設定している時間になったら設定したtaskを実行

    def _monitor_end_time( self, uptime_info: Dict[int, int], finish_event: threading.Event, stop_event: threading.Event, main_thread: Callable[[], None]):
        try:
            self.logger.debug( f"_monitor_end_time のスレッドID: {threading.get_ident()}" )
            end_diff = uptime_info["end_diff"]
            self.logger.info(f'end_diff: {end_diff}')

            now = datetime.now()

            end_time = now + timedelta(seconds=end_diff)
            self.logger.critical(f"終了時間 {end_time}\n 現在時刻: {now}")

            while datetime.now() < end_time and not finish_event.is_set():
                remaining_time = (end_time - datetime.now()).total_seconds()
                sleep_time = min(remaining_time, 60)  # remaining_timeが60秒よりも小さかったらminで選ばれる
                self.logger.debug(f'終了まで {remaining_time:.2f} 秒（次のチェックまで {sleep_time:.2f} 秒）')
                finish_event.wait(sleep_time)  # 待機する

            if not finish_event.is_set():
                self.logger.debug("終了時間に到達！ `_end_time_task()` を実行")
                self._end_time_task(finish_event=finish_event, stop_event=stop_event, main_thread=main_thread)

        except Exception as e:
            comment = f"終了時間の設定などによるエラー: {e}"
            self.logger.error(comment)

    # ----------------------------------------------------------------------------------
    # 終了時に行うtask

    def _end_time_task(self, finish_event: threading.Event, stop_event: threading.Event, main_thread: threading.Thread):
        # 処理を停止
        finish_event.set()
        stop_event.set()
        if finish_event.is_set():
            comment = "終了時間に達したため処理を停止しました。"
            self.logger.warning(comment)
            self.update_label_signal.emit(comment)

        try:
            # main_thread の終了処理
            if main_thread and main_thread.is_alive():
                self.logger.info('`main_task` の処理が完了するまで待機中...')
                main_thread.join(timeout=3)

                if main_thread.is_alive():
                    self.logger.warning(f'{self.__class__.__name__} メインスレッドが終了しないため、強制終了します。')
                    self._async_raise(main_thread.ident, SystemExit)
                    time.sleep(1)

            for thread in threading.enumerate():
                if thread is main_thread and thread.is_alive():
                    self.logger.warning("🚨 メインスレッドが完全に終了していないため、強制終了を試みます。")
                    self._async_raise(thread.ident, SystemExit)
                    time.sleep(1)
                    if not thread.is_alive():
                        del main_thread
                        self.logger.info("✅ メインスレッドを完全に削除しました")

            # new_main_task_thread の終了処理
            if self.new_main_task_thread and self.new_main_task_thread.is_alive():
                self.logger.info(f'`new_main_task_thread` の処理が完了するまで待機中...')
                self.new_main_task_thread.join(timeout=3)

                if self.new_main_task_thread.is_alive():
                    self.logger.warning(f'{self.__class__.__name__} `new_main_task_thread` が終了しないため、強制終了します。')
                    self._async_raise(self.new_main_task_thread.ident, SystemExit)
                    time.sleep(1)

            for thread in threading.enumerate():
                if thread is self.new_main_task_thread and thread.is_alive():
                    self.logger.warning("🚨 `new_main_task_thread` が完全に終了していないため、強制終了を試みます。")
                    self._async_raise(thread.ident, SystemExit)
                    time.sleep(1)
                    if not thread.is_alive():
                        del self.new_main_task_thread
                        self.logger.info("✅ `new_main_task_thread` を完全に削除しました")

        except AssertionError:
            self.logger.warning("AssertionError をキャッチしましたが、処理を継続します。")

        # 処理完了後に「待機中...」を設定
        self.update_label_signal.emit("待機中...")


    # ----------------------------------------------------------------------------------
# **********************************************************************************

class LoopProcessOrderNoUpdate(QObject):
    update_label_signal = Signal(str)  # クラス変数

    def __init__(self):
        super().__init__()
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()
        self.update_label = UpdateLabel()
        self.time_manager = TimeManager()

        self.new_main_task_thread = None
        self.TEST_MODE = False

    # ----------------------------------------------------------------------------------
    # start_eventに使用するmain処理

    def main_task(self, stop_event: threading.Event, label: QLabel, process_func: Callable, user_info: Dict, gss_info: Dict, interval_info: Dict):
        self.logger.info("これからmainloop処理を開始")
        self.new_item_process(stop_event=stop_event, process_func=process_func, user_info=user_info, gss_info=gss_info, label=label, interval_info=interval_info)

    # ----------------------------------------------------------------------------------
    # 直列処理に変更（並列処理はなし）

    def new_item_process(self, stop_event: threading.Event, process_func: Callable, user_info: Dict, gss_info: Dict, label: QLabel, interval_info: Dict):
        task_id = 1
        try:
            while not stop_event.is_set():
                if not task_id == 1:
                    self.logger.debug(f'task_id: {task_id}')
                    # 🔹 出品間隔時間を待機
                    random_wait_time = self.time_manager._random_sleep(random_info=interval_info)

                    hours = int(random_wait_time // 3600)
                    minutes = int((random_wait_time % 3600) // 60)
                    seconds = int(random_wait_time % 60)

                    time_str = f"{hours}時間 {minutes}分 {seconds}秒" if hours >= 1 else f"{minutes}分 {seconds}秒"

                    random_wait_comment = f'出品間隔に合わせて、{time_str} 待機してます'
                    self.logger.info(random_wait_comment)
                    self.update_label_signal.emit(random_wait_comment)
                    stop_event.wait(random_wait_time)

                # 直接タスクを実行
                self._task_contents(task_id=task_id, label=label, process_func=process_func, user_info=user_info, gss_info=gss_info, interval_info=interval_info)
                task_id += 1

        except KeyboardInterrupt:
            self.logger.info("停止要求を受け付けました")

        finally:
            end_comment = "stop_eventを検知認め終了"
            self.logger.info(end_comment)
            self.update_label_signal.emit("待機中...")

    ####################################################################################
    # タスクの実行

    def _task_contents(self, task_id: int, label: QLabel, process_func: Callable, user_info: Dict, gss_info: Dict, interval_info: Dict):
        comment = f"新規出品 処理中 {task_id} 回目 ..."
        self.update_label._update_label(label=label, comment=comment)
        self.update_label_signal.emit(comment)

        # 開始時刻
        start_time = datetime.now()
        start_time_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
        self.logger.info(f"【start】実行処理開始: ({task_id}回目) [{start_time_str}]")

        self.logger.debug(f"\nid: {user_info['id']}\npass: {user_info['pass']}\nworksheet_name: {gss_info}")

        try:
            # 処理を実施
            process_func(id_text=user_info['id'], pass_text=user_info['pass'], worksheet_name=gss_info['select_worksheet'], gss_url=gss_info['sheet_url'], interval_info=interval_info)

        except UnexpectedAlertPresentException as e:
            alert_comment = "再出品の間隔が短いため処理中断"
            self.logger.error(f"再出品の間隔が短いため、エラー 処理中断: {e}")
            self.update_label_signal.emit(alert_comment)

        except Exception as e:
            self.logger.error(f"タスク実行中にエラーが発生 この処理をスキップ: {e}")

        # 処理時間計測
        end_time = datetime.now()
        diff_time = end_time - start_time
        minutes, seconds = divmod(diff_time.total_seconds(), 60)
        diff_time_str = f"{int(minutes)} 分 {int(seconds)} 秒" if minutes > 0 else f"{int(seconds)} 秒"

        self.logger.info(f"【complete】実行処理完了: ({task_id}回目) [処理時間: {diff_time_str}]")

    # ----------------------------------------------------------------------------------
    # 日付が変わるまで秒数待機（GCとMAのみ）

    def _monitor_date_change( self, stop_event: threading.Event, finish_event:threading.Event, main_thread: threading.Thread, label: QLabel, process_func: Callable, user_info: Dict, gss_info: Dict, interval_info: Dict):
        try:
            self.logger.debug(f"_monitor_date_change のスレッドID: {threading.get_ident()}")

            while not finish_event.is_set():
                now = datetime.now()
                next_day = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)  # ✅ 日付が変わるたびに更新
                self.logger.warning(f'next_day: {next_day}')

                if self.TEST_MODE:
                    next_day_total_time = 30  # ✅ テスト用に30秒後に実行
                else:
                    next_day_total_time = (next_day - now).total_seconds()  # ✅ 本番環境

                self.logger.info(f"\n現時刻: {now}\n翌日の時刻（24時換算): {next_day}\n日付が変わるまでの秒数: {next_day_total_time}")

                while not finish_event.is_set() and next_day_total_time > 0:

                    now = datetime.now()  # ✅ 毎回現在時刻を取得（時間のずれを防ぐ）
                    next_day_total_time = (next_day - now).total_seconds()  # ✅ 正確な残り時間を計算

                    if next_day_total_time <= 0:
                        self.logger.critical("日付変更を検知！ `next_day` を更新してループを継続します。")
                        break  # ✅ 日付が変わったのでループを抜け、新しい `next_day` を設定する

                    sleep_time = min(next_day_total_time, 60)  # ✅ 最大60秒ごとに待機
                    self.logger.warning(f'【日にち切替確認】次のチェックまで {sleep_time} 秒待機...')

                    finish_event.wait(sleep_time)  # ✅ `finish_event` がセットされると即時終了

                    # ✅ 待機後に現在の時間を取得し、再計算
                    now = datetime.now()
                    next_day_total_time = (next_day - now).total_seconds()

                    hours = int(next_day_total_time // 3600)
                    minutes = int((next_day_total_time % 3600) // 60)
                    seconds = int(next_day_total_time % 60)

                    time_str = f"{hours}時間 {minutes}分 {seconds}秒" if hours >= 1 else f"{minutes}分 {seconds}秒"
                    self.logger.critical(f"日付が変わるまで残り時間: {time_str}")

                    if self.TEST_MODE:
                        next_day_total_time = -1

                # ✅ `while True` の先頭で `next_day` を更新するので、次の日の監視を継続できる
                self.logger.critical(f'{self.__class__.__name__} 日付が変わりました。main_taskを再起動します')

                # 🔹 メインスレッドが生きている場合、完了を待機
                if main_thread and main_thread.is_alive():
                    self.logger.info(f'`main_task_thread` の処理が完了するまで待機中...{main_thread}')
                    self.update_label_signal.emit("日付が変わったことを検知...最後の処理が完了するまで待機")
                    stop_event.set()
                    main_thread.join()
                    self.logger.info('最後の`main_task_thread` が終了しました')

                # 🔹 2回目以降のスレッドも完了するまで待機
                if self.new_main_task_thread and self.new_main_task_thread.is_alive():
                    self.logger.info(f'`new_main_task_thread` の処理が完了するまで待機中...{self.new_main_task_thread}')
                    stop_event.set()
                    self.new_main_task_thread.join()
                    self.logger.info('最後の`new_main_task_thread` が終了しました')

                # 🔹 出品間隔時間を待機
                random_wait_time = self.time_manager._random_sleep(random_info=interval_info)
                random_wait_comment = f'出品間隔に合わせて {int(random_wait_time)} 秒間、待機してます'
                self.logger.info(random_wait_comment)
                self.update_label_signal.emit(random_wait_comment)

                if self.TEST_MODE:
                    time.sleep(1)  # ✅ テスト用に短縮
                else:
                    finish_event.wait(random_wait_time)  # 本番環境

                if not finish_event.is_set():
                    restart_comment = "日付が変わったため更新処理からリスタート処理を実施"
                    self.logger.info(restart_comment)
                    self.update_label_signal.emit(restart_comment)
                    self._restart_main_task(stop_event, label, process_func, user_info, gss_info, interval_info)
                else:
                    self.logger.critical(f'finish_eventがあるため最後の処理をスキップしてます: {finish_event.is_set()}')

        except Exception as e:
            self.logger.error(f"処理中にエラーが発生: {e}")

        finally:
            self.logger.info(f'finish_eventを検知しました。')
            self.update_label_signal.emit("待機中...")
            stop_event.clear()
            finish_event.clear()

    # ----------------------------------------------------------------------------------

    def _restart_main_task(self, stop_event: threading.Event, label: QLabel, process_func: Callable, user_info: Dict, gss_info: Dict, interval_info: Dict):
        self.logger.info("【日付変更】`main_task` の再起動を開始")

        # 🟢 新しい `main_task` を開始
        stop_event.clear()
        self.logger.info("stop_eventを元の状態に戻しました。")

        self._restart_main_thread(stop_event, label, process_func, user_info, gss_info, interval_info)


    # ----------------------------------------------------------------------------------
    # 新しいメインスレッドの実行

    def _restart_main_thread(self, stop_event: threading.Event, label: QLabel, process_func: Callable, user_info: Dict, gss_info: Dict, interval_info: Dict):
            # メイン処理を別スレッドの定義
            self.new_main_task_thread = threading.Thread(
                target=self.main_task,
                kwargs={
                    "stop_event": stop_event,
                    "label": label,
                    "process_func": process_func,
                    "user_info": user_info,
                    "gss_info": gss_info,
                    "interval_info": interval_info,
                }, daemon=True )

            # 各スレッドスタート
            self.new_main_task_thread.start()

    # ----------------------------------------------------------------------------------
    # 設定している時間になったら設定したtaskを実行

    def _monitor_end_time( self, uptime_info: Dict[int, int], finish_event: threading.Event, stop_event: threading.Event, main_thread: Callable[[], None]):
        try:
            self.logger.debug( f"_monitor_end_time のスレッドID: {threading.get_ident()}" )
            end_diff = uptime_info["end_diff"]

            if end_diff > 0:
                self.logger.critical( f"終了時間まで {end_diff} 秒待機します (threading.Timer を使用)" )
                # 終了時間まで待機
                threading.Timer( end_diff, lambda: self._end_time_task(finish_event=finish_event, stop_event=stop_event, main_thread=main_thread) ).start()
        except Exception as e:
            comment = f"終了時間の設定などによるエラー: {e}"
            self.logger.error(comment)

    # ----------------------------------------------------------------------------------
    # 終了時に行うtask

    def _end_time_task(self, finish_event: threading.Event, stop_event: threading.Event, main_thread: threading.Thread):
        # 処理を停止
        finish_event.set()
        stop_event.set()
        if finish_event.is_set():
            comment = "終了時間に達したため処理を停止しました。"
            self.logger.warning(comment)
            self.update_label_signal.emit(comment)

        try:
            # threadにあるmain_threadがあったら終わるまで待機する
            if main_thread and main_thread.is_alive():
                self.logger.info('`main_task` の処理が完了するまで待機中...: ')
                main_thread.join()  # main_threadが終了するまで待機

            if self.new_main_task_thread and self.new_main_task_thread.is_alive():
                self.logger.info(f'`new_main_task_thread` の処理が完了するまで待機中...{self.new_main_task_thread}')
                self.new_main_task_thread.join()
                self.logger.info('最後の`new_main_task_thread` が終了しました')

        except AssertionError:
            self.logger.warning("AssertionError をキャッチしましたが、処理を継続します。")

        # 処理完了後に「待機中...」を設定
        self.update_label_signal.emit("待機中...")

    # ----------------------------------------------------------------------------------
