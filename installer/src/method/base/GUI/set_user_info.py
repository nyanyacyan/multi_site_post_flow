# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# export PYTHONPATH="/Users/nyanyacyan/Desktop/project_file/domain_search/installer/src"


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
from typing import Dict, List
from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QLabel,
    QGroupBox,
    QComboBox,
)
from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator

# 自作モジュール


# ----------------------------------------------------------------------------------
# **********************************************************************************
# ユーザー情報のグループを設定


class UserInfoForm(QGroupBox):
    def __init__(self, gui_info: Dict):
        super().__init__(gui_info["USER_INPUT_TITLE"])  # タイトルを設定

        # タイトルのスタイルを設定
        self.setStyleSheet(
            """
            QGroupBox {
                font-size: 12px;  /* 文字の大きさ */
                font-weight: bold;  /* 太字 */
                text-decoration: underline;  /* 下線 */
            }
        """
        )

        # レイアウトを設定
        self.setLayout(
            self._create_user_info_layout(
                gui_info=gui_info
            )
        )

    ####################################################################################
    # 値を取得

    def get_user_info(self):
        try:
            id_text = self.id_input.text().strip()
            pass_text = self.pass_input.text().strip()
            # select_dropdown_text = self.dropdown_input.currentText()

            if not id_text:
                self._set_error_msg("IDが入力されていません")
                raise ValueError("IDが入力されていません")

            if not pass_text:
                self._set_error_msg("PASSが入力されていません")
                raise ValueError("PASSが入力されていません")

            # if select_dropdown_text == "選択してください":
            #     self._set_error_msg("Worksheetが選択されてません")
            #     raise ValueError("Worksheetが選択されていません")

            # エラーがない場合はメッセージをクリア
            self._set_error_msg("")

            return {"id": id_text, "pass": pass_text}

        except ValueError as e:
            self.error_label.setText(str(e))
            raise

    ####################################################################################

    ####################################################################################
    # ユーザー入力欄のグループ

    def _create_user_info_layout(self, gui_info: Dict):
        group_layout = QVBoxLayout()

        group_layout.setContentsMargins(15, 15, 15, 15)
        group_layout.setSpacing(15)

        # ID入力
        id_label = QLabel(gui_info["ID_LABEL"])
        self.id_input = self._create_input_field(
            gui_info["INPUT_EXAMPLE_ID"], fixed_width=250
        )

        # idのレイアウト作成
        id_layout = QHBoxLayout()  # 横レイアウト
        id_layout.addWidget(id_label)
        id_layout.addWidget(self.id_input)

        # グループにidレイアウトを追加
        group_layout.addLayout(id_layout)

        # Pass入力
        pass_label = QLabel(gui_info["PASS_LABEL"])
        self.pass_input = self._create_input_field(
            gui_info["INPUT_EXAMPLE_PASS"], fixed_width=250
        )

        # Passのレイアウト作成
        pass_layout = QHBoxLayout()  # 横レイアウト
        pass_layout.addWidget(pass_label)
        pass_layout.addWidget(self.pass_input)

        # グループにPassレイアウトを追加
        group_layout.addLayout(pass_layout)

        # errorラベルを追加
        self.error_label = self._error_label()
        group_layout.addWidget(self.error_label)

        return group_layout

    ####################################################################################
    # ----------------------------------------------------------------------------------
    # ID入力欄→passwordを渡せば非表示

    def _create_input_field(
        self, input_example: str, is_password: bool = False, fixed_width: int = 200
    ):
        input_field = QLineEdit()
        input_field.setPlaceholderText(input_example)  # input_exampleは入力例

        # 半角のみを許可する正規表現を設定
        validator = QRegularExpressionValidator(QRegularExpression(".+"))
        input_field.setValidator(validator)

        if is_password:
            input_field.setEchoMode(QLineEdit.Password)

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
