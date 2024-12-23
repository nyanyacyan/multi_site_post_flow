# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# 2024/9/14 更新

# Pathの設定 export PYTHONPATH="${PYTHONPATH}:/Users/nyanyacyan/Desktop/project_file/SNS_auto_upper/installer/src/method/base"

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import pytest
import pandas as pd
from unittest.mock import patch, mock_open
import pickle

# 自作モジュール
from installer.src.method.base.pklChange import PickleRead, PickleWrite


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************
# pytestを実行する


class TestPickleRead:

    # ----------------------------------------------------------------------------------

    def testSuccess(self):
        pklName = "dummyName"
        data = b"\x80\x03}q\x00X\x03\x00\x00\x00keyq\x01X\x05\x00\x00\x00valueq\x02s."

        instance = PickleRead()

        with patch("builtins.open", mock_open(read_data=data)) as mockedFile:

            # ここを対象のメソッドに変更
            instance.pickleToDf(pklName=pklName)

            # 一回だけモックを呼び出せているか確認
            mockedFile().read.assert_called()

    # ----------------------------------------------------------------------------------

    def testError(self):
        pklName = "dummyName"
        data = b"\x80\x03}q\x00X\x03\x00\x00\x00keyq\x01X\x05\x00\x00\x00valueq\x02s."

        instance = PickleRead()

        with patch("builtins.open", mock_open(read_data=data)) as mockedFile:

            mockedFile.side_effect = TypeError

            with pytest.raises(TypeError):

                # ここを対象のメソッドに変更
                result = instance.pklToUtf8(pklName=pklName)

                # 一回だけモックを呼び出せているか確認
                mockedFile().read.assert_called()

            assert result is None


# ----------------------------------------------------------------------------------
# **********************************************************************************
# pytestを実行する


class TestPickleWrite:

    # ----------------------------------------------------------------------------------

    def testSuccess(self):
        pklName = "dummyName"
        data = "dummyName"

        instance = PickleWrite()

        with patch("builtins.open", mock_open()) as mockedFile:

            # ここを対象のメソッドに変更
            instance.pickleToDf(data=data, pklName=pklName)

            # 一回だけモックを呼び出せているか確認
            mockedFile().read.assert_called()

    # ----------------------------------------------------------------------------------

    def testDfSuccess(self):
        pklName = "dummyName"
        data = {
            "TestData": ["a", "B"],
            "TestData2": ["d", "e"],
            "TestData3": ["f", "g"],
        }

        df = pd.DataFrame(data)

        instance = PickleWrite()

        with patch("builtins.open", mock_open()) as mockedFile:

            instance.dfToPickle(df=df, pklName=pklName)

            mockedFile().write.assert_called()

    # ----------------------------------------------------------------------------------

    def testError(self):
        pklName = "dummyName"
        data = "TestData"

        instance = PickleWrite()

        with patch("builtins.open", mock_open()) as mockedFile:

            mockedFile.side_effect = ValueError

            with pytest.raises(ValueError):

                result = instance.toPkl(data=data, pklName=pklName)

                # 一回だけモックを呼び出せているか確認
                mockedFile().read.assert_called()

            assert result is None

    # ----------------------------------------------------------------------------------

    def testDfError(self):
        pklName = "dummyName"
        data = {
            "TestData": ["a", "B"],
            "TestData2": ["d", "e"],
            "TestData3": ["f", "g"],
        }

        df = pd.DataFrame(data)

        instance = PickleWrite()

        with patch("builtins.open", mock_open()) as mockedFile:

            mockedFile.side_effect = ValueError

            with pytest.raises(ValueError):

                result = instance.dfToPickle(df=df, pklName=pklName)

                # 一回だけモックを呼び出せているか確認
                mockedFile().read.assert_called()

            assert result is None


# ----------------------------------------------------------------------------------
