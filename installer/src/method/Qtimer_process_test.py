import sys
from datetime import timedelta
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from PySide6.QtCore import QTimer

# 必要なクラスをインポート
from method.base.GUI.Qtimer_content import CountDownQTimer  # CountDownQTimerの正しいパスを指定してください

class TestCountDownApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CountDown QTimer Test")
        self.resize(300, 200)

        # レイアウト
        self.label = QLabel("カウントダウン待機中...")
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

        # カウントダウンテスト開始
        uptime_info = {"start_diff": timedelta(seconds=10), "end_diff": timedelta(seconds=20)}
        self.timer = CountDownQTimer(self.label, uptime_info)
        self.timer.countdown_event()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestCountDownApp()
    window.show()
    sys.exit(app.exec())
