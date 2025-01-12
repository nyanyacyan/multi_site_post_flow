# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# export PYTHONPATH="/Users/nyanyacyan/Desktop/project_file/domain_search/installer/src"


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import threading
from datetime import timedelta
from typing import Dict, Callable
from PySide6.QtWidgets import QLabel
from PySide6.QtCore import QObject, QMetaObject, Qt, QTimer


# 自作モジュール
from method.base.utils import Logger


# ----------------------------------------------------------------------------------
# **********************************************************************************


class UpdateEvent(QObject):
    def __init__(self):
        super().__init__()
        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()


    ####################################################################################
    # ----------------------------------------------------------------------------------
    # 更新処理

    def _update_task(self, stop_event: threading.Event, update_complete_event: threading.Event, label: QLabel, update_func: Callable, user_info: Dict):
        # 出品処理を停止
        stop_event.set()

        # 更新処理ストップフラグをクリア→更新処理が実施できるようにする
        update_complete_event.clear()
        self.logger.debug(f'更新処理のクリアを実施: {__name__}')

        if label is None:
            print("ラベルがNoneです")

        # ステータス変更
        comment = "[DEBUG] ラベルを更新: 更新処理中..."
        QTimer.singleShot(0, lambda: print(comment) or label.setText(comment))
        label_text = label.text()
        print(f"label_text: {label_text}")
        if label_text != comment:
            print("更新されてない")

        # 更新処理を実施
        update_func(id_text=user_info['id'], pass_text=user_info['pass'])

        # 更新作業完了フラグを立てる
        update_complete_event.set()
        self.logger.debug(f'更新処理が完了したのでフラグ立て: {__name__}')

        comp_comment = "[DEBUG] ラベルを更新: 更新処理が完了しました。"
        QTimer.singleShot(0, lambda: print(comp_comment) or label.setText(comp_comment))
        if label.text() != comp_comment:
            print("更新されてない")

        self.logger.debug(f'更新処理が完了しました。: {__name__}')


    # ----------------------------------------------------------------------------------
