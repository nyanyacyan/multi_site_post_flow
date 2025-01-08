# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# export PYTHONPATH="/Users/nyanyacyan/Desktop/project_file/multi_site_post_flow/installer/src"

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import threading, time, _asyncio, sys
from datetime import datetime, timedelta
from typing import Dict, Callable, List
from PySide6.QtWidgets import QWidget, QVBoxLayout, QApplication
from PySide6.QtCore import QTimer
from PySide6.QtGui import QIcon

# 自作モジュール
from method.base.GUI.set_user_info import UserInfoForm
from method.base.GUI.set_gss_info import GSSInfoForm
from method.base.GUI.set_interval_time import IntervalTimeForm
from method.base.GUI.set_uptime import SetUptime
from method.base.GUI.set_radio_btn import RadioSelect
from method.base.GUI.set_action_btn import ActionBtn
from method.base.GUI.set_status_display import StatusManager
from method.base.time_manager import TimeManager
from method.base.path import BaseToPath
from method.base.spreadsheetRead import GetDataGSSAPI
from method.flow_game_club_new_item import FlowGameClubNewItem
from method.flow_MA_club_new_item import FlowMAClubNewItem
from method.flow_gc_update import FlowGameClubUpdate
from method.flow_ma_club_update import FlowMAClubUpdate
from PySide6.QtGui import QGuiApplication

# const
from method.const_element import GssInfo, GuiInfo


# ----------------------------------------------------------------------------------
# **********************************************************************************


class MainMAClubApp(QWidget):
    def __init__(self, gui_info: Dict, process_func: Callable, update_func: Callable):
        super().__init__()
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

        # ステータスラベルを定義
        self.status_label = StatusManager()

        # 各GUIパーツを追加
        self.user_info_form = UserInfoForm(gui_info=gui_info)
        self.gss_info_form = GSSInfoForm(gui_info=gui_info)
        self.interval_form = IntervalTimeForm(gui_info=gui_info)
        self.uptime_form = SetUptime(gui_info=gui_info)
        self.radio_btn_form = RadioSelect(gui_info=gui_info)
        self.action_btn_form = ActionBtn(gui_info=gui_info, status_label=self.status_label, process_func=self._start_wait_time, cancel_func=self.cancel_event)


        # レイアウトに追加
        self.layout.addWidget(self.user_info_form)
        self.layout.addWidget(self.gss_info_form)
        self.layout.addWidget(self.interval_form)
        self.layout.addWidget(self.uptime_form)
        self.layout.addWidget(self.radio_btn_form)
        self.layout.addWidget(self.action_btn_form)
        self.layout.addWidget(self.status_label)


        # フラグをセット（フラグを立てる場合には self.stop_event.set() を実施）
        self.stop_event = threading.Event()
        self.update_complete_event = threading.Event()

        # メインの処理を受け取る
        self.process_func = process_func
        self.update_func = update_func

        # ここでupdateの要否を確認→bool
        self.update_bool = True  # 初期値を設定

        # インスタンス
        self.time_manager = TimeManager()


    ####################################################################################
    # start_event

    def start_event(self):
        try:
            user_info = self.user_info_form.get_user_info()
            interval_info = self.interval_form.get_interval_info()
            uptime_info = self.uptime_form.get_uptime_info()

            # スタートするまで待機
            # self._start_wait_time(uptime_info=uptime_info)

            # STARTボタンを押下したときのradio_btnを取得
            self.update_bool = self.radio_btn_form.get_radio_info()

            # 更新処理がある場合には実施
            if self.update_bool:
                self._update_task(user_info=user_info)

            # 終了時間の監視taskをスタート
            threading.Thread(target=self._monitor_end_time, args=(uptime_info,), daemon=True).start()

            # 終了時間の監視taskをスタート
            threading.Thread(target=self._monitor_date_change, args=(user_info,), daemon=True).start()

            # メイン処理実施
            self.loop_process(user_info=user_info, interval_info=interval_info, uptime_info=uptime_info)

        except Exception as e:
            self.status_label.update_status(msg=f"エラー: {e}", color="red")
            print(f"処理中にエラーが発生: {e}")


    ####################################################################################

    ####################################################################################
    # キャンセル処理

    def cancel_event(self):
        self.status_label.update_status(msg="出品処理を停止中です。", color="red")

        # タイマーが設定されてればストップ
        if self.timer:
            self.timer.stop()

        # 出品処理を停止
        self.stop_event.set()

        # 更新完了されたフラグもリセット
        self.update_complete_event.clear()

        self.status_label.update_status(msg="待機中...", color="red")


    ####################################################################################
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
            end_diff = uptime_info['end_diff']

            if end_diff.total_seconds() > 0:
                # 終了時間まで待機
                threading.Timer(end_diff.total_seconds(), self._end_time_task).start()

        except Exception as e:
            self.status_label.update_status(msg=f"終了時間の設定などによるエラー: {e}", color="red")


    # ----------------------------------------------------------------------------------
    # 終了時に行うtask

    def _end_time_task(self):
            # 処理を停止
            self.stop_event.set()
            self.status_label.update_status(msg="終了時間に達したため処理を停止しました。", color="red")


    # ----------------------------------------------------------------------------------


    def _start_wait_time(self):
        # 開始時間まで待機
        uptime_info = self.uptime_form.get_uptime_info()
        start_diff = uptime_info['start_diff']
        self.wait_seconds = start_diff.total_seconds()

        # タイマーの設定
        self.timer = QTimer()
        self.timer.setInterval(1000)  # 1秒ごとに発火
        self.timer.timeout.connect(self._countdown_tick)  # カウントダウン処理に接続

        # タイマーを開始
        self.timer.start()


    # ----------------------------------------------------------------------------------
    # QTimerによって1秒毎に実施されるアクションを定義

    def _countdown_tick(self):
        if self.wait_seconds > 0:
            # 残り時間を更新
            minutes, seconds = divmod(self.wait_seconds, 60)
            if minutes > 0:
                msg = f"実行開始まで {int(minutes)} 分 {int(seconds)} 秒"
            else:
                msg = f"実行開始まで {int(seconds)} 秒"

            self.status_label.update_status(msg)
            self.wait_seconds -= 1
        else:
            # カウントダウン終了時の処理
            self.timer.stop()  # タイマー停止
            self.status_label.update_status("実行を開始します！")
            self.start_event()  # メインタスクを開始


    # ----------------------------------------------------------------------------------
    # 更新処理

    def _update_task(self, user_info: Dict):
        # 出品処理を停止
        self.stop_event.set()

        # 更新処理ストップフラグをクリア→更新処理が実施できるようにする
        self.update_complete_event.clear()

        # ステータス変更
        self.status_label.update_status(msg="更新処理中...", color="black")

        # 更新処理を実施
        self.update_func(id_text=user_info['id'], pass_text=user_info['pass'])

        # 更新作業完了フラグを立てる
        self.update_complete_event.set()

        self.status_label.update_status(msg="更新処理が完了しました。", color="blue")


    # ----------------------------------------------------------------------------------
    # 出品処理

    def loop_process(self, user_info: Dict, interval_info: Dict, uptime_info: Dict[str, timedelta]):
        # ストップフラグがis_setされるまでループ処理
        while not self.stop_event.is_set():
            # 更新作業が完了するまで待機
            self.update_complete_event.wait()

            if self.stop_event.is_set():
                break

            self.status_label.update_status(msg="実行処理中...", color="blue")

            # 処理を実施
            self.process_func(id_text=user_info['id'], pass_text=user_info['pass'], worksheet_name=user_info['worksheet'])

            # 設定した待機をランダムで実行
            self.time_manager._random_sleep(random_info=interval_info)


    # ----------------------------------------------------------------------------------
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# GCテスト実施

if __name__ == "__main__":
    gss_info = GssInfo.MA_CLUB.value
    gui_info = GuiInfo.MA_CLUB.value

    # スプシからすべてのWorksheet名を取得
    # gss_read = GetDataGSSAPI()
    # worksheet_info = gss_read._get_all_worksheet(gss_info=gss_info, sort_word_list=gss_info['workSheetName'])


    def process_func(*args, **kwargs):
        if not hasattr(process_func, "instance"):
            process_func.instance = FlowMAClubNewItem()
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
