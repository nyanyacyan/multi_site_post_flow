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


class UpdateSelect(QGroupBox):
    def __init__(self, gui_info: Dict) -> None:
        super().__init__(gui_info['UPDATE_SELECT_GROUP_TITLE'])

        # レイアウトを設定
        self.setLayout(self._create_update_select_group(gui_info=gui_info))


    ####################################################################################
    # 値を取得

    def get_update_info(self):
        if self.update_true.isChecked():
            return True
        else:
            return False


    ####################################################################################
    # ラジオボタンの設計

    def _create_update_select_group(self, gui_info: Dict):
        update_layout = QVBoxLayout()

        # ラジオボタンを設置
        self.update_true = QRadioButton(gui_info['RADIO_BTN_TRUE_TITLE'])
        self.update_false = QRadioButton(gui_info['RADIO_BTN_FALSE_TITLE'])

        # デフォルトでチェックを入れておく
        self.update_true.setChecked(True)

        # end_updateのレイアウト作成
        update_select_layout = QHBoxLayout()  # 横レイアウト
        update_select_layout.addWidget(self.update_true)
        update_select_layout.addWidget(self.update_false)

        # end_updateをグループに追加
        update_layout.addLayout(update_select_layout)

        return update_layout


    ####################################################################################
