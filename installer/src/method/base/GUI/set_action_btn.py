# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# export PYTHONPATH="/Users/nyanyacyan/Desktop/project_file/domain_search/installer/src"

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
from typing import Dict, Callable
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGroupBox

# 自作モジュール



# ----------------------------------------------------------------------------------
# **********************************************************************************


class ActionBtn(QGroupBox):
    def __init__(self, gui_info: Dict, process_func: Callable, cancel_func: Callable):
        super().__init__()

        # 処理関数をここで所持
        self.process_func = process_func
        self.cancel_func = cancel_func

        # レイアウトを設定
        self.setLayout(self._create_action_btn_group(gui_info=gui_info))


    ####################################################################################
    # アクションを実行

    def _create_action_btn_group(self, gui_info: Dict, process_func: Callable, cancel_func: Callable):
        action_btn_layout = QVBoxLayout()

        # ボタンを設置
        self.process_btn = self._action_btn(name_in_btn=gui_info['PROCESS_BTN_NAME'], action_func=process_func)
        self.cancel_btn = self._action_btn(name_in_btn=gui_info['CANCEL_BTN_NAME'], action_func=cancel_func)


        # end_updateのレイアウト作成
        btn_layout = QHBoxLayout()  # 横レイアウト
        btn_layout.addWidget(self.process_btn)
        btn_layout.addWidget(self.cancel_btn)

        # end_updateをグループに追加
        action_btn_layout.addLayout(btn_layout)

        # status_labelを追加
        self.status_label = self._status_label()
        action_btn_layout.addWidget(self.status_label)

        # 各ボタンのクリックイベントを定義
        self.process_btn.clicked.connect(self._start_processing)
        self.cancel_btn.clicked.connect(self._cancel_processing)

        return action_btn_layout


    ####################################################################################
    # ----------------------------------------------------------------------------------
    # buttonを定義

    def _action_btn(self, name_in_btn: str):
        action_btn = QPushButton(name_in_btn)
        return action_btn


    # ----------------------------------------------------------------------------------
    # ステータス状況を表示させる

    def _status_label(self):
        status_label = QLabel("待機中...")
        status_label.setStyleSheet("color: green;")
        return status_label


    # ----------------------------------------------------------------------------------
    # process_btnを実行した際のアクション

    def _start_processing(self):
        # ラベルにコメントを追記
        self.status_label.setText("出品処理中...")

        self.process_btn.setEnabled(False)  # 開始ボタンを押せないSTS変更
        self.cancel_btn.setEnabled(True)  # キャンセルボタンを押せるSTS変更

        self.process_func()


    # ----------------------------------------------------------------------------------
    # cancel_btnを実行した際のアクション

    def _cancel_processing(self):

        self.status_label.setText("処理を中断してます...")

        self.process_btn.setEnabled(True)  # 開始ボタンを押せる状態にSTS変更
        self.cancel_btn.setEnabled(False)  # キャンセルボタンを押せないSTS変更

        self.cancel_func()

        # キャンセル処理完了後に「待機中」に戻す
        self.status_label.setText("待機中...")

    # ----------------------------------------------------------------------------------
