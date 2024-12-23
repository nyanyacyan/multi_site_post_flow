# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# Pathの設定 export PYTHONPATH="${PYTHONPATH}:/Users/nyanyacyan/Desktop/project_file/ImageAutomation/installer/src/method/base"

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import

from unittest.mock import MagicMock, patch
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 自作モジュール
from installer.src.method.base.loginWithId import LoginID


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************
# 単体テスト 写真を取得


class TestSeleniumInput:

    # ----------------------------------------------------------------------------------
    # テストOK

    def testInputSuccess(self):
        chrome = MagicMock()
        loginUrl = "http://example.com"
        homeUrl = "dummyUrl.com"
        by = "id"
        value = "dummyPath"
        inputText = "dummyText"

        instance = LoginID(chrome=chrome, loginUrl=loginUrl, homeUrl=homeUrl)

        instance.element = MagicMock()

        instance.element.inputText.return_value = "mocked input"

        # WebDriverWaitをモック化
        with patch(
            "installer.src.method.base.driverDeco.WebDriverWait"
        ) as mock_WebDriverWait:
            # WebDriverWait の until メソッドが返すモックされた要素
            mock_element = MagicMock(spec=WebElement)
            mock_WebDriverWait.return_value.until.return_value = mock_element

            # テスト対象のメソッドを実行
            result = instance.inputId(by=by, value=value, inputText=inputText)

            # inputText メソッドが正しい引数で呼ばれたか確認
            instance.element.inputText.assert_called_once_with(
                by=by, value=value, inputText=inputText
            )

            # WebDriverWaitが正しく呼び出されたか確認
            mock_WebDriverWait.assert_called_once_with(chrome, 10)
            mock_WebDriverWait.return_value.until.assert_called_once()

            # 戻り値の確認
            assert result == "mocked input"


# ----------------------------------------------------------------------------------
# **********************************************************************************
# 単体テスト 写真を取得


class TestSeleniumClick:

    # ----------------------------------------------------------------------------------
    # テストOK

    def testClickSuccess(self):
        chrome = MagicMock()
        loginUrl = "http://example.com"
        homeUrl = "dummyUrl.com"
        by = "id"
        value = "dummyPath"

        instance = LoginID(chrome=chrome, loginUrl=loginUrl, homeUrl=homeUrl)

        instance.element = MagicMock()

        # WebDriverWaitをモック化
        with patch(
            "installer.src.method.base.driverDeco.WebDriverWait"
        ) as mock_WebDriverWait:
            # WebDriverWait の until メソッドが返すモックされた要素
            mock_element = MagicMock(spec=WebElement)
            mock_WebDriverWait.return_value.until.return_value = mock_element

            # テスト対象のメソッドを実行
            instance.clickLoginBtn(by=by, value=value)

            # clickElement メソッドが正しい引数で呼ばれたか確認
            instance.element.clickElement.assert_called_once_with(by=by, value=value)

            # WebDriverWaitの呼び出し回数が2回であることを確認
            assert mock_WebDriverWait.call_count == 2


# ----------------------------------------------------------------------------------
