# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# export PYTHONPATH="/Users/nyanyacyan/Desktop/project_file/domain_search/installer/src"

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
from PySide6.QtWidgets import QVBoxLayout, QLabel, QGroupBox


# ----------------------------------------------------------------------------------
# **********************************************************************************


class StatusManager(QGroupBox):
    def __init__(self):
        super().__init__()

        self.status_label = QLabel("待機中...")
        self.status_label.setStyleSheet("color: black;")

        # レイアウトを設定
        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        self.setLayout(layout)


    ####################################################################################
    # アクションを実行

    def update_status(self, msg: str, color: str= "black"):
        self.status_label.setText(msg)
        self.status_label.setStyleSheet(f"color: {color};")


    ####################################################################################
