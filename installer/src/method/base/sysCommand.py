# coding: utf-8
# ----------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------
# import
import sys, os


# 自作モジュール
from .utils import Logger
from const_str import FileName


# **********************************************************************************


class SysCommand:
    def __init__(self, debugMode=True):

        # logger
        self.getLogger = Logger(
            moduleName=FileName.LOG_FILE_NAME.value, debugMode=debugMode
        )
        self.logger = self.getLogger.getLogger()

    # ----------------------------------------------------------------------------------

    def restartSys(self):
        # windowsの再起動
        if sys.platform == "win32":
            os.system("shutdown /r /t 1")

        # Macの再起動
        elif sys.platform == "darwin":
            os.system("sudo shutdown -r now")

        # linuxの再起動
        elif sys.platform.startswith("linux"):
            os.system("sudo reboot")


# ----------------------------------------------------------------------------------
