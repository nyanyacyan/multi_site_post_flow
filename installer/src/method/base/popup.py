# coding: utf-8
# ----------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------
# import
import tkinter as tk
from tkinter import messagebox
from typing import Callable, Optional


# 自作モジュール
from .utils import Logger


# **********************************************************************************


class Popup:
    def __init__(self, debugMode=True):

        # logger
        self.getLogger = Logger(__name__, debugMode=debugMode)
        self.logger = self.getLogger.getLogger()


# ----------------------------------------------------------------------------------


    def popupCommentOnly(self, popupTitle: str, comment: str):
        root = tk.Tk()
        root.withdraw()
        messagebox.showwarning(popupTitle, comment)

        root.destroy()  # メインウィンドウを破棄

# ----------------------------------------------------------------------------------


    def popupCommentChoice(self, popupTitle: str, comment: str, func: Optional[Callable[[], None]]):
        root = tk.Tk()
        root.withdraw()
        result = messagebox.askyesno(popupTitle, comment)

        if result:
            func()

        root.destroy()  # メインウィンドウを破棄


# ----------------------------------------------------------------------------------