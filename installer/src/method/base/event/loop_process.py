# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# export PYTHONPATH="/Users/nyanyacyan/Desktop/project_file/domain_search/installer/src"


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import threading
from datetime import datetime
from typing import Dict, Callable
from PySide6.QtWidgets import QLabel
from PySide6.QtCore import QObject


# 自作モジュール
from method.base.utils import Logger
from method.base.event.update_label import UpdateLabel
from method.base.event.update_event import UpdateEvent

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


    ####################################################################################
    # ----------------------------------------------------------------------------------
    # 出品処理

    def loop_process(self, stop_event: threading.Event, label: QLabel, user_info: Dict, interval_info: Dict):
        try:
            # ストップフラグがis_setされるまでループ処理
            count = 0
            while not stop_event.is_set():

                if stop_event.is_set():
                    comment = "出品処理処理を停止..."
                    self.update_label._update_label(label=label, comment=comment)
                    self.logger.info("ストップイベントフラグを確認。出品処理を停止")
                    break

                count += 1
                self.status_label.update_status(msg=f"実行処理中({count}回目)...", color="blue")
                comment = f"実行処理中({count}回目)..."
                self.update_label._update_label(label=label, comment=comment)

                # 開始時刻
                start_time = datetime.now()
                start_time_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
                self.logger.info(f"【start】実行処理開始: ({count}回目) [{start_time_str}]")

                # 処理を実施
                self.process_func(id_text=user_info['id'], pass_text=user_info['pass'], worksheet_name=user_info['worksheet'])

                # 処理時間計測
                end_time = datetime.now()
                diff_time = end_time - start_time
                minutes, seconds = divmod(diff_time.total_seconds(), 60)
                diff_time_str = f"{minutes} 分 {seconds} 秒" if minutes > 0 else f"{seconds} 秒"

                self.logger.info(f"【complete】実行処理完了: ({count}回目) [処理時間: {diff_time_str}]")

                # 設定した待機をランダムで実行
                self.time_manager._random_sleep(random_info=interval_info)

        except KeyError as e:
            comment = f"KeyError: {count}回目処理中 必須情報が不足しています: {e}"
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

    def main_task(self, update_bool: bool, stop_event: threading.Event, label: QLabel, update_event: threading.Event, update_func: Callable, user_info: Dict, interval_info: Dict):
        # 更新処理がありの場合に処理
        if update_bool:
            self.update_event._update_task(stop_event=stop_event, label=label, update_event=update_event, update_func=update_func, user_info=user_info)
        else:
            self.logger.info("更新処理「なし」のため更新処理なし")

        self.loop_process(stop_event=stop_event, label=label, user_info=user_info, interval_info=interval_info)


    ####################################################################################

