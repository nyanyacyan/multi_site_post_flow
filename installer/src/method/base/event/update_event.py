# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# export PYTHONPATH="/Users/nyanyacyan/Desktop/project_file/domain_search/installer/src"


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import threading
from datetime import timedelta
from typing import Dict, Callable
from PySide6.QtWidgets import QLabel
from PySide6.QtCore import QObject, QMetaObject, Qt, QTimer, Q_ARG, QCoreApplication, QThread


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

        before_label_text = label.text()
        self.logger.debug(f'before_label_text: {before_label_text}')

        comment = "[DEBUG] ラベルを更新: 更新処理中..."

        if not QCoreApplication.instance():
            print("[DEBUG] イベントループが開始されていません")
        else:
            print("[DEBUG] イベントループが開始されています")

        if QThread.currentThread() != QCoreApplication.instance().thread():
            print("[DEBUG] 現在のスレッドはメインスレッドではありません。メインスレッドで処理を実行します")
            QMetaObject.invokeMethod(self, "_update_label_text", Qt.QueuedConnection, Q_ARG(QLabel, label), Q_ARG(str, comment))
        else:
            print("[DEBUG] 現在のスレッドはメインスレッドです")
            self._update_label_text(label, comment)

        # ステータス変更
        # QTimer.singleShot(0, lambda: print("[DEBUG] QTimer.singleShotがスケジュールされました") or self._update_label_text(label, comment))

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
        QTimer.singleShot(0, lambda: self._update_label_text(label, comp_comment))
        if label.text() != comp_comment:
            print("更新されてない")

        self.logger.debug(f'更新処理が完了しました。: {__name__}')


    # ----------------------------------------------------------------------------------


    def _update_label_text(self, label: QLabel, comment: str):
        """ラベルのテキストを更新"""
        print(f"[DEBUG] _update_label_textが呼ばれました。更新内容: {comment}")

        # ラベルのIDを確認
        print(f"[DEBUG] ラベルのID: {id(label)}")

        # テキストを設定
        label.setText(comment)

        # 再描画を強制
        label.repaint()
        label.parentWidget().update()  # 親ウィジェットも再描画

        # サイズ調整
        label.adjustSize()

        # デバッグ用
        print(f"[DEBUG] 更新後のラベル内容: {label.text()}")
        print(f"[DEBUG] ラベルの可視状態: {label.isVisible()}")

    # ----------------------------------------------------------------------------------
