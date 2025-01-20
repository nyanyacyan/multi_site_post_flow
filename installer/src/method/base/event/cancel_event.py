# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# export PYTHONPATH="/Users/nyanyacyan/Desktop/project_file/domain_search/installer/src"


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import threading, os, sys, signal
from PySide6.QtWidgets import QLabel
from PySide6.QtCore import QObject


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

    def _cancel_event(self, label: QLabel):
        self.update_label._update_label(label=label, comment="アプリケーションを終了しています...")

        threading_process = [f"スレッド名: {t.name}, スレッドID: {t.ident}" for t in threading.enumerate()]
        self.logger.debug(f'threading_process: {threading_process}')

        os.kill(os.getpid(), signal.SIGKILL)  # 現在のプロセスを強制終了
        sys.exit(0)

    # ----------------------------------------------------------------------------------


    def _restart_app(self):
        """アプリケーションを再起動する"""

        # プロセスを完全終了して再起動
        python = sys.executable
        os.execl(python, python, *sys.argv)
        os.kill(os.getpid(), signal.SIGKILL)
        sys.exit(0)

    # ----------------------------------------------------------------------------------

