# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# Pathの設定 export PYTHONPATH="${PYTHONPATH}:/Users/nyanyacyan/Desktop/project_file/SNS_auto_upper/installer/src/method/base"

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import

import time
from unittest.mock import patch, MagicMock

# 自作モジュール
from installer.src.method.base.cookieManager import CookieManager


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************
# 単体テスト 写真を取得


class TestCookie:

    # ----------------------------------------------------------------------------------
    # テストOK

    def testCookieManAgeSuccess(self):
        chrome = MagicMock()
        homeUrl = "http://example.com"

        instance = CookieManager(chrome=chrome, homeUrl=homeUrl)

        with patch.object(instance.__class__, "getCookies") as mock_getCookie:
            mock_getCookie.return_value = [
                {
                    "name": "sessionId",
                    "value": "dummySession",
                    "domain": "example.com",
                    "path": "/",
                    "expires": int(time.time()) + 3600,
                    "max-age": 3600,
                }
            ]

            result = instance.startBoolFilePath()
            resultWithoutId = {
                key: value
                for key, value in result.items()
                if key != "id" and key != "max-age"
            }

            mock_getCookie_value = mock_getCookie.return_value[0]
            mockWithoutMaxAge = {
                key: value
                for key, value in mock_getCookie_value.items()
                if key != "max-age"
            }

            print(resultWithoutId)
            print(mockWithoutMaxAge)
            assert resultWithoutId == mockWithoutMaxAge

    # ----------------------------------------------------------------------------------
    # テストOK

    def testCookieExpiresSuccess(self):
        chrome = MagicMock()
        homeUrl = "http://example.com"

        instance = CookieManager(chrome=chrome, homeUrl=homeUrl)

        with patch.object(instance.__class__, "getCookies") as mock_getCookie:
            mock_getCookie.return_value = [
                {
                    "name": "sessionId",
                    "value": "dummySession",
                    "domain": "example.com",
                    "path": "/",
                    "expires": int(time.time()) + 3600,
                }
            ]

            result = instance.startBoolFilePath()
            resultWithoutId = {
                key: value
                for key, value in result.items()
                if key != "id" and key != "max-age"
            }

            mock_getCookie_value = mock_getCookie.return_value[0]
            mockWithoutMaxAge = {
                key: value
                for key, value in mock_getCookie_value.items()
                if key != "max-age"
            }

            print(resultWithoutId)
            assert resultWithoutId == mockWithoutMaxAge

    # ----------------------------------------------------------------------------------
    # テストOK

    def testCookieNoExpires(self):
        chrome = MagicMock()
        homeUrl = "http://example.com"

        instance = CookieManager(chrome=chrome, homeUrl=homeUrl)

        with patch.object(instance.__class__, "getCookies") as mock_getCookie:
            mock_getCookie.return_value = [
                {
                    "name": "sessionId",
                    "value": "dummySession",
                    "domain": "example.com",
                    "path": "/",
                    "expires": "",
                    "max-age": "",
                }
            ]

            result = instance.startBoolFilePath()
            resultWithoutId = {
                key: value for key, value in result.items() if key != "id"
            }

            mock_getCookie_value = mock_getCookie.return_value[0]
            # mockWithoutMaxAge = {key: value for key, value in mock_getCookie_value.items() if key != 'max-age' and key != 'expires'}

            print(resultWithoutId)
            print(mock_getCookie_value)
            assert resultWithoutId == mock_getCookie_value

    # ----------------------------------------------------------------------------------
    # Cookie情報が、なにもない場合の挙動
    # テストOK

    def testCookieNoData(self):
        chrome = MagicMock()
        homeUrl = "http://example.com"

        instance = CookieManager(chrome=chrome, homeUrl=homeUrl)

        with patch.object(instance.__class__, "getCookies") as mock_getCookie:
            mock_getCookie.return_value = [
                {
                    "name": "",
                    "value": "",
                    "domain": "",
                    "path": "",
                    "expires": "",
                    "max-age": "",
                }
            ]

            result = instance.startBoolFilePath()

            assert result == None


# ----------------------------------------------------------------------------------
