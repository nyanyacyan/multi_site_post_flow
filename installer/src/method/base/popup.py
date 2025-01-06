# coding: utf-8
# ----------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------
# import
import tkinter as tk  # python -m tkinter このコマンドで使えるかどうか確認できる
from tkinter import messagebox
from typing import Callable, Optional


# 自作モジュール
from .utils import Logger


# **********************************************************************************


class Popup:
    def __init__(self):

        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

    # ----------------------------------------------------------------------------------

    def popupCommentOnly(self, popupTitle: str, comment: str):
        root = tk.Tk()
        root.withdraw()
        messagebox.showwarning(popupTitle, comment)

        root.destroy()  # メインウィンドウを破棄

    # ----------------------------------------------------------------------------------

    def popupCommentChoice(
        self, popupTitle: str, comment: str, func: Optional[Callable[[], None]]
    ):
        root = tk.Tk()
        root.withdraw()
        result = messagebox.askyesno(popupTitle, comment)

        if result:
            func()

        root.destroy()  # メインウィンドウを破棄


# ----------------------------------------------------------------------------------


    def timer_popup(self, ):
        pass

