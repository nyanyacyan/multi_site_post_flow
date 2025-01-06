# coding: utf-8
# ----------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------
# import
import sys, os


# 自作モジュール
from .utils import Logger

# **********************************************************************************


class SysCommand:
    def __init__(self):
        # logger
        self.getLogger = Logger()
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
