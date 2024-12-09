#  coding: utf-8
# 文字列をすべてここに保管する
# ----------------------------------------------------------------------------------
# 2024/7/17 更新
# tree -I 'venv|resultOutput|__pycache__'

# ----------------------------------------------------------------------------------
from enum import Enum


# ----------------------------------------------------------------------------------


class LoginInfo(Enum):

    SITE_PATTERNS = {
        'GAME_CLUB':{
            'ID_BY': 'xpath',
            'ID_VALUE' : '',
            'PASS_BY': 'xpath',
            'PASS_VALUE': '',
            'BTN_BY': 'xpath',
            'BTN_VALUE': '',
            'LOGIN_AFTER_ELEMENT_BY': 'xpath',
            'LOGIN_AFTER_ELEMENT_VALUE': '',
        },
        'MA_CLUB':{
            'ID_BY': 'xpath',
            'ID_VALUE' : '',
            'PASS_BY': 'xpath',
            'PASS_VALUE': '',
            'BTN_BY': 'xpath',
            'BTN_VALUE': '',
            'LOGIN_AFTER_ELEMENT_BY': 'xpath',
            'LOGIN_AFTER_ELEMENT_VALUE': '',
        },
        'RRMT_CLUB':{
            'ID_BY': 'xpath',
            'ID_VALUE' : '',
            'PASS_BY': 'xpath',
            'PASS_VALUE': '',
            'BTN_BY': 'xpath',
            'BTN_VALUE': '',
            'LOGIN_AFTER_ELEMENT_BY': 'xpath',
            'LOGIN_AFTER_ELEMENT_VALUE': '',
        },
    }

