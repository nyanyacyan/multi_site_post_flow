#  coding: utf-8
# 文字列をすべてここに保管する
# ----------------------------------------------------------------------------------
# 2024/7/17 更新
# tree -I 'venv|resultOutput|__pycache__'

# ----------------------------------------------------------------------------------
import os
from enum import Enum
from dotenv import load_dotenv
load_dotenv()

# ----------------------------------------------------------------------------------


class LoginInfo(Enum):

    SITE_PATTERNS = {
        'GAME_CLUB':{
            'LOGIN_URL': 'https://gameclub.jp/signin',
            'HOME_URL': 'https://gameclub.jp/mypage',
            'TABLE_NAME': 'GAME_CLUB_COOKIES_TABLE_COLUMNS',
            'ID_BY': 'xpath',
            'ID_VALUE' : "//input[@name='email']",
            'ID_TEXT': os.getenv('GAME_CLUB_ID'),
            'PASS_BY': 'xpath',
            'PASS_VALUE': "//input[@name='password']",
            'PASS_TEXT': os.getenv('GAME_CLUB_PASS'),
            'BTN_BY': 'xpath',
            'BTN_VALUE': "//button[contains(@class, 'btn-registration') and contains(text(), 'ログイン')]",
            'LOGIN_AFTER_ELEMENT_BY': 'xpath',
            'LOGIN_AFTER_ELEMENT_VALUE': "//a[@href='/mypage' and contains(text(),'マイページ')]",
            'RECAPTCHA_CHECKBOX_BY': "id",
            'RECAPTCHA_CHECKBOX_VALUE': "recaptcha-anchor",
        },
        'MA_CLUB':{
            'LOGIN_URL': 'https://maclub.jp/signin',
            'HOME_URL': 'https://maclub.jp/mypage',
            'TABLE_NAME': 'MA_CLUB_COOKIES_TABLE_COLUMNS',
            'ID_BY': 'xpath',
            'ID_VALUE' : "//input[@name='email']",
            'ID_TEXT': os.getenv('MA_CLUB_ID'),
            'PASS_BY': 'xpath',
            'PASS_VALUE': "//input[@name='password']",
            'PASS_TEXT': os.getenv('MA_CLUB_PASS'),
            'BTN_BY': 'xpath',
            'BTN_VALUE': "//button[@class='btn btn-danger btn-registration' and text()='ログイン']",
            'LOGIN_AFTER_ELEMENT_BY': 'xpath',
            'LOGIN_AFTER_ELEMENT_VALUE': "//a[@href='/mypage' and contains(text(), 'マイページ')]",
            'RECAPTCHA_CHECKBOX_BY': "id",
            'RECAPTCHA_CHECKBOX_VALUE': "recaptcha-anchor",
        },
        'RRMT_CLUB':{
            'LOGIN_URL': 'https://rmt.club/user-login',
            'HOME_URL': 'https://www.xdomain.ne.jp/',
            'TABLE_NAME': 'RRMT_CLUB_COOKIES_TABLE_COLUMNS',
            'ID_BY': 'xpath',
            'ID_VALUE' : "//input[@id='UserMail']",
            'ID_TEXT': os.getenv('RRMT_CLUB_ID'),
            'PASS_BY': 'xpath',
            'PASS_VALUE': "//input[@id='UserPassword' and @name='data[User][password]']",
            'PASS_TEXT': os.getenv('RRMT_CLUB_PASS'),
            'BTN_BY': 'xpath',
            'BTN_VALUE': "//input[@class='btn_type1 fade' and @type='submit' and @value='ログイン']",
            'LOGIN_AFTER_ELEMENT_BY': 'xpath',
            'LOGIN_AFTER_ELEMENT_VALUE': "",
            'RECAPTCHA_CHECKBOX_BY': "id",
            'RECAPTCHA_CHECKBOX_VALUE': "recaptcha-anchor",
        },
    }

