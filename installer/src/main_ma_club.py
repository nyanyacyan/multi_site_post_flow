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
from method.base.GUI.set_radio_btn import RadioSelect
from method.base.GUI.set_action_btn import ActionBtn

from method.base.event.countdown_event import CountdownEvent
from method.base.event.update_event import UpdateEvent
from method.base.event.cancel_event import CancelEvent
from method.base.event.thread_event import ThreadEvent
from method.base.event.loop_process import LoopProcess

from method.base.time_manager import TimeManager
from method.base.path import BaseToPath
from method.flow_ma_club_new_item import FlowMAClubProcess
from method.flow_ma_club_update import FlowMAClubUpdate
from method.base.GUI.Qtimer_content import CountDownQTimer, CheckFlag
from method.base.event.update_label import UpdateLabel


# const
from method.const_element import GssInfo, GuiInfo


# ----------------------------------------------------------------------------------
# **********************************************************************************


class MainMAClubApp(QWidget):
    def __init__(self, gui_info: Dict, process_func: Callable, update_func: Callable):
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
        self.radio_btn_form = RadioSelect(gui_info=gui_info)
        self.action_btn_form = ActionBtn(label=self.process_label, gui_info=gui_info, process_func=self.entry_event, cancel_func=self.cancel_process)


        # レイアウトに追加
        self.layout.addWidget(self.user_info_form)
        self.layout.addWidget(self.gss_info_form)
        self.layout.addWidget(self.interval_form)
        self.layout.addWidget(self.uptime_form)
        self.layout.addWidget(self.radio_btn_form)
        self.layout.addWidget(self.action_btn_form)
        self.layout.addWidget(self.process_label)


        # フラグをセット（フラグを立てる場合には self.stop_event.set() を実施）
        self.stop_flag = threading.Event()
        self.update_flag = threading.Event()
        self.start_event_flag = threading.Event()

        # メインの処理を受け取る
        self.process_func = process_func
        self.update_func = update_func

        # ここでupdateの要否を確認→bool
        self.update_bool = True  # 初期値を設定

        # インスタンス
        self.time_manager = TimeManager()
        self.countdown_event = CountdownEvent()
        self.update_event = UpdateEvent()
        self.check_flag = CheckFlag()
        self.cancel_event = CancelEvent()
        self.thread_event = ThreadEvent()
        self.main_event = LoopProcess()
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
            self.interval_info = self.interval_form.get_interval_info()  # 処理の実施間隔の値
            self.update_bool = self.radio_btn_form.get_radio_info()  # 選択した値


            # 終了時間の監視taskをスタート
            self.end_time_thread = threading.Thread(target=self._monitor_end_time, daemon=True)

            # 終了時間の監視taskをスタート
            self.date_change_thread = threading.Thread(target=self._monitor_date_change, daemon=True)

            # 各スレッドスタート
            self.end_time_thread.start()
            self.date_change_thread.start()

            comment = "処理中..."
            self.update_label._update_label(label=self.process_label, comment=comment)

            # メイン処理を別スレッドで実行
            self.main_task_thread = threading.Thread(
                target=self.main_event.main_task,
                kwargs={
                    "update_bool": self.update_bool,
                    "stop_event": self.stop_flag,
                    "label": self.process_label,
                    "update_event": self.update_flag,
                    "update_func": self.update_func,
                    "process_func": self.process_func,
                    "user_info": self.user_info,
                    "gss_info": self.gss_info,
                    "interval_info": self.interval_info,
                },
                daemon=True
            )
            self.main_task_thread.start()

        except Exception as e:
            print(f"処理中にエラーが発生: {e}")


    # ----------------------------------------------------------------------------------
    # キャンセル処理

    def cancel_process(self):
        self.cancel_event._cancel_event(label=self.process_label)


    # ----------------------------------------------------------------------------------
    # 日付が変わるまでの時間を算出して待機する

    def _monitor_date_change(self):
        self.thread_event._monitor_date_change(stop_event=self.stop_flag, label=self.process_label, update_event=self.update_flag, update_func=self.update_func, process_func=self.process_func, update_bool=self.update_bool, user_info=self.user_info, gss_info=self.gss_info, interval_info=self.interval_info)


    # ----------------------------------------------------------------------------------
    # 設定している時間になったら設定したtaskを実行

    def _monitor_end_time(self):
        self.thread_event._monitor_end_time(uptime_info=self.uptime_info, stop_event=self.stop_flag)


    # ----------------------------------------------------------------------------------
    # ラベルをアップデートする

    def _update_label(self, comment: str):
        self.process_label.setText(comment)

    # ----------------------------------------------------------------------------------
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# GCテスト実施

if __name__ == "__main__":
    gss_info = GssInfo.MA_CLUB.value
    gui_info = GuiInfo.MA_CLUB.value


    def process_func(*args, **kwargs):
        if not hasattr(process_func, "instance"):
            process_func.instance = FlowMAClubProcess()
        return process_func.instance.process(*args, **kwargs)


    # 更新処理をラップして遅延初期化
    def update_func(*args, **kwargs):
        if not hasattr(update_func, "instance"):
            update_func.instance = FlowMAClubUpdate()  # 初回呼び出し時にインスタンス化
        return update_func.instance.process(*args, **kwargs)


    app = QApplication(sys.argv)
    main_app = MainMAClubApp(gui_info=gui_info, process_func=process_func, update_func=update_func)
    main_app.show()
    sys.exit(app.exec())
