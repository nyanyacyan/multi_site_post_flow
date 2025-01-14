# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# export PYTHONPATH="/Users/nyanyacyan/Desktop/project_file/multi_site_post_flow/installer/src"

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import threading, time, asyncio, sys
from datetime import datetime, timedelta
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

from method.base.event.update_event import UpdateEvent
from method.base.event.cancel_event import CancelEvent

from method.base.time_manager import TimeManager
from method.base.path import BaseToPath
from method.flow_game_club_new_item import FlowGameClubNewItem
from method.flow_gc_update import FlowGameClubUpdate
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
        self.stop_event = threading.Event()
        self.update_complete_event = threading.Event()
        self.start_event_flag = threading.Event()

        # メインの処理を受け取る
        self.process_func = process_func
        self.update_func = update_func

        # ここでupdateの要否を確認→bool
        self.update_bool = True  # 初期値を設定

        # インスタンス
        self.time_manager = TimeManager()
        self.update_event = UpdateEvent()
        self.check_flag = CheckFlag()
        self.cancel_event = CancelEvent()

        # タイマーの設定
        self.uptime_info = {}  # 初期化
        self.timer = CountDownQTimer(label=self.process_label, uptime_info=self.uptime_info, start_event_flag=self.start_event_flag)


    ####################################################################################


    def entry_event(self):
        try:
            # 開始時間と終了時間を取得
            self.uptime_info = self.uptime_form.get_uptime_info()
            print(self.uptime_info)

            self.timer.update_uptime_info(self.uptime_info)  # 最新の数値に実行するMethod側の数値を更新する

            print("Entry Event 開始")
            self.timer.countdown_event()  # SingleShotTestのタイマーを起動
            print("Entry Event 完了")

            # QTimerでフラグを監視
            self.check_flag._check_flag(flag=self.start_event_flag, event_func=self.start_event)


        except Exception as e:
            print(f"エラーです{e}")


    # ----------------------------------------------------------------------------------
    # start_event

    def start_event(self):
        try:
            user_info = self.user_info_form.get_user_info()
            interval_info = self.interval_form.get_interval_info()
            uptime_info = self.uptime_form.get_uptime_info()

            # STARTボタンを押下したときのradio_btnを取得
            self.update_bool = self.radio_btn_form.get_radio_info()

            # 更新処理がある場合には実施
            if self.update_bool:
                self.update_event._update_task(stop_event=self.stop_event, update_complete_event=self.update_complete_event, update_func=self.update_func, label=self.process_label, user_info=user_info)

            # 終了時間の監視taskをスタート
            self.end_time_thread = threading.Thread(target=self._monitor_end_time, args=(uptime_info,), daemon=True)

            # 終了時間の監視taskをスタート
            self.date_change_thread = threading.Thread(target=self._monitor_date_change, args=(user_info,), daemon=True)

            # 各スレッドスタート
            self.end_time_thread.start()
            self.date_change_thread.start()

            # スレッドの状態確認
            if self.end_time_thread.is_alive():
                print("終了時間の監視タスクが実行中です")
            else:
                print("終了時間の監視タスクは終了しています")

            if self.date_change_thread.is_alive():
                print("日付変更の監視タスクが実行中です")
            else:
                print("日付変更の監視タスクは終了しています")

            # メイン処理実施
            self.loop_process(user_info=user_info, interval_info=interval_info, uptime_info=uptime_info)

        except Exception as e:
            print(f"処理中にエラーが発生: {e}")


    # ----------------------------------------------------------------------------------
    # キャンセル処理

    def cancel_process(self):
        self.cancel_event._cancel_event(label=self.process_label, timer=self.timer, stop_flag=self.stop_event, update_flag=self.update_complete_event)


    # ----------------------------------------------------------------------------------
    # 日付が変わるまでの時間を算出して待機する

    def _monitor_date_change(self, user_info: Dict):
        # ストップフラグがis_setされるまでループ処理
        while not self.stop_event.is_set():
            now = datetime.now()
            next_day = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)

            total_sleep_time = (next_day - now).total_seconds()

            time.sleep(total_sleep_time)

            if self.update_bool:
                self._update_task(user_info=user_info)


    # ----------------------------------------------------------------------------------
    # 設定している時間になったら設定したtaskを実行

    def _monitor_end_time(self, uptime_info: Dict[str, timedelta]):
        try:
            self.logger.debug(f"現在のスレッドID: {threading.get_ident()}")
            end_diff = uptime_info['end_diff']

            if end_diff > 0:
                self.logger.debug(f"終了時間まで {end_diff} 秒待機します (threading.Timer を使用)")
                # 終了時間まで待機
                threading.Timer(end_diff, self._end_time_task).start()

        except Exception as e:
            self.status_label.update_status(msg=f"終了時間の設定などによるエラー: {e}", color="red")


    # ----------------------------------------------------------------------------------
    # 終了時に行うtask

    def _end_time_task(self):
            # 処理を停止
            self.stop_event.set()
            self.status_label.update_status(msg="終了時間に達したため処理を停止しました。", color="red")


    # ----------------------------------------------------------------------------------
    # 出品処理

    def loop_process(self, user_info: Dict, interval_info: Dict):
        # ストップフラグがis_setされるまでループ処理
        count = 0
        while not self.stop_event.is_set():

            if self.stop_event.is_set():
                self.status_label.update_status(msg="出品処理処理を停止...", color="blue")
                print("ストップイベントフラグを確認。出品処理を停止")
                break

            count += 1
            self.status_label.update_status(msg=f"実行処理中({count}回目)...", color="blue")
            print(f"実行処理中({count}回目)")

            # 処理を実施
            self.process_func(id_text=user_info['id'], pass_text=user_info['pass'], worksheet_name=user_info['worksheet'])

            # 設定した待機をランダムで実行
            self.time_manager._random_sleep(random_info=interval_info)


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
            process_func.instance = FlowGameClubNewItem()
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
