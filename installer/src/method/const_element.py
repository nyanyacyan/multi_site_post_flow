#  coding: utf-8
# 文字列をすべてここに保管する
# ----------------------------------------------------------------------------------
# 2024/7/17 更新
# tree -I 'venv|resultOutput|__pycache__'

# ----------------------------------------------------------------------------------
# import
import os
from enum import Enum
from dotenv import load_dotenv
load_dotenv()


# ----------------------------------------------------------------------------------
# GSS情報

class GssInfo(Enum):

    GAME_CLUB = {
        'jsonKeyName': 'sns-auto-430920-08274ad68b41.json',
        'spreadsheetId': '11hUzuGZaXmM070E8Gl5YA5ydUcWGDcjV0MkGQEpzLx8',
        'workSheetName': 'GAME_CLUB',
    }

    MA_CLUB = {
        'jsonKeyName': 'sns-auto-430920-08274ad68b41.json',
        'spreadsheetId': '11hUzuGZaXmM070E8Gl5YA5ydUcWGDcjV0MkGQEpzLx8',
        'workSheetName': 'MA_CLUB',
    }

    RRMT_CLUB = {
        'jsonKeyName': 'sns-auto-430920-08274ad68b41.json',
        'spreadsheetId': '11hUzuGZaXmM070E8Gl5YA5ydUcWGDcjV0MkGQEpzLx8',
        'workSheetName': 'RRMT_CLUB',
    }


# ----------------------------------------------------------------------------------
# ログイン情報

class LoginInfo(Enum):

    SITE_PATTERNS = {
        'GAME_CLUB':{
            'SITE_NAME': 'GAME_CLUB',
            'LOGIN_URL': 'https://gameclub.jp/signin',
            'HOME_URL': 'https://gameclub.jp/mypage',
            'TABLE_NAME': 'GAME_CLUB',
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
            'SELL_BTN': "//a[@href='/mypage/products/add']",

        },
        'MA_CLUB':{
            'SITE_NAME': 'MA_CLUB',
            'LOGIN_URL': 'https://maclub.jp/signin',
            'HOME_URL': 'https://maclub.jp/mypage',
            'TABLE_NAME': 'MA_CLUB',
            'ID_BY': 'xpath',
            'ID_VALUE' : "//input[@name='email']",
            'ID_TEXT': os.getenv('MA_CLUB_ID'),
            'PASS_BY': 'xpath',
            'PASS_VALUE': "//input[@name='password']",
            'PASS_TEXT': os.getenv('MA_CLUB_PASS'),
            'BTN_BY': 'xpath',
            'BTN_VALUE': "//button[contains(@class, 'btn-registration') and normalize-space(text())='ログイン']",
            'LOGIN_AFTER_ELEMENT_BY': 'xpath',
            'LOGIN_AFTER_ELEMENT_VALUE': "//a[@href='/mypage' and contains(text(), 'マイページ')]",
            'RECAPTCHA_CHECKBOX_BY': "id",
            'RECAPTCHA_CHECKBOX_VALUE': "recaptcha-anchor",
        },
        'RRMT_CLUB':{
            'SITE_NAME': 'RRMT_CLUB',
            'LOGIN_URL': 'https://rmt.club/user-login',
            'HOME_URL': 'https://www.xdomain.ne.jp/',
            'TABLE_NAME': 'RRMT_CLUB',
            'ID_BY': 'xpath',
            'ID_VALUE' : "//input[@id='UserMail']",
            'ID_TEXT': os.getenv('RRMT_CLUB_ID'),
            'PASS_BY': 'xpath',
            'PASS_VALUE': "//input[@id='UserPassword' and @name='data[User][password]']",
            'PASS_TEXT': os.getenv('RRMT_CLUB_PASS'),
            'BTN_BY': 'xpath',
            'BTN_VALUE': "//input[@class='btn_type1 fade' and @type='submit' and @value='ログイン']",
            'LOGIN_AFTER_ELEMENT_BY': 'xpath',
            'LOGIN_AFTER_ELEMENT_VALUE': "//div[@class='top-link-btns']/a[@href='/mypage' and contains(@class, 'btn_mypage')]",
            'RECAPTCHA_CHECKBOX_BY': "id",
            'RECAPTCHA_CHECKBOX_VALUE': "recaptcha-anchor",
        },
    }


# ----------------------------------------------------------------------------------
# 出品要素

class SellInfo(Enum):

    GAME_CLUB = {
        'SELL_BTN': "//a[@href='/mypage/products/add']",
        '': '',
        '': '',
    }

    MA_CLUB = {
        '': '',
        '': '',
        '': '',
    }

    RRMT_CLUB = {
        '': '',
        '': '',
        '': '',
    }


# ----------------------------------------------------------------------------------
