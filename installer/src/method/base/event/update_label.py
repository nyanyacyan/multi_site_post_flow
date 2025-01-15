# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# export PYTHONPATH="/Users/nyanyacyan/Desktop/project_file/domain_search/installer/src"


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
from PySide6.QtWidgets import QLabel, QApplication
from PySide6.QtCore import QObject, QTimer, QCoreApplication, QThread


# 自作モジュール
from method.base.utils import Logger


# ----------------------------------------------------------------------------------
# **********************************************************************************


class UpdateLabel(QObject):
    def __init__(self):
        super().__init__()
        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()


    ####################################################################################


    def _update_label(self, label: QLabel, comment: str):
        # イベントループ実行確認
        if not QCoreApplication.instance():
            self.logger.warning(f'イベントループが開始されてません: 【ラベル作成中】{comment} 現在のラベル: {label.text()} ')
            return  # スキップ
        else:
            self.logger.info(f'イベントループ実行中です: {__name__}')

        # メインスレッド確認
        if QThread.currentThread() != QCoreApplication.instance().thread():
            self.logger.warning(f'現在のスレッドはメインスレッドではありません。メインスレッドで処理を実行します')
            QTimer.singleShot(0, lambda: self.update_label_text(label, comment))
            # QMetaObject.invokeMethod(self, "update_label_text", Qt.QueuedConnection, Q_ARG(QLabel, label), Q_ARG(str, comment))
        else:
            self.logger.info(f'現在のスレッドはメインスレッドです。処理を実施します。')
            self._update_label_text(label, comment)

        # 実施した処理のあと反映してるのか確認
        label_text = label.text()
        self.logger.debug(f"label_text: {label_text}")
        if label_text != comment:
            self.logger.error(f"\n【ラベル更新に失敗しました】\n変更したいコメント: {comment}\n変更前コメント: {label_text}")
            return


    ####################################################################################
    # ----------------------------------------------------------------------------------


    def _update_label_text(self, label: QLabel, comment: str):
        """ラベルのテキストを更新"""
        self.logger.debug(f'_update_label_textが呼ばれました。更新内容: {comment}')

        # ラベルのIDを確認
        self.logger.debug(f'ラベルのID: {id(label)}')

        # テキストを設定
        label.setText(comment)  # コメントを挿入
        label.repaint()  # 再描画を強制

        QApplication.processEvents()


    # ----------------------------------------------------------------------------------


