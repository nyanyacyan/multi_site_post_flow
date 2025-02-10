# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# export PYTHONPATH="/Users/nyanyacyan/Desktop/project_file/domain_search/installer/src"


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
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


class LoopProcess(QObject):
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


    ####################################################################################
    # start_eventに使用するmain処理

    def main_task(self, update_bool: bool, stop_event: threading.Event, label: QLabel, update_event: threading.Event, update_func: Callable, process_func: Callable, user_info: Dict, gss_info: Dict, interval_info: Dict):
        # 更新処理がありの場合に処理
        if update_bool:
            update_comment = "更新処理中..."
            self.update_label_signal.emit(update_comment)
            self.logger.warning(f'update_comment: {update_comment}')

            self.update_event._update_task(stop_event=stop_event, update_event=update_event, update_func=update_func, user_info=user_info)

            comp_comment = "更新処理が完了しました。"
            self.update_label_signal.emit(comp_comment)
            self.logger.debug(comp_comment)
        else:
            self.logger.info("更新処理「なし」のため更新処理なし")

        self.logger.info("これからmainloop処理を開始")
        self.process(stop_event=stop_event, process_func=process_func, user_info=user_info, gss_info=gss_info, label=label, interval_info=interval_info)


    ####################################################################################
    # ----------------------------------------------------------------------------------


    def process(self, stop_event: threading.Event, process_func: Callable, user_info: Dict, gss_info: str, label: QLabel, interval_info: Dict, max_workers: int =3):
        executor = ThreadPoolExecutor(max_workers=max_workers)
        task_que = Queue()

        self._start_parallel_process(stop_event=stop_event, executor=executor, task_que=task_que, process_func=process_func, user_info=user_info, gss_info=gss_info, label=label, interval_info=interval_info)


    # ----------------------------------------------------------------------------------
    # 並列処理の実行
    # Queを管理するツールを起動→Queを作り続ける→監視ツールがQueを確認次第処理を開始→並列処理


    def _start_parallel_process(self, stop_event: threading.Event, executor: ThreadPoolExecutor, task_que: Queue, process_func: Callable, user_info: Dict, gss_info: Dict, label: QLabel, interval_info: Dict):
        # 並列処理ロジックスタート（dispatcherはtaskを受取、ThreadPoolに割り当てる）
        dispatcher_thread = threading.Thread( target=self._task_manager, kwargs={ 'stop_event': stop_event, 'executor' : executor, 'task_que' : task_que, 'process_func' : process_func, 'user_info' : user_info, 'gss_info' : gss_info, 'interval_info': interval_info, 'label' : label, } )
        dispatcher_thread.start()

        task_id = 1
        try:
            # queを作成し続ける
            while not stop_event.is_set():
                self._add_que_task(task_id=task_id, task_queue=task_que)
                self.logger.info(f'【{task_id} 個目】Queを追加')
                task_id += 1

                # 指定しているランダム待機
                random_wait_time = self.time_manager._random_sleep(random_info=interval_info)

                # TODO ここに列の分だけ追加するrandomの待機時間を生成する
                row_num = gss_info['row_num'] + 1
                self.logger.debug(f'\nrow_num: {row_num}\n型: {type(row_num)}')
                total_wait_time = random_wait_time * row_num

                self.logger.info(f"{int(total_wait_time)} 秒待機して次のタスクを生成...")
                time.sleep(total_wait_time)

        except KeyboardInterrupt:
            self.logger.info("停止要求を受け付けました")

        finally:
            # 停止処理
            self.stop(executor=executor)
            comment = f"【全 {task_id} 回実施】 処理を停止しました。"
            self.logger.warning(comment)
            self.update_label_signal.emit(comment)
            dispatcher_thread.join()


            next_comment = "待機中..."
            self.update_label_signal.emit(next_comment)


    # ----------------------------------------------------------------------------------
    # Queを追加

    def _add_que_task(self, task_id: int, task_queue: Queue):
        self.logger.info(f"タスク {task_id} を追加しました")
        task_queue.put(task_id)  # Queを追加


    # ----------------------------------------------------------------------------------
    # Queがないかを監視


    def _task_manager(self, stop_event: threading.Event, executor: ThreadPoolExecutor, task_que: Queue, process_func: Callable, user_info: Dict, gss_info: Dict, interval_info: Dict, label: QLabel, delay: int=1):
        task_count = 0
        while not stop_event.is_set():
            try:
                # Queを取得
                task_id = task_que.get(timeout=1)
                self.logger.info(f"task_id: {task_id}")

                #! ここでメインのループ処理を実行する
                task = partial(self._task_contents, count=task_count, label=label, process_func=process_func, user_info=user_info, gss_info=gss_info, interval_info=interval_info)
                # 処理を実施
                executor.submit(task)

                task_count += 1
                task_que.task_done()  # タスクの完了を通知

            # Queが殻になったら待機
            except Empty:
                time.sleep(delay)

            except RuntimeError:
                executor.shutdown(wait=True)
                self.logger.info("シャットダウンをしてます。")

        self.logger.info(f"タスクディスパッチャーを停止します (新規出品数: {task_count})")
        comment = f"【全 {task_count} 回目】新規出品処理 停止中..."
        self.update_label_signal.emit(comment)
        self.logger.warning(comment)


    # ----------------------------------------------------------------------------------
    # taskの中身（実際に処理する内容）

    def _task_contents(self, count: int, label: QLabel, process_func: Callable, user_info: Dict, gss_info: Dict, interval_info: Dict):
        comment = f"新規出品 処理中 {count + 1}回目 ..."
        self.update_label._update_label(label=label, comment=comment)
        self.update_label_signal.emit(comment)

        # 開始時刻
        start_time = datetime.now()
        start_time_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
        self.logger.info(f"【start】実行処理開始: ({count}回目) [{start_time_str}]")

        self.logger.debug(f"\nid: {user_info['id']}\npass: {user_info['pass']}\nworksheet_name: {gss_info}")

        try:
            # 処理を実施
            # TODO ここにシートの長さとインターバルインフォを渡す

            process_func(id_text=user_info['id'], pass_text=user_info['pass'], worksheet_name=gss_info['select_worksheet'], gss_url=gss_info['sheet_url'], interval_info=interval_info)

        except UnexpectedAlertPresentException as e:
            alert_comment = f"再出品の間隔が短いためを処理中断"
            self.logger.error(f"再出品の間隔が短いため、エラー 処理中断: {e}")
            self.update_label_signal.emit(alert_comment)

        except Exception as e:
            self.logger.error(f"タスク実行中にエラーが発生 この処理をスキップ: {e}")

        # 処理時間計測
        end_time = datetime.now()
        self.logger.debug(f"start_timeの型: {type(start_time)}, end_timeの型: {type(end_time)}")

        diff_time = end_time - start_time
        minutes, seconds = divmod(diff_time.total_seconds(), 60)
        diff_time_str = f"{int(minutes)} 分 {int(seconds)} 秒" if minutes > 0 else f"{int(seconds)} 秒"

        self.logger.info(f"【complete】実行処理完了: ({count}回目) [処理時間: {diff_time_str}]")


    # ----------------------------------------------------------------------------------
    # ストップ処理

    def stop(self, executor: ThreadPoolExecutor):
        executor.shutdown(wait=True)  # 並列処理の機械をシャットダウンする
        self.logger.info("すべてのタスクが完了しました")


    # ----------------------------------------------------------------------------------
# **********************************************************************************


class LoopProcessNoUpdate(QObject):
    update_label_signal = Signal(str)  # クラス変数

    def __init__(self):
        super().__init__()
        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()


        # インスタンス
        self.update_label = UpdateLabel()
        # self.update_event = UpdateEvent()
        self.time_manager = TimeManager()


    ####################################################################################
    # start_eventに使用するmain処理

    def main_task(self, stop_event: threading.Event, process_func: Callable, user_info: Dict, gss_info: str, interval_info: Dict):
        self.logger.info("これからmainloop処理を開始")
        self.process(stop_event=stop_event, process_func=process_func, user_info=user_info, gss_info=gss_info, interval_info=interval_info)


    ####################################################################################
    # ----------------------------------------------------------------------------------


    def process(self, stop_event: threading.Event, process_func: Callable, user_info: Dict, gss_info: str, interval_info: Dict, max_workers: int =3):
        executor = ThreadPoolExecutor(max_workers=max_workers)
        task_que = Queue()

        self._start_parallel_process(stop_event=stop_event, executor=executor, task_que=task_que, process_func=process_func, user_info=user_info, gss_info=gss_info, interval_info=interval_info)


    # ----------------------------------------------------------------------------------
    # 並列処理の実行
    # Queを管理するツールを起動→Queを作り続ける→監視ツールがQueを確認次第処理を開始→並列処理


    def _start_parallel_process(self, stop_event: threading.Event, executor: ThreadPoolExecutor, task_que: Queue, process_func: Callable, user_info: Dict, gss_info: str, interval_info: Dict):
        # 並列処理ロジックスタート（dispatcherはtaskを受取、ThreadPoolに割り当てる）
        dispatcher_thread = threading.Thread(
            target=self._task_manager,
            kwargs={
                'stop_event': stop_event,
                'executor' : executor,
                'task_que' : task_que,
                'process_func' : process_func,
                'user_info' : user_info,
                'gss_info' : gss_info,
                'interval_info': interval_info,
            }
        )
        dispatcher_thread.start()

        task_id = 1
        try:
            # queを作成し続ける
            while not stop_event.is_set():
                self._add_que_task(task_id=task_id, task_queue=task_que)
                self.logger.info(f'【{task_id} 個目】Queを追加')
                task_id += 1

                # 指定しているランダム待機
                random_wait = self.time_manager._random_sleep(random_info=interval_info)
                self.logger.info(f"{int(random_wait)} 秒待機して次のタスクを生成...")
                time.sleep(random_wait)

        except KeyboardInterrupt:
            self.logger.info("停止要求を受け付けました")

        finally:
            # 停止処理
            self.stop(executor=executor)
            comment = f"【全 {task_id} 回目】新規出品処理 停止中..."
            self.logger.warning(comment)
            self.update_label_signal.emit(comment)
            dispatcher_thread.join()

            next_comment = "待機中..."
            self.update_label_signal.emit(next_comment)

    # ----------------------------------------------------------------------------------
    # Queを追加

    def _add_que_task(self, task_id: int, task_queue: Queue):
        self.logger.info(f"タスク {task_id} を追加しました")
        task_queue.put(task_id)  # Queを追加


    # ----------------------------------------------------------------------------------
    # Queがないかを監視


    def _task_manager(self, stop_event: threading.Event, executor: ThreadPoolExecutor, task_que: Queue, process_func: Callable, user_info: Dict, gss_info: str, interval_info: Dict, delay: int=1):
        task_count = 0
        while not stop_event.is_set():
            try:
                # Queを取得
                task_id = task_que.get(timeout=1)
                self.logger.info(f"task_id: {task_id}")

                #! ここでメインのループ処理を実行する
                task = partial(self._task_contents, count=task_count, process_func=process_func, user_info=user_info, gss_info=gss_info, interval_info=interval_info)
                # 処理を実施
                executor.submit(task)

                task_count += 1
                task_que.task_done()  # タスクの完了を通知

            # Queが殻になったら待機
            except Empty:
                time.sleep(delay)

            except RuntimeError:
                executor.shutdown(wait=True)
                self.logger.info("シャットダウンをしてます。")

        self.logger.info(f"タスクディスパッチャーを停止します (新規出品数: {task_count})")
        comment = f"【{task_count}回目】新規出品処理 停止しました。"
        self.update_label_signal.emit(comment)
        self.logger.warning(comment)


    # ----------------------------------------------------------------------------------
    # taskの中身（実際に処理する内容）

    def _task_contents(self, count: int, process_func: Callable, user_info: Dict, gss_info: Dict, interval_info: Dict):
        comment = f"新規出品 処理中 {count + 1} 回目..."
        self.update_label_signal.emit(comment)

        # 開始時刻
        start_time = datetime.now()
        start_time_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
        self.logger.info(f"【start】実行処理開始: ({count}回目) [{start_time_str}]")

        self.logger.debug(f"\nid: {user_info['id']}\npass: {user_info['pass']}\nworksheet_name: {gss_info['select_worksheet']}\ngss_url: {gss_info['sheet_url']}\nmin_interval: {interval_info['min']}\nmax_interval: {interval_info['max']}")

        try:
            # 処理を実施
            # TODO ここにシートの長さとインターバルインフォを渡す
            process_func(id_text=user_info['id'], pass_text=user_info['pass'], worksheet_name=gss_info['select_worksheet'], gss_url=gss_info['sheet_url'], interval_info=interval_info)

        except UnexpectedAlertPresentException as e:
            alert_comment = f"再出品の間隔が短いためを処理中断"
            self.logger.error(f"再出品の間隔が短いため、エラー 処理中断: {e}")
            self.update_label_signal.emit(alert_comment)


        except Exception as e:
            self.logger.error(f"タスク実行中にエラーが発生 この処理をスキップ: {e}")

        # 処理時間計測
        end_time = datetime.now()
        self.logger.debug(f"start_timeの型: {type(start_time)}, end_timeの型: {type(end_time)}")

        diff_time = end_time - start_time
        minutes, seconds = divmod(diff_time.total_seconds(), 60)
        diff_time_str = f"{int(minutes)} 分 {int(seconds)} 秒" if minutes > 0 else f"{int(seconds)} 秒"

        self.logger.info(f"【complete】実行処理完了: ({count}回目) [処理時間: {diff_time_str}]")


    # ----------------------------------------------------------------------------------
    # ストップ処理

    def stop(self, executor: ThreadPoolExecutor):
        executor.shutdown(wait=True)  # 並列処理の機械をシャットダウンする
        self.logger.info("すべてのタスクが完了しました")


    # ----------------------------------------------------------------------------------
#! **********************************************************************************

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

    ####################################################################################


    def parallel_process(self, update_bool: bool, uptime_info: dict, stop_event: threading.Event, label: QLabel, update_event: threading.Event, update_func: Callable, process_func: Callable, user_info: Dict, gss_info: Dict, interval_info: Dict):
        # メインで行うスレッドを定義
        main_thread = threading.Thread(target=self.main_task, args=(
            update_bool, self.stop_event, label, update_event, update_func, process_func, user_info, gss_info, interval_info
        ), daemon=True)

        # 日付変更を検知するスレッド
        monitor_date_thread = threading.Thread(target=self.thread_event._monitor_date_change, args=(
            stop_event, label, update_event, update_bool, update_func, process_func, user_info, gss_info, interval_info
        ), daemon=True)

        # 指定した時間を検知するスレッド
        monitor_end_time_thread = threading.Thread(target=self.thread_event._monitor_end_time, args=(
            uptime_info, stop_event
        ), daemon=True)

        # 各スレッドスタート
        monitor_date_thread.start()
        monitor_end_time_thread.start()
        main_thread.start()






    # ----------------------------------------------------------------------------------
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
                # 直接タスクを実行
                self._task_contents(count=task_id, label=label, process_func=process_func, user_info=user_info, gss_info=gss_info, interval_info=interval_info)
                task_id += 1

        except KeyboardInterrupt:
            self.logger.info("停止要求を受け付けました")

        finally:
            end_comment = "stop_eventを検知認め終了"
            self.logger.info(end_comment)
            self.update_label_signal.emit("待機中...")

    ####################################################################################
    # タスクの実行

    def _task_contents(self, count: int, label: QLabel, process_func: Callable, user_info: Dict, gss_info: Dict, interval_info: Dict):
        comment = f"新規出品 処理中 {count} 回目 ..."
        self.update_label._update_label(label=label, comment=comment)
        self.update_label_signal.emit(comment)

        # 開始時刻
        start_time = datetime.now()
        start_time_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
        self.logger.info(f"【start】実行処理開始: ({count}回目) [{start_time_str}]")

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

        self.logger.info(f"【complete】実行処理完了: ({count}回目) [処理時間: {diff_time_str}]")

    # ----------------------------------------------------------------------------------
    # ストップ処理（不要なexecutor削除）

    def stop(self):
        self.logger.info("すべてのタスクが完了しました")


    # ----------------------------------------------------------------------------------

    def _main_thread_process(self, update_bool: bool, stop_event: threading.Event, label: QLabel, update_event: threading.Event, update_func: Callable, process_func: Callable, user_info: Dict, gss_info: Dict, interval_info: Dict):
        # メインで行うスレッドを定義
        main_thread = threading.Thread(target=self.main_task, kwargs={
            "update_bool": update_bool,
            "stop_event": stop_event,
            "label": label,
            "update_event": update_event,
            "update_func": update_func,
            "process_func": process_func,
            "user_info": user_info,
            "gss_info": gss_info,
            "interval_info": interval_info
        }, daemon=True)

        # スレッドスタート
        main_thread.start()


    # ----------------------------------------------------------------------------------


    def _monitor_date_change(self, stop_event: threading.Event, finish_event: threading.Event, label, update_event, update_bool, update_func, process_func, user_info, gss_info, interval_info):
        """日付変更を検知し、main_taskの終了を待ってから再実行するループ"""

        while not finish_event.is_set:
            # 📌 1. 次の日の 0 時になるまで待機
            now = datetime.now()
            next_day = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            wait_time = (next_day - now).total_seconds()

            self.logger.info(f"次の日まで {wait_time:.2f} 秒待機中...")
            threading.Timer(wait_time, self._trigger_date_change_task)


            self.logger.warning("【日付変更】タスクをリスタート準備中...")

            # 📌 2. 現在の `main_task` が終了するのを待つ
            if self.main_thread and self.main_thread.is_alive():
                self.logger.info("`main_task` の処理が完了するまで待機中...")
                self.main_thread.join()  # `main_task` の終了を待つ

            # 📌 3. `main_task` を再実行
            stop_event.clear()  # 停止フラグを解除
            self.logger.info("再度 `main_task` を開始！")

            self.start_main_task(update_bool, stop_event, label, update_event, update_func, process_func, user_info, gss_info, interval_info)

            # 📌 4. 次の日付変更を待機（ループへ戻る）

    # ----------------------------------------------------------------------------------

    def _trigger_date_change_task(self, finish_event: threading.Event, update_bool: bool, stop_event: threading.Event, label: QLabel, update_event: threading.Event, update_func: Callable, process_func: Callable, user_info: Dict, gss_info: Dict, interval_info: Dict):
        if finish_event.is_set:
            return

        self.logger.warning("【日付変更】タスクをリスタート準備中...")

        if self._main_thread_process and self._main_thread_process.is_alive():
            self.logger.info("`main_task` の処理が完了するまで待機中...")
            self._main_thread_process.join()  # `main_task` の終了を待つ

        # 📌 3. `main_task` を再実行
        stop_event.clear()  # 停止フラグを解除
        self.logger.info("再度 `main_task` を開始！")

        self._main_thread_process(update_bool=update_bool, stop_event=stop_event, label=label, update_event=update_event, update_func=update_func, process_func=process_func, user_info=user_info, gss_info=gss_info, interval_info=interval_info)

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

    # ----------------------------------------------------------------------------------

    def main_task(self, stop_event: threading.Event, process_func: Callable, user_info: Dict, gss_info: str, interval_info: Dict):
        self.logger.info("これからmainloop処理を開始")
        self.process(stop_event=stop_event, process_func=process_func, user_info=user_info, gss_info=gss_info, interval_info=interval_info)

    # ----------------------------------------------------------------------------------

    def process(self, stop_event: threading.Event, process_func: Callable, user_info: Dict, gss_info: str, interval_info: Dict):
        task_id = 1
        try:
            while not stop_event.is_set():
                self._execute_task(task_id=task_id, process_func=process_func, user_info=user_info, gss_info=gss_info, interval_info=interval_info)
                task_id += 1

        except KeyboardInterrupt:
            self.logger.info("停止要求を受け付けました")

    # ----------------------------------------------------------------------------------

    def _execute_task(self, task_id: int, process_func: Callable, user_info: Dict, gss_info: str, interval_info: Dict):
        self.logger.info(f"タスク {task_id} を実行します")
        comment = f"新規出品 処理中 {task_id} 回目..."
        self.update_label_signal.emit(comment)

        start_time = datetime.now()
        try:
            process_func(id_text=user_info['id'], pass_text=user_info['pass'], worksheet_name=gss_info['select_worksheet'], gss_url=gss_info['sheet_url'], interval_info=interval_info)
        except Exception as e:
            self.logger.error(f"タスク実行中にエラーが発生 この処理をスキップ: {e}")

        end_time = datetime.now()
        diff_time = end_time - start_time
        minutes, seconds = divmod(diff_time.total_seconds(), 60)
        diff_time_str = f"{int(minutes)} 分 {int(seconds)} 秒" if minutes > 0 else f"{int(seconds)} 秒"
        self.logger.info(f"タスク {task_id} の処理が完了しました [処理時間: {diff_time_str}]")

    # ----------------------------------------------------------------------------------
