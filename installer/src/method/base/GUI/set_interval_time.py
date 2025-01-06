# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# export PYTHONPATH="/Users/nyanyacyan/Desktop/project_file/domain_search/installer/src"


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
from typing import Dict
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLineEdit, QLabel, QGroupBox
from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator

# 自作モジュール



# ----------------------------------------------------------------------------------
# **********************************************************************************


class IntervalTimeForm(QGroupBox):
    def __init__(self, gui_info: Dict):
        super().__init__(gui_info['INTERVAL_TIME_GROUP_TITLE'])

        # タイトルのスタイルを設定
        self.setStyleSheet("""
            QGroupBox {
                font-size: 12px;  /* 文字の大きさ */
                font-weight: bold;  /* 太字 */
                text-decoration: underline;  /* 下線 */
            }
        """)

        # レイアウトを設定
        self.setLayout(self._input_interval_time_group(gui_info=gui_info))


    ####################################################################################
    # 値を取得

    def get_interval_info(self):
        try:
            min_value = self.interval_min_text.text().strip()
            max_value = self.interval_max_text.text().strip()

            if not min_value:
                self._set_error_msg("下限が入力されてません")
                raise ValueError("下限が入力されてません")

            if not max_value:
                self._set_error_msg("上限が入力されてません")
                raise ValueError("上限が入力されてません")

            if int(min_value) > int(max_value):
                self._set_error_msg("最小時間は最大時間以下である必要があります")
                raise ValueError("最小時間は最大時間以下である必要があります")

            # エラーがない場合はメッセージをクリア
            self._set_error_msg("")

            return {
                "min": min_value,
                "max": max_value,
            }

        except ValueError as e:
            self.error_label.setText(str(e))
            raise


    ####################################################################################

    ####################################################################################
    # 実施間隔を入力

    def _input_interval_time_group(self, gui_info: Dict):
        interval_time_group_layout = QVBoxLayout()

        # interval_minを入力
        self.interval_min_text = self._create_input_int_field(gui_info['INPUT_EXAMPLE_INTERVAL_MIN'])
        input_between_label = QLabel(gui_info['INPUT_BETWEEN_LABEL'])

        self.interval_max_text = self._create_input_int_field(gui_info['INPUT_EXAMPLE_INTERVAL_MAX'])
        input_last_label = QLabel(gui_info['INPUT_LAST_LABEL'])

        # 横に並びに配置
        interval_time_layout = QHBoxLayout()  # 横レイアウト
        interval_time_layout.addWidget(self.interval_min_text)
        interval_time_layout.addWidget(input_between_label)
        interval_time_layout.addWidget(self.interval_max_text)
        interval_time_layout.addWidget(input_last_label)

        # グループレイアウトに追加したいレイアウトいれる
        interval_time_group_layout.addLayout(interval_time_layout)

        # errorラベルを追加
        self.error_label = self._error_label()
        interval_time_group_layout.addWidget(self.error_label)

        return interval_time_group_layout


    ####################################################################################
    # ----------------------------------------------------------------------------------
    # ID入力欄→passwordを渡せば非表示

    def _create_input_int_field(self, input_example: str, fixed_width: int=100):
        input_field = QLineEdit()
        input_field.setPlaceholderText(input_example)  # input_exampleは入力例

        # 半角のみを許可する正規表現を設定
        validator = QRegularExpressionValidator(QRegularExpression("[0-9]+"))
        input_field.setValidator(validator)

        # 入力欄の幅を調整
        input_field.setFixedWidth(fixed_width)

        return input_field


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
