# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# Pathの設定 export PYTHONPATH="${PYTHONPATH}:/Users/nyanyacyan/Desktop/project_file/ImageAutomation/installer/src/method/base"

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import

from unittest.mock import MagicMock

# 自作モジュール
from installer.src.method.base.loginWithId import LoginID


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************
# 単体テスト 写真を取得


class TestDriver:

    # ----------------------------------------------------------------------------------
    # テストOK

    def testOpenSiteSuccess(self):
        chrome = MagicMock()
        loginUrl = "http://example.com"
        homeUrl = "dummyUrl.com"

        instance = LoginID(chrome=chrome, loginUrl=loginUrl, homeUrl=homeUrl)

        instance.openSite()

        assert chrome.get.call_count == 2
        chrome.get.assert_any_call(loginUrl)


# ----------------------------------------------------------------------------------
