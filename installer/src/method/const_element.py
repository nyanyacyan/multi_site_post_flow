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
        'INPUT_PHOTO_FOLDER_NAME': '01_GAME_CLUB',
        'FILE_INPUT_BY': 'id',
        'FILE_INPUT_VALUE': 'item-images',
        'CHECK_BY': 'css',
        'CHECK_VALUE': '#sortableArea .upimages-item',
        'GAME_TITLE_CLICK_VALUE': '//*[@id="btn-search-title"]',
        'GAME_TITLE_INPUT_VALUE': '//*[@id="search-title-input"]',
        'GAME_TITLE_SELECT_VALUE': '//div[contains(@data-item, \'"name":"{}"\')]',
        'CATEGORY_INTAI_SELECT_VALUE': '//*[@id="account-type-id-10"]',
        'CATEGORY_ITEM_SELECT_VALUE': '//*[@id="account-type-id-30"]',
        'CATEGORY_DAIKO_SELECT_VALUE': '//*[@id="account-type-id-40"]',
        'SELL_TITLE_INPUT_BY': 'id',
        'SELL_TITLE_INPUT_VALUE': 'name',
        'SELL_EXPLANATION_INPUT_BY': 'id',
        'SELL_EXPLANATION_INPUT_VALUE': 'input-body-text',
        'CHARGE_VALUE': '//input[@name="subcategory_unique_property_1_value"]',
        'FIRST_MSG_BY': 'id',
        'FIRST_MSG_VALUE': 'firstchat',
        'SELL_METHOD_FURIMA_VALUE': '//input[@id="productType1"]',
        'SELL_METHOD_TIME_SALE_VALUE': '//input[@id="productType3"]',
        'PRICE_VALUE': '//input[@name="price"]',
        'CHECK_VALUE': '//button[@id="btn-confirm"]',
        'SELL_BTN': '//button[@id="btn-add"]',
        'POPUP_DELETE_BTN_VALUE': '//div[@class="btn-modal-close"]',
        'MY_PAGE_VALUE': '//div[@class="header-top-btns"]/a[@class="icon-user"]',
        '': '',
    }

    MA_CLUB = {
        'SELL_BTN': "//a[@href='/mypage/products/add']",
        'INPUT_PHOTO_FOLDER_NAME': '02_MA_CLUB',
        'FILE_INPUT_BY': 'id',
        'FILE_INPUT_VALUE': 'item-images',
        'CHECK_BY': 'css',
        'CHECK_VALUE': '#sortableArea .upimages-item',
        'GAME_TITLE_CLICK_VALUE': '//*[@id="btn-search-title"]',
        'GAME_TITLE_INPUT_VALUE': '//*[@id="search-title-input"]',
        'GAME_TITLE_SELECT_VALUE': '//div[contains(@data-item, \'"name":"{}"\')]',
        'CATEGORY_JYOTO_SELECT_VALUE': '//*[@id="account-type-id-10"]',
        'CATEGORY_OTHER_SELECT_VALUE': '//*[@id="account-type-id-30"]',
        # 'CATEGORY_DAIKO_SELECT_VALUE': '//*[@id="account-type-id-40"]',
        'SELL_TITLE_INPUT_BY': 'id',
        'SELL_TITLE_INPUT_VALUE': 'name',
        'SELL_EXPLANATION_INPUT_BY': 'id',
        'SELL_EXPLANATION_INPUT_VALUE': 'input-body-text',
        # 'CHARGE_VALUE': '//input[@name="subcategory_unique_property_1_value"]',
        'FIRST_MSG_BY': 'id',
        'FIRST_MSG_VALUE': 'firstchat',
        'SELL_METHOD_FURIMA_VALUE': '//input[@id="productType1"]',
        'SELL_METHOD_TIME_SALE_VALUE': '//input[@id="productType3"]',
        'PRICE_VALUE': '//input[@name="price"]',
        'CHECK_VALUE': '//button[@id="btn-confirm"]',
        'SELL_BTN': '//button[@id="btn-add"]',
        'POPUP_DELETE_BTN_VALUE': '//div[@class="btn-modal-close"]',
        'MY_PAGE_VALUE': '//div[@class="header-top-btns"]/a[@class="icon-user"]',
        '': '',
    }

    RRMT_CLUB = {
        '': '',
        '': '',
        '': '',
        '': '',
        '': '',
        '': '',
        '': '',
        '': '',
        '': '',
        '': '',
        '': '',
        '': '',
        '': '',
        '': '',
        '': '',
        '': '',
        '': '',
        '': '',
        '': '',
        '': '',
        '': '',
    }


# ----------------------------------------------------------------------------------
