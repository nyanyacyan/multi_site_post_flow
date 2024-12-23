# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# 2024/8/1 更新
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import

from datetime import datetime


# 自作モジュール
from .utils import Logger
from .decorators import Decorators

from const_str import FileName


decoInstance = Decorators()


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************
# GSSからプロンプトを取得してChatGPTへのリクエスト


class GetContext:
    def __init__(self):

        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

    # ----------------------------------------------------------------------------------
    # sheet_nameを当日の曜日によって変更する

    @decoInstance.funcBase
    def getWeekday(self):

        todayWeekdayNum = datetime.today().weekday()
        self.logger.debug(f"todayWeekdayNum: {todayWeekdayNum}")

        sheetNames = ["月曜", "火曜", "水曜", "木曜", "金曜", "土曜", "日曜"]

        todayWeekday = sheetNames[todayWeekdayNum]
        self.logger.debug(f"todayWeekday: {todayWeekday}")

        return todayWeekday


# ----------------------------------------------------------------------------------
# **********************************************************************************
