# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# export PYTHONPATH="/Users/nyanyacyan/Desktop/project_file/multi_site_post_flow/installer/src"

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import threading, sys
from typing import Dict, Callable
from PySide6.QtWidgets import QWidget, QVBoxLayout, QApplication, QLabel
from PySide6.QtGui import QIcon
from PySide6.QtGui import QGuiApplication


# 自作モジュール
from method.base.GUI.set_user_info import UserInfoForm
from method.base.GUI.set_gss_info import GSSInfoForm
from method.base.GUI.set_interval_time import IntervalTimeForm
from method.base.GUI.set_uptime import SetUptime
from method.base.GUI.set_action_btn import ActionBtn
from method.base.event.countdown_event import CountdownEvent
from method.base.event.cancel_event import CancelEvent
from method.base.event.loop_process import LoopProcessOrderNoUpdate

from method.base.time_manager import TimeManager
from method.base.path import BaseToPath
from method.flow_rmt_club_new_item import FlowRMTProcess
from method.base.GUI.Qtimer_content import CountDownQTimer, CheckFlag
from method.base.event.update_label import UpdateLabel


# const
from method.const_element import GssInfo, GuiInfo


# ----------------------------------------------------------------------------------
# **********************************************************************************


class MainRMTClubApp(QWidget):
    def __init__(self, gui_info: Dict, process_func: Callable):
        super().__init__()

        self.countdown_timer = None  # クラスの属性として初期化

        # 画面サイズを取得
        screen_geometry = QGuiApplication.primaryScreen().geometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        # ウィンドウサイズ
        window_width = gui_info["GUI_WIDTH"]
        window_height = gui_info["GUI_HEIGHT"]

        # 配置の割合
        x_ratio = gui_info["X_RATIO"]
        y_ratio = gui_info["Y_RATIO"]

        # 割合から座標を計算
        window_x = int(screen_width * x_ratio) - window_width
        window_y = int(screen_height * y_ratio) - int(window_height / 2)

        # サイズと位置を設定
        self.setGeometry(window_x, window_y, window_width, window_height)

        # メインタイトル
        self.setWindowTitle(gui_info['MAIN_WINDOW_TITLE'])

        # logo
        self.path =BaseToPath()
        logo_path = self.path.getInputLogoFilePath(fileName=gui_info['LOGO_NAME'])
        QGuiApplication.setWindowIcon(QIcon(str(logo_path)))

        # メインレイアウトの設定
        self.layout = QVBoxLayout()

        # 各padding設定
        self.layout.setContentsMargins(15, 30, 15, 15)

        # 各レイアウト間の幅
        self.layout.setSpacing(15)

        self.setLayout(self.layout)


        # カウントダウン用ラベルを追加
        self.process_label = QLabel("待機中...")
        self.process_label.setFixedSize(380, 20)


        # 各GUIパーツを追加
        self.user_info_form = UserInfoForm(gui_info=gui_info)
        self.gss_info_form = GSSInfoForm(gui_info=gui_info)
        self.interval_form = IntervalTimeForm(gui_info=gui_info)
        self.uptime_form = SetUptime(gui_info=gui_info)
        self.action_btn_form = ActionBtn(label=self.process_label, gui_info=gui_info, process_func=self.entry_event, cancel_func=self.cancel_process)


        # レイアウトに追加
        self.layout.addWidget(self.user_info_form)
        self.layout.addWidget(self.gss_info_form)
        self.layout.addWidget(self.interval_form)
        self.layout.addWidget(self.uptime_form)
        self.layout.addWidget(self.action_btn_form)
        self.layout.addWidget(self.process_label)


        # フラグをセット（フラグを立てる場合には self.stop_event.set() を実施）
        self.stop_flag = threading.Event()
        self.finish_flag = threading.Event()
        self.start_event_flag = threading.Event()

        # メインの処理を受け取る
        self.process_func = process_func

        # ここでupdateの要否を確認→bool
        self.update_bool = True  # 初期値を設定

        # インスタンス
        self.time_manager = TimeManager()
        self.countdown_event = CountdownEvent()
        self.check_flag = CheckFlag()
        self.cancel_event = CancelEvent()
        self.main_event = LoopProcessOrderNoUpdate()
        self.update_label = UpdateLabel()

        # シグナル受信
        self.main_event.update_label_signal.connect(self._update_label)

        # タイマーの設定
        self.uptime_info = {}  # 初期化
        self.timer = CountDownQTimer(label=self.process_label, uptime_info=self.uptime_info, start_event_flag=self.start_event_flag)


    ####################################################################################
    # エントリー

    def entry_event(self):
        # 開始時間と終了時間を取得
        self.uptime_info = self.uptime_form.get_uptime_info()
        self.countdown_event.entry_event(uptime_info=self.uptime_info, label=self.process_label, start_event_flag=self.start_event_flag, event_func=self.start_event)

    # ----------------------------------------------------------------------------------
    # start_event

    def start_event(self):
        try:
            self.user_info = self.user_info_form.get_user_info()  # 入力したIDとパス
            self.gss_info = self.gss_info_form.get_gss_info()  # ドロップダウンメニューから選択された値
            self.interval_info = self.interval_form.get_interval_info()  # TODO 処理の実施間隔の値

            # 各スレッドスタート
            self._start_main_thread()
            self._start_monitor_date_thread()
            self._start_monitor_end_time_thread()

        except Exception as e:
            print(f"処理中にエラーが発生: {e}")

    # ----------------------------------------------------------------------------------
    # キャンセル処理

    def cancel_process(self):
        self.cancel_event._cancel_event(label=self.process_label)

    # ----------------------------------------------------------------------------------
    # メインスレッドの実行

    def _start_main_thread(self):
            # メイン処理を別スレッドの定義
            self.main_task_thread = threading.Thread(
                target=self.main_event.main_task,
                kwargs={
                    "stop_event": self.stop_flag,
                    "label": self.process_label,
                    "process_func": self.process_func,
                    "user_info": self.user_info,
                    "gss_info": self.gss_info,
                    "interval_info": self.interval_info,
                }, daemon=True )

            # 各スレッドスタート
            self.main_task_thread.start()


    # ----------------------------------------------------------------------------------
    # 日付が変わるまでの時間を算出して待機する

    def _start_monitor_date_thread(self):
        # 日付変更の監視taskをスタート
        try:
            self.date_change_thread = threading.Thread(
                target=self.main_event._monitor_date_change,
                kwargs = {
                    "stop_event": self.stop_flag,
                    "finish_event": self.finish_flag,
                    "main_thread": self.main_task_thread,
                    "label": self.process_label,
                    "process_func": self.process_func,
                    "user_info": self.user_info,
                    "gss_info": self.gss_info,
                    "interval_info": self.interval_info,
                }, daemon=True )

            # threadスタート
            self.date_change_thread.start()

        except Exception as e:
            print(f"_start_monitor_date_thread を処理中にエラーが発生: {e}")



    # ----------------------------------------------------------------------------------
    # 設定している時間になったら設定したtaskを実行

    def _start_monitor_end_time_thread(self):
        try:
            # 終了時間の監視taskをスタート
            self.end_time_thread = threading.Thread(
                target=self.main_event._monitor_end_time,
                kwargs={
                    "uptime_info": self.uptime_info,
                    "finish_event": self.finish_flag,
                    "stop_event": self.stop_flag,
                    "main_thread": self.main_task_thread
                }, daemon=True)

            # threadスタート
            self.end_time_thread.start()

        except Exception as e:
            print(f"_start_monitor_end_time_thread を処理中にエラーが発生: {e}")


    # ----------------------------------------------------------------------------------    # ラベルをアップデートする
    # ラベルをアップデートする

    def _update_label(self, comment: str):
        self.process_label.setText(comment)

    # ----------------------------------------------------------------------------------
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# GCテスト実施

if __name__ == "__main__":
    gss_info = GssInfo.RMT_CLUB.value
    gui_info = GuiInfo.RMT_CLUB.value


    def process_func(*args, **kwargs):
        if not hasattr(process_func, "instance"):
            process_func.instance = FlowRMTProcess()
        return process_func.instance.process(*args, **kwargs)


    app = QApplication(sys.argv)
    main_app = MainRMTClubApp(gui_info=gui_info, process_func=process_func)
    main_app.show()
    sys.exit(app.exec())
