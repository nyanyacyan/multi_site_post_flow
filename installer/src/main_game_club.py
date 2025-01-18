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
from method.flow_game_club_new_item import FlowGameClubProcess
from method.flow_game_club_update import FlowGameClubUpdate
from method.base.GUI.Qtimer_content import CountDownQTimer, CheckFlag


# const
from method.const_element import GssInfo, GuiInfo


# ----------------------------------------------------------------------------------
# **********************************************************************************


class MainGamaClubApp(QWidget):
    def __init__(self, gui_info: Dict, process_func: Callable, update_func: Callable):
        super().__init__()

        self.countdown_timer = None  # クラスの属性として初期化

        # メインタイトル
        self.setWindowTitle(gui_info['MAIN_WINDOW_TITLE'])

        # バックグラウンドカラー
        # self.setStyleSheet(f"background-color: {gui_info['BACKGROUND_COLOR']};")

        # logo
        self.path =BaseToPath()
        logo_path = self.path.getInputLogoFilePath(fileName=gui_info['LOGO_NAME'])
        QGuiApplication.setWindowIcon(QIcon(str(logo_path)))

        # メインレイアウトの設定
        self.layout = QVBoxLayout()

        # 各padding設定
        self.layout.setContentsMargins(15, 30, 15, 15)

        # 各レイアウト間の幅
        self.layout.setSpacing(30)

        self.setLayout(self.layout)


        # カウントダウン用ラベルを追加
        self.process_label = QLabel("待機中...")

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

            # メイン処理実施
            # self.main_event.main_task(update_bool=self.update_bool, stop_event=self.stop_flag, label=self.process_label, update_event=self.update_flag, update_func=self.update_func, process_func=self.process_func, user_info=self.user_info, gss_info=self.gss_info, interval_info=self.interval_info)

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
        self.cancel_event._cancel_event(label=self.process_label, timer=self.timer, stop_flag=self.stop_flag, update_flag=self.update_flag)


    # ----------------------------------------------------------------------------------
    # 日付が変わるまでの時間を算出して待機する

    def _monitor_date_change(self):
        self.thread_event._monitor_date_change(stop_event=self.stop_flag, label=self.process_label, update_event=self.update_flag, update_func=self.update_func, process_func=self.process_func, update_bool=self.update_bool, user_info=self.user_info, gss_info=self.gss_info, interval_info=self.interval_info)


    # ----------------------------------------------------------------------------------
    # 設定している時間になったら設定したtaskを実行

    def _monitor_end_time(self):
        self.thread_event._monitor_end_time(uptime_info=self.uptime_info, stop_event=self.stop_flag, label=self.process_label)


    # ----------------------------------------------------------------------------------
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# GCテスト実施

if __name__ == "__main__":
    gss_info = GssInfo.GAME_CLUB.value
    gui_info = GuiInfo.GAME_CLUB.value

    # スプシからすべてのWorksheet名を取得
    # gss_read = GetDataGSSAPI()
    # worksheet_info = gss_read._get_all_worksheet(gss_info=gss_info, sort_word_list=gss_info['workSheetName'])


    def process_func(*args, **kwargs):
        if not hasattr(process_func, "instance"):
            process_func.instance = FlowGameClubProcess()
        return process_func.instance.process(*args, **kwargs)


    # 更新処理をラップして遅延初期化
    def update_func(*args, **kwargs):
        if not hasattr(update_func, "instance"):
            update_func.instance = FlowGameClubUpdate()  # 初回呼び出し時にインスタンス化
        return update_func.instance.process(*args, **kwargs)


    app = QApplication(sys.argv)
    main_app = MainGamaClubApp(gui_info=gui_info, process_func=process_func, update_func=update_func)
    main_app.show()
    sys.exit(app.exec())
