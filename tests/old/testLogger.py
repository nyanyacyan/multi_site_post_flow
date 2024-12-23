# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# 2024/9/19 更新
# テストOK

# Pathの設定 export PYTHONPATH="${PYTHONPATH}:/Users/nyanyacyan/Desktop/project_file/SNS_auto_upper/installer/src/method/base"

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import io
import logging

# 自作モジュール
from installer.src.method.base.utils import Logger

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************
# 単体テスト 写真を取得


# 成功したときのテスト
# @patch('method')→この中にいれるmethodがモック化される→モック化されたものは引数に渡す必要がある


class TestLogger:
    def testContextSuccess(self):
        # ロガーのインスタンス化
        instance = Logger(__name__)
        logger = instance.getLogger()

        # ログ出力をキャプチャするための設定
        captured_output = io.StringIO()
        handler = logging.StreamHandler(captured_output)
        logger.addHandler(handler)

        # ログメッセージの出力
        logger.debug("abc")

        # キャプチャした出力の取得
        log_output = captured_output.getvalue()

        # 結果の検証
        assert "abc" in log_output

        # クリーンアップ
        logger.removeHandler(handler)


# ----------------------------------------------------------------------------------
