# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# export PYTHONPATH="/Users/nyanyacyan/Desktop/project_file/domain_search/installer/src"


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import threading
from datetime import timedelta
from typing import Dict, Callable
from PySide6.QtWidgets import QLabel, QApplication
from PySide6.QtCore import QObject, QMetaObject, Qt, QTimer, Q_ARG, QCoreApplication, QThread


# 自作モジュール
from method.base.utils import Logger
from method.base.event.update_label import UpdateLabel

# ----------------------------------------------------------------------------------
# **********************************************************************************


class UpdateEvent(QObject):
    def __init__(self):
        super().__init__()
        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

        # インスタンス
        self.update_label = UpdateLabel()


    ####################################################################################
    # ----------------------------------------------------------------------------------
    # 更新処理

    def _update_task(self, stop_event: threading.Event, update_event: threading.Event, label: QLabel, update_func: Callable, user_info: Dict):
        # 出品処理を停止
        stop_event.set()
        if stop_event.is_set():
            comment = "【complete】メイン処理を停止フラグを実施。"
            self.update_label._update_label(label=label, comment=comment)

        # 更新処理ストップフラグをクリア→更新処理が実施できるようにする
        if update_event.is_set():
            update_event.clear()
            comment = "【complete】更新処理未実施のため、フラグクリア処理は未実施"
            self.logger.info(comment)

        comment = "更新処理中..."
        self.update_label._update_label(label=label, comment=comment)

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

        comp_comment = "更新処理が完了しました。"
        self.update_label._update_label(label=label, comment=comp_comment)
        self.logger.debug(comp_comment)


    # ----------------------------------------------------------------------------------
