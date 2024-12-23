# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# 2024/9/13 更新 テストOK

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import pytest
from unittest.mock import patch, mock_open

# 自作モジュール
from installer.src.method.base.fileWrite import FileWrite


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************
# pytestを実行する


class TestFileWrite:

    # ----------------------------------------------------------------------------------

    def testSuccess(self):
        fileName = "dummyName"
        data = "TestData"

        instance = FileWrite()

        with patch("builtins.open", mock_open()) as mockedFile:

            instance.writeToText(data=data, fileName=fileName)

            mockedFile().write.assert_called_once_with(data)

    # ----------------------------------------------------------------------------------

    def testError(self):
        fileName = "dummyName"
        data = "TestData"

        instance = FileWrite()

        with patch("builtins.open", mock_open()) as mockedFile:

            mockedFile.side_effect = FileNotFoundError

            with pytest.raises(FileNotFoundError):

                instance.writeToText(data=data, fileName=fileName)

                mockedFile().write.assert_called_once_with(data)


# ----------------------------------------------------------------------------------
