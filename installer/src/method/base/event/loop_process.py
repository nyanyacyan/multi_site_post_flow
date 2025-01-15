# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# export PYTHONPATH="/Users/nyanyacyan/Desktop/project_file/domain_search/installer/src"


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import threading, asyncio
from datetime import datetime
from typing import Dict, Callable
from PySide6.QtWidgets import QLabel
from PySide6.QtCore import QObject


# 自作モジュール
from method.base.utils import Logger
from method.base.event.update_label import UpdateLabel
from method.base.event.update_event import UpdateEvent
from method.base.time_manager import TimeManager


# ----------------------------------------------------------------------------------
# **********************************************************************************


class LoopProcess(QObject):
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
    # ----------------------------------------------------------------------------------
    # 出品処理

    async def loop_process(self, stop_event: threading.Event, label: QLabel, process_func: Callable, user_info: Dict, gss_info: str, interval_info: Dict):
        try:
            self.logger.info(f"stop_eventの状態: {stop_event.is_set()}")

            # ストップフラグがis_setされるまでループ処理
            count = 0
            tasks = []

            async def repeat_task(task_id):
                nonlocal count  # 外側の関数の変数を使うための宣言

                count += 1
                await asyncio.sleep(1)

                comment = f"新規出品 処理中({count}回目)..."
                self.update_label._update_label(label=label, comment=comment)

                # 開始時刻
                start_time = datetime.now()
                start_time_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
                self.logger.info(f"【start】, タスクID: {task_id}) 実行処理開始: ({count}回目) [{start_time_str}]")

                self.logger.debug(f"\nid: {user_info['id']}\npass: {user_info['pass']}\nworksheet_name: {gss_info}")

                try:
                    # 処理を実施
                    await process_func(id_text=user_info['id'], pass_text=user_info['pass'], worksheet_name=gss_info)
                except Exception as e:
                    self.logger.error(f"タスク実行中にエラーが発生 この処理をスキップ: {e}")

                # 処理時間計測
                end_time = datetime.now()
                self.logger.debug(f"start_timeの型: {type(start_time)}, end_timeの型: {type(end_time)}")

                diff_time = end_time - start_time
                minutes, seconds = divmod(diff_time.total_seconds(), 60)
                diff_time_str = f"{int(minutes)} 分 {int(seconds)} 秒" if minutes > 0 else f"{int(seconds)} 秒"

                self.logger.info(f"【complete】実行処理完了: ({count}回目) [処理時間: {diff_time_str}]")

            # stop_eventが入るまでtaskを追加し続ける
            add_task_count = 0
            while not stop_event.is_set():
                self.logger.debug(f'add_task_count: {add_task_count}')
                random_wait = self.time_manager._random_sleep(random_info=interval_info)
                self.logger.info(f"{int(random_wait)} 秒待機して次のタスクを生成...")

                if add_task_count >= 1:

                    #! テスト用
                    half_time = random_wait / 2
                    await asyncio.sleep(half_time)
                    # await asyncio.sleep(random_wait)
                    self.logger.debug(f'次回までのtask待ち時間: {half_time}')

                # task生成して実行
                add_task_count += 1
                task_id = len(tasks) + 1
                task = asyncio.create_task(repeat_task(task_id))  # 非同期でtaskに追加
                tasks.append(task)

                # イベントループに制御を戻す
                await asyncio.sleep(0)
                self.logger.warning(f'{task_id} をtasksに追加しました')

            self.logger.info(f"ループ処理がストップしたのでタスク完了までお待ちください\n残りtask: {len(tasks)}個")

            # 残ったtaskのキャンセル
            for task in tasks:
                if not task.done():
                    task.cancel()

            # 残りのtaskが完了するのを待つ→制御
            all_tasks = await asyncio.gather(*tasks, return_exceptions=True)
            self.logger.info(f'all_tasks: {all_tasks}')

            self.logger.info(f"stop_eventの状態: {stop_event.is_set()}")

        except KeyError as e:
            comment = f"KeyError: {count}回目処理中 必須情報が正しく渡されなかった: {e}"
            self.update_label._update_label(label=label, comment=comment)
            self.logger.error(comment)

        except ConnectionError as e:
            comment = f"ConnectionError: {count}回目処理中 ネットワーク接続エラー: {e}"
            self.update_label._update_label(label=label, comment=comment)
            self.logger.error(comment)

        except Exception as e:
            comment = f"{count}回目処理中 処理中にエラーが発生: {e}"
            self.update_label._update_label(label=label, comment=comment)
            self.logger.error(comment)


    ####################################################################################

    ####################################################################################
    # start_eventに使用するmain処理

    def main_task(self, update_bool: bool, stop_event: threading.Event, label: QLabel, update_event: threading.Event, update_func: Callable, process_func: Callable, user_info: Dict, gss_info: str, interval_info: Dict):
        # 更新処理がありの場合に処理
        if update_bool:
            self.update_event._update_task(stop_event=stop_event, label=label, update_event=update_event, update_func=update_func, user_info=user_info)
        else:
            self.logger.info("更新処理「なし」のため更新処理なし")

        self.logger.info("これからmainloop処理を開始")
        loop = asyncio.get_event_loop()
        if not loop.is_running():
            loop.run_until_complete(self.loop_process(
                stop_event=stop_event,
                label=label,
                process_func=process_func,
                user_info=user_info,
                gss_info=gss_info,
                interval_info=interval_info,
            ))
        else:
            # イベントループが既に動作している場合
            asyncio.create_task(self.loop_process(
                stop_event=stop_event,
                label=label,
                process_func=process_func,
                user_info=user_info,
                gss_info=gss_info,
                interval_info=interval_info,
            ))

    ####################################################################################

