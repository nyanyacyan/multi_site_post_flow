# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# export PYTHONPATH="/Users/nyanyacyan/Desktop/project_file/domain_search/installer/src"


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import threading
from PySide6.QtWidgets import QLabel
from PySide6.QtCore import QObject, QMetaObject, Qt, QTimer, Q_ARG, QCoreApplication, QThread


# 自作モジュール
from method.base.utils import Logger
from method.base.event.update_label import UpdateLabel

# ----------------------------------------------------------------------------------
# **********************************************************************************


class CancelEvent(QObject):
    def __init__(self):
        super().__init__()
        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

        # インスタンス
        self.update_label = UpdateLabel()


    ####################################################################################
    # ----------------------------------------------------------------------------------
    # キャンセル処理

    def _cancel_event(self, label: QLabel, timer: QTimer, stop_flag: threading.Event, update_flag: threading.Event):
        # メインスレッドかを確認
        if QThread.currentThread() != QCoreApplication.instance().thread():
            self.update_label._update_label(label=label, comment="出品処理を停止中です...")
            # メインスレッドに指定の関数を割り込み
            QMetaObject.invokeMethod(self, "_stop_timer_and_update_gui", Qt.QueuedConnection, Q_ARG(QLabel, label), Q_ARG(QTimer, timer))

        # タイマーが設定されてればストップ
        else:
            self._stop_timer_and_update_gui(label=label, timer=timer)

        # 出品処理を停止
        stop_flag.set()

        # 更新完了されたフラグもリセット
        update_flag.clear()

        # キャンセル処理完了したため、待機中に変更
        self.update_label._update_label(label=label, comment="待機中...")


    # ----------------------------------------------------------------------------------


    def _stop_timer_and_update_gui(self, label: QLabel, timer: QTimer):
        if timer.isActive():
            timer.stop()
            self.update_label._update_label(label=label, comment="待機中...")


    # ----------------------------------------------------------------------------------
# **********************************************************************************


class CancelEventNoUpdate(QObject):
    def __init__(self):
        super().__init__()
        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

        # インスタンス
        self.update_label = UpdateLabel()


    ####################################################################################
    # ----------------------------------------------------------------------------------
    # キャンセル処理

    def _cancel_event(self, label: QLabel, timer: QTimer, stop_flag: threading.Event):
        # メインスレッドかを確認
        if QThread.currentThread() != QCoreApplication.instance().thread():
            self.update_label._update_label(label=label, comment="出品処理を停止中です...")
            # メインスレッドに指定の関数を割り込み
            QMetaObject.invokeMethod(self, "_stop_timer_and_update_gui", Qt.QueuedConnection, Q_ARG(QLabel, label), Q_ARG(QTimer, timer))

        # タイマーが設定されてればストップ
        else:
            self._stop_timer_and_update_gui(label=label, timer=timer)

        # 出品処理を停止
        stop_flag.set()

        # キャンセル処理完了したため、待機中に変更
        self.update_label._update_label(label=label, comment="待機中...")


    # ----------------------------------------------------------------------------------


    def _stop_timer_and_update_gui(self, label: QLabel, timer: QTimer):
        if timer.isActive():
            timer.stop()
            self.update_label._update_label(label=label, comment="待機中...")


    # ----------------------------------------------------------------------------------
