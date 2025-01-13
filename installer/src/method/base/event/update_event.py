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

        comment = "更新処理中..."
        self.update_label._update_label(label=label, comment=comment)

        # 更新処理を実施
        update_func(id_text=user_info['id'], pass_text=user_info['pass'])

        # 更新作業完了フラグを立てる
        update_complete_event.set()
        self.logger.debug(f'更新処理が完了したのでフラグ立て: {__name__}')

        comp_comment = "更新処理が完了しました。"
        self.update_label._update_label(label=label, comment=comp_comment)

        self.logger.debug(f'更新処理が完了しました。: {__name__}')


    # ----------------------------------------------------------------------------------


    # def _update_label_text(self, label: QLabel, comment: str):
    #     """ラベルのテキストを更新"""
    #     self.logger.debug(f'_update_label_textが呼ばれました。更新内容: {comment}')

    #     # ラベルのIDを確認
    #     self.logger.debug(f'ラベルのID: {id(label)}')

    #     # テキストを設定
    #     label.setText(comment)  # コメントを挿入
    #     label.repaint()  # 再描画を強制

    #     QApplication.processEvents()


    # # ----------------------------------------------------------------------------------


    # def _update_label(self, label: QLabel, comment: str):
    #     # イベントループ実行確認
    #     if not QCoreApplication.instance():
    #         self.logger.warning(f'イベントループが開始されてません: 【ラベル作成中】{comment} 現在のラベル: {label.text()} ')
    #         return  # スキップ
    #     else:
    #         self.logger.info(f'イベントループ実行中です: {__name__}')

    #     # メインスレッド確認
    #     if QThread.currentThread() != QCoreApplication.instance().thread():
    #         self.logger.warning(f'現在のスレッドはメインスレッドではありません。メインスレッドで処理を実行します')
    #         QTimer.singleShot(0, lambda: self._update_label_text(label, comment))
    #         # QMetaObject.invokeMethod(self, "_update_label_text", Qt.QueuedConnection, Q_ARG(QLabel, label), Q_ARG(str, comment))
    #     else:
    #         self.logger.info(f'現在のスレッドはメインスレッドです。処理を実施します。')
    #         self._update_label_text(label, comment)

    #     # 実施した処理のあと反映してるのか確認
    #     label_text = label.text()
    #     print(f"label_text: {label_text}")
    #     if label_text != comment:
    #         self.logger.error(f"ラベル更新に失敗しました: {comment}")
    #         return


    # # ----------------------------------------------------------------------------------
