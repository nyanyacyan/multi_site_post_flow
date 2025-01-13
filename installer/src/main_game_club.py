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
from PySide6.QtCore import QTimer


# 自作モジュール
from method.base.GUI.set_user_info import UserInfoForm
from method.base.GUI.set_gss_info import GSSInfoForm
from method.base.GUI.set_interval_time import IntervalTimeForm
from method.base.GUI.set_uptime import SetUptime
from method.base.GUI.set_radio_btn import RadioSelect
from method.base.GUI.set_action_btn import ActionBtn
from method.base.GUI.set_status_display import StatusManager

from method.base.event.update_event import UpdateEvent

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

        # ステータスラベルを定義
        self.status_label = StatusManager()

        # 各GUIパーツを追加
        self.user_info_form = UserInfoForm(gui_info=gui_info)
        self.gss_info_form = GSSInfoForm(gui_info=gui_info)
        self.interval_form = IntervalTimeForm(gui_info=gui_info)
        self.uptime_form = SetUptime(gui_info=gui_info)
        self.radio_btn_form = RadioSelect(gui_info=gui_info)
        self.action_btn_form = ActionBtn(gui_info=gui_info, status_label=self.status_label, process_func=self.entry_event, cancel_func=self.cancel_event)

        # カウントダウン用ラベルを追加
        self.process_label = QLabel("カウントダウン待機中...")
        # self.process_label_two = QLabel('処理ステータス')


        # レイアウトに追加
        self.layout.addWidget(self.user_info_form)
        self.layout.addWidget(self.gss_info_form)
        self.layout.addWidget(self.interval_form)
        self.layout.addWidget(self.uptime_form)
        self.layout.addWidget(self.radio_btn_form)
        self.layout.addWidget(self.action_btn_form)
        self.layout.addWidget(self.status_label)
        self.layout.addWidget(self.process_label)
        # self.layout.addWidget(self.process_label_two)


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

        # タイマーの設定
        self.uptime_info = {}  # 初期化
        self.timer = CountDownQTimer(label=self.process_label, uptime_info=self.uptime_info, start_event_flag=self.start_event_flag)


    ####################################################################################


    def entry_event(self):
        try:
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


    def _check_flag_and_start(self):
        """フラグを監視し、立ったらstart_eventを実行"""
        if self.start_event_flag.is_set():
            print("[DEBUG] フラグが立ちました！start_eventを開始します")
            self.check_timer.stop()  # タイマーを停止
            self.start_event()
        else:
            print("[DEBUG] フラグはまだ立っていません")


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
                # if self.process_label_two is None:
                #     print(f"[DEBUG] ラベルが初期化されていません {self.process_label_two}")
                # print(f"ラベルの中身 {self.process_label_two}")

                # print(f"[DEBUG] 呼び出し元のラベルID: {id(self.process_label_two)}")

                self.update_event._update_task(stop_event=self.stop_event, update_complete_event=self.update_complete_event, update_func=self.update_func, label=self.process_label, user_info=user_info)



            # 終了時間の監視taskをスタート
            threading.Thread(target=self._monitor_end_time, args=(uptime_info,), daemon=True).start()

            # 終了時間の監視taskをスタート
            threading.Thread(target=self._monitor_date_change, args=(user_info,), daemon=True).start()

            # 更新作業が完了するまで待機
            self.update_complete_event.wait()

            # メイン処理実施
            self.loop_process(user_info=user_info, interval_info=interval_info, uptime_info=uptime_info)

        except Exception as e:
            print(f"処理中にエラーが発生: {e}")


    # ----------------------------------------------------------------------------------


    # ----------------------------------------------------------------------------------
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
            end_diff = uptime_info['end_diff']

            if end_diff > 0:
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


    # def _start_wait_time(self):
    #     # 開始時間まで待機
    #     uptime_info = self.uptime_form.get_uptime_info()
    #     start_diff = uptime_info['start_diff']
    #     self.wait_seconds = start_diff.total_seconds()
    #     print(f"self.wait_seconds: {self.wait_seconds}")

    #     # タイマーの設定
    #     self.countdown_timer.setInterval(1000)  # 1秒ごとに発火
    #     self.countdown_timer.timeout.connect(self._countdown_tick)  # カウントダウン処理に接続

    #     # タイマーを開始
    #     self.countdown_timer.start()


    # # ----------------------------------------------------------------------------------

    # def _start_timer(self, msg: str, color: str='black'):
    #     # タイマーの設定
    #     if hasattr(self, 'timer') and self.timer.isActive():
    #         print("Stopping previous timer")  # デバッグ
    #         self.timer.stop()

    #     self.status_timer.timeout.disconnect()
    #     self.status_timer.setInterval(1000)  # 1秒ごとに発火

    #     self.status_timer.timeout.connect(partial(self._status_update, msg, color))

    #     print("Starting new timer with message:", msg)  # デバッグ
    #     # タイマーを開始
    #     self.status_timer.start()


    # ----------------------------------------------------------------------------------


    def _status_update(self, msg: str, color: str='black'):
        current_text = self.status_label._get_status_text()

        if current_text == msg:
            self._stop_timer()
            print("タイマーストップ")
            return

        self.status_label.update_status(msg=msg, color=color)


    def _test_update(self):
        print("Timer triggered!")

    def _stop_timer(self):
        if hasattr(self, 'timer') and self.timer.isActive():
            self.status_timer.stop()


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
            self.status_label.update_status("タイマーストップ")
            self.countdown_timer.stop()  # タイマー停止

            # タイマーが停止したかどうかを確認
            if not self.countdown_timer.isActive():
                print("タイマーが正常に停止しました")
            else:
                print("タイマーがまだ動作中です！")


        # タイマー終了後の次の処理を非同期で実行
            self._start_timer(msg="実行を開始します1！")


            self._start_timer(msg="実行を開始します2！")

    async def _after_countdown(self):
        await asyncio.sleep(0.5)
        self.status_label.update_status("実行を開始します1！")


    async def _after_start_event(self):
        # await asyncio.sleep(0.5)
        # self.status_label.update_status("実行を開始します2！")
        self.start_event()  # メインタスクを開始

    # ----------------------------------------------------------------------------------
    # 更新処理

    def _update_task(self, user_info: Dict):
        # 出品処理を停止
        self.stop_event.set()

        # 更新処理ストップフラグをクリア→更新処理が実施できるようにする
        self.update_complete_event.clear()
        print("更新処理のクリアを実施")

        # ステータス変更
        self.status_label.update_status(msg="")
        self.status_label.update_status(msg="更新処理中...")
        print("更新処理の開始")


        # 更新処理を実施
        self.update_func(id_text=user_info['id'], pass_text=user_info['pass'])

        # 更新作業完了フラグを立てる
        self.update_complete_event.set()
        print("更新処理が完了したのでフラグ立て")

        self.status_label.update_status(msg="更新処理が完了しました。", color="blue")


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
