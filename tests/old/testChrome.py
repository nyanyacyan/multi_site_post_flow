# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# Pathの設定 export PYTHONPATH="${PYTHONPATH}:/Users/nyanyacyan/Desktop/project_file/SNS_auto_upper/installer/src/method/base"

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import

import pytest
from unittest.mock import patch, AsyncMock

# 自作モジュール
from installer.src.method.base.chrome import ChromeManager


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************
# 単体テスト 写真を取得


class TestChrome:

    # ----------------------------------------------------------------------------------

    def testChromeSetup(self):
        chromeSetup = ChromeManager()

        chrome = chromeSetup.setupChrome()
        chrome.get("https://www.google.co.jp/")

        assert chrome.current_url == "https://www.google.co.jp/"

        chrome.quit()


# ----------------------------------------------------------------------------------
