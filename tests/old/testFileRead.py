# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# 2024/9/18 更新
# テストOK

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import pytest
from unittest.mock import patch, mock_open

# 自作モジュール
from installer.src.method.base.fileRead import ResultFileRead


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************
# pytestを実行する


class TestFileRead:

    # ----------------------------------------------------------------------------------

    def testSuccess(self):
        fileName = "dummyName"

        instance = ResultFileRead()

        with patch("builtins.open", mock_open()) as mockedFile:

            instance.readTextToResult(fileName=fileName)

            mockedFile().read.assert_called_once_with()

    # ----------------------------------------------------------------------------------

    def testError(self):
        fileName = "dummyName"

        instance = ResultFileRead()

        with patch("builtins.open", mock_open()) as mockedFile:

            mockedFile.side_effect = FileNotFoundError

            with pytest.raises(FileNotFoundError):

                instance.readTextResult(fileName=fileName)

                mockedFile().write.assert_called_once_with()


# ----------------------------------------------------------------------------------
