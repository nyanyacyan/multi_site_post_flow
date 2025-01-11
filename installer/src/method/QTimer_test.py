from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
import sys

class TimerTestApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QTimer Test")
        self.resize(300, 200)

        # ラベルとレイアウト
        self.label = QLabel("カウント開始", self)
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

        # QTimerの設定
        self.counter = 10
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_label)
        self.timer.start(1000)  # 1秒ごとに発火

    def update_label(self):
        if self.counter > 0:
            self.label.setText(f"残り時間: {self.counter} 秒")
            self.counter -= 1
        else:
            self.label.setText("カウントダウン終了")
            self.timer.stop()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TimerTestApp()
    window.show()
    sys.exit(app.exec())






from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
import sys


class SingleShotTest(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Single Shot Timer Test")
        self.resize(300, 200)

        # ラベルとレイアウト
        self.label = QLabel("タイマー待機中...", self)
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

        # タイマーの初期化と設定
        self.start_timer()

    def start_timer(self):
        self.label.setText("5秒後に変更します...")
        QTimer.singleShot(5000, self.update_label)  # 5秒後に `update_label` を呼び出す

    def update_label(self):
        self.label.setText("ラベルが変更されました！")
        print("タイマーが発火しました")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SingleShotTest()
    window.show()
    sys.exit(app.exec())
