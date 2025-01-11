# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# export PYTHONPATH="/Users/nyanyacyan/Desktop/project_file/domain_search/installer/src"

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
from PySide6.QtWidgets import QVBoxLayout, QLabel, QGroupBox, QApplication
from PySide6.QtCore import QTimer

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
        QApplication.processEvents()
        QTimer.singleShot(0, lambda: self._update_label(msg, color))

    ####################################################################################

    def _update_label(self, msg: str, color: str= "black"):
        print(f"Status Update: {msg}")
        self.status_label.setText(msg)
        self.status_label.setStyleSheet(f"color: {color};")


    ####################################################################################


    def _get_status_text(self):
        return self.status_label.text()
