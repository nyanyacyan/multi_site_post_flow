# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# export PYTHONPATH="/Users/nyanyacyan/Desktop/project_file/domain_search/installer/src"


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import threading
from typing import Dict, Callable
from PySide6.QtCore import QObject, Signal

# 自作モジュール
from method.base.utils import Logger

# ----------------------------------------------------------------------------------
# **********************************************************************************


class UpdateEvent(QObject):
    update_label_signal = Signal(str)  # クラス変数

    def __init__(self):
        super().__init__()
        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()


    ####################################################################################
    # ----------------------------------------------------------------------------------
    # 更新処理

    def _update_task(self, stop_event: threading.Event, update_event: threading.Event, update_func: Callable, user_info: Dict):
        # 出品処理を停止
        stop_event.set()
        if stop_event.is_set():
            stop_flag_comment = "【complete】メイン処理を停止フラグを実施。"
            # self.update_label_signal.emit(stop_flag_comment)
            self.logger.info(stop_flag_comment)


        # 更新処理ストップフラグをクリア→更新処理が実施できるようにする
        if update_event.is_set():
            update_event.clear()
            update_flag_comment = "【complete】更新処理未実施のため、フラグクリア処理は未実施"
            self.logger.info(update_flag_comment)


        # 更新処理を実施
        update_func(id_text=user_info['id'], pass_text=user_info['pass'])

        # 更新作業完了フラグを立てる
        update_event.set()
        if update_event.is_set():
            self.logger.debug(f'【complete】更新処理を上限まで実施。アップデート完了フラグOK: {__name__}')
        else:
            self.logger.error(f"フラグ立てに失敗")
            return

        stop_event.clear()
        self.logger.info(f"stop_eventフラグをクリア: {stop_event.is_set()}")


    # ----------------------------------------------------------------------------------
