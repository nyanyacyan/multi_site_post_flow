# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# export PYTHONPATH="/Users/nyanyacyan/Desktop/project_file/domain_search/installer/src"


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
from typing import Dict
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QRadioButton, QGroupBox

# 自作モジュール



# ----------------------------------------------------------------------------------
# **********************************************************************************


class RadioSelect(QGroupBox):
    def __init__(self, gui_info: Dict) -> None:
        super().__init__(gui_info['UPDATE_SELECT_GROUP_TITLE'])

        # タイトルのスタイルを設定
        self.setStyleSheet("""
            QGroupBox {
                font-size: 12px;  /* 文字の大きさ */
                font-weight: bold;  /* 太字 */
                text-decoration: underline;  /* 下線 */
            }
        """)

        # レイアウトを設定
        self.setLayout(self._create_radio_select_group(gui_info=gui_info))

        # ラジオボタンのシグナルを受けて更新
        self._signal_radio_event()

    ####################################################################################
    # 値を取得

    def get_radio_info(self):
        if self.radio_true.isChecked():
            return True
        else:
            return False


    ####################################################################################
    # ラジオボタンの設計

    def _create_radio_select_group(self, gui_info: Dict):
        radio_layout = QVBoxLayout()

        # ラジオボタンを設置
        self.radio_true = QRadioButton(gui_info['RADIO_BTN_TRUE_TITLE'])
        self.radio_false = QRadioButton(gui_info['RADIO_BTN_FALSE_TITLE'])

        # デフォルトでチェックを入れておく
        self.radio_true.setChecked(True)

        # radioのレイアウト作成
        radio_select_layout = QHBoxLayout()  # 横レイアウト
        radio_select_layout.addWidget(self.radio_true)
        radio_select_layout.addWidget(self.radio_false)

        # end_radioをグループに追加
        radio_layout.addLayout(radio_select_layout)

        return radio_layout


    ####################################################################################
    # ----------------------------------------------------------------------------------
    # ラジオボタンのシグナルをキャッチする

    def _signal_radio_event(self):
        self.radio_true.toggled.connect(self._update_radio_state)
        self.radio_false.toggled.connect(self._update_radio_state)


    # ----------------------------------------------------------------------------------
    # 更新状態をログに残す

    def _update_radio_state(self):
        # ラジオボタンの状態を取得してログを表示（例: 状態更新処理を追加可能）
        print(f"Radio Button True: {self.radio_true.isChecked()}, False: {self.radio_false.isChecked()}")


    # ----------------------------------------------------------------------------------
