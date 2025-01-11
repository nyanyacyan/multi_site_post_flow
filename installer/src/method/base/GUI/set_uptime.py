# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# export PYTHONPATH="/Users/nyanyacyan/Desktop/project_file/domain_search/installer/src"


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
from datetime import datetime, timedelta
from typing import Dict
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QDateTimeEdit, QLabel, QGroupBox
from PySide6.QtCore import QDateTime

# 自作モジュール



# ----------------------------------------------------------------------------------
# **********************************************************************************


class SetUptime(QGroupBox):
    def __init__(self, gui_info: Dict):
        super().__init__(gui_info['UPTIME_TIME_GROUP_TITLE'])

        # タイトルのスタイルを設定
        self.setStyleSheet("""
            QGroupBox {
                font-size: 12px;  /* 文字の大きさ */
                font-weight: bold;  /* 太字 */
                text-decoration: underline;  /* 下線 */
            }
        """)

        # レイアウトを設定
        self.setLayout(self._create_uptime_input_group(gui_info=gui_info))


    ####################################################################################
    # 値を取得

    def get_uptime_info(self) -> Dict[str, timedelta]:
        try:
            uptime_start_time = self.uptime_start_time.dateTime().toPython()
            uptime_end_time = self.uptime_end_time.dateTime().toPython()

            now = datetime.now()
            start_diff = uptime_start_time - now
            end_diff = uptime_end_time - now

            start_diff_int = int(start_diff.total_seconds())
            end_diff_int = int(end_diff.total_seconds())

            if not uptime_start_time:
                self._set_error_msg("開始日時の設定がされてません")
                raise ValueError("開始日時の設定がされてません")

            if not uptime_end_time:
                self._set_error_msg("終了日時の設定がされてません")
                raise ValueError("終了日時の設定がされてません")

            if uptime_start_time >= uptime_end_time:
                self._set_error_msg("開始日時は終了日時より前に設定する必要があります")
                raise ValueError("開始日時は終了日時より前に設定する必要があります")

            # エラーがない場合はメッセージをクリア
            self._set_error_msg("")

            return {
                "start_diff": start_diff_int,
                "end_diff": end_diff_int,
            }

        except ValueError as e:
            self.error_label.setText(str(e))
            raise


    ####################################################################################
    # 開始と終了の時刻入力

    def _create_uptime_input_group(self, gui_info: Dict):
        uptime_layout = QVBoxLayout()

        # start_uptimeを入力
        input_start_uptime_label = QLabel(gui_info['INPUT_START_UPTIME_TITLE'])
        self.uptime_start_time = self._set_datetime()

        # start_uptimeのレイアウト作成
        start_uptime_layout = QHBoxLayout()  # 横レイアウト
        start_uptime_layout.addWidget(input_start_uptime_label)
        start_uptime_layout.addWidget(self.uptime_start_time)

        # start_uptimeグループに追加
        uptime_layout.addLayout(start_uptime_layout)

        # end_uptimeを入力
        input_last_label = QLabel(gui_info['INPUT_END_UPTIME_TITLE'])
        self.uptime_end_time = self._set_datetime()

        # end_uptimeのレイアウト作成
        end_uptime_layout = QHBoxLayout()  # 横レイアウト
        end_uptime_layout.addWidget(input_last_label)
        end_uptime_layout.addWidget(self.uptime_end_time)

        # end_uptimeをグループに追加
        uptime_layout.addLayout(end_uptime_layout)

        # errorラベルを追加
        self.error_label = self._error_label()
        uptime_layout.addWidget(self.error_label)

        return uptime_layout


    ####################################################################################


    # カレンダーから日時を選択
    # 実行されて初めて入力内容が確認できる→デバッグはこの関数が実行された後に
    # 値は見えるやすように処理する必要がある→ .dateTime().toString("yyyy-MM-dd HH:mm:ss")

    def _set_datetime(self, fixed_width: int=250):
        edit_datetime = QDateTimeEdit(self)
        edit_datetime.setDateTime(QDateTime.currentDateTime())  # 現時刻をデフォルトにする
        edit_datetime.setCalendarPopup(True)  # カレンダー表示を有効化

        # 入力欄の幅を調整
        edit_datetime.setFixedWidth(fixed_width)

        return edit_datetime


    # ----------------------------------------------------------------------------------
    # エラーラベル（通常時は非表示）

    def _error_label(self):
        error_label = QLabel("")
        error_label.setStyleSheet("color: red;")
        error_label.hide()
        return error_label


    # ----------------------------------------------------------------------------------
    # メッセージが合ったときに表示させる

    def _set_error_msg(self, msg: str):
        # エラーあり
        if msg:
            self.error_label.setText(msg)
            self.error_label.show()

        # エラーなし
        else:
            self.error_label.clear()
            self.error_label.hide()


    # ----------------------------------------------------------------------------------
