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
        "jsonKeyName": "sns-auto-430920-08274ad68b41.json",
        "spreadsheetId": "11hUzuGZaXmM070E8Gl5YA5ydUcWGDcjV0MkGQEpzLx8",
        "workSheetName": "GAME_CLUB",
        "SORT_WORD_LIST": ["GAME_CLUB", "GC", "ゲームクラブ", "GAME"],
    }

    MA_CLUB = {
        "jsonKeyName": "sns-auto-430920-08274ad68b41.json",
        "spreadsheetId": "11hUzuGZaXmM070E8Gl5YA5ydUcWGDcjV0MkGQEpzLx8",
        "workSheetName": "MA_CLUB",
        "SORT_WORD_LIST": ["M&A", "MA", "エムアンドエー", "MA_CLUB", "M&A_CLUB"],
    }

    RMT_CLUB = {
        "jsonKeyName": "sns-auto-430920-08274ad68b41.json",
        "spreadsheetId": "11hUzuGZaXmM070E8Gl5YA5ydUcWGDcjV0MkGQEpzLx8",
        "workSheetName": "RMT_CLUB",
        "SORT_WORD_LIST": ["RMT", "rmt", "アールエムティ"],
    }


# ----------------------------------------------------------------------------------
# ログイン情報


class LoginInfo(Enum):

    SITE_PATTERNS = {
        "GAME_CLUB": {
            "SITE_NAME": "GAME_CLUB",
            "LOGIN_URL": "https://gameclub.jp/signin",
            "HOME_URL": "https://gameclub.jp/mypage",
            "TABLE_NAME": "GAME_CLUB",
            "ID_BY": "xpath",
            "ID_VALUE": "//input[@name='email']",
            "ID_TEXT": os.getenv("GAME_CLUB_ID"),
            "PASS_BY": "xpath",
            "PASS_VALUE": "//input[@name='password']",
            "PASS_TEXT": os.getenv("GAME_CLUB_PASS"),
            "BTN_BY": "xpath",
            "BTN_VALUE": "//button[contains(@class, 'btn-registration') and contains(text(), 'ログイン')]",
            "LOGIN_AFTER_ELEMENT_BY": "xpath",
            "LOGIN_AFTER_ELEMENT_VALUE": "//a[@href='/mypage' and contains(text(),'マイページ')]",
            "RECAPTCHA_CHECKBOX_BY": "id",
            "RECAPTCHA_CHECKBOX_VALUE": "recaptcha-anchor",
            "SELL_BTN": "//a[@href='/mypage/products/add']",
            "SORT_WORD_LIST": ["GAME_CLUB", "GC", "ゲームクラブ", "GAME"],
        },
        "MA_CLUB": {
            "SITE_NAME": "MA_CLUB",
            "LOGIN_URL": "https://maclub.jp/signin",
            "HOME_URL": "https://maclub.jp/mypage",
            "TABLE_NAME": "MA_CLUB",
            "ID_BY": "xpath",
            "ID_VALUE": "//input[@name='email']",
            "ID_TEXT": os.getenv("MA_CLUB_ID"),
            "PASS_BY": "xpath",
            "PASS_VALUE": "//input[@name='password']",
            "PASS_TEXT": os.getenv("MA_CLUB_PASS"),
            "BTN_BY": "xpath",
            "BTN_VALUE": "//button[contains(@class, 'btn-registration') and normalize-space(text())='ログイン']",
            "LOGIN_AFTER_ELEMENT_BY": "xpath",
            "LOGIN_AFTER_ELEMENT_VALUE": "//a[@href='/mypage' and contains(text(), 'マイページ')]",
            "RECAPTCHA_CHECKBOX_BY": "id",
            "RECAPTCHA_CHECKBOX_VALUE": "recaptcha-anchor",
            "SORT_WORD_LIST": ["M&A", "MA", "エムアンドエー"],
        },
        "RMT_CLUB": {
            "SITE_NAME": "RMT_CLUB",
            "LOGIN_URL": "https://rmt.club/user-login",
            "HOME_URL": "https://rmt.club/mypage",
            "TABLE_NAME": "RMT_CLUB",
            "ID_BY": "xpath",
            "ID_VALUE": "//input[@id='UserMail']",
            "ID_TEXT": os.getenv("RMT_CLUB_ID"),
            "PASS_BY": "xpath",
            "PASS_VALUE": "//input[@id='UserPassword' and @name='data[User][password]']",
            "PASS_TEXT": os.getenv("RMT_CLUB_PASS"),
            "BTN_BY": "xpath",
            "BTN_VALUE": "//input[@class='btn_type1 fade' and @type='submit' and @value='ログイン']",
            "LOGIN_AFTER_ELEMENT_BY": "xpath",
            "LOGIN_AFTER_ELEMENT_VALUE": "//div[@class='top-link-btns']/a[@href='/mypage' and contains(@class, 'btn_mypage')]",
            "RECAPTCHA_CHECKBOX_BY": "id",
            "RECAPTCHA_CHECKBOX_VALUE": "recaptcha-anchor",
            "SORT_WORD_LIST": ["RMT", "rmt", "アールエムティ"],
        },
    }


# ----------------------------------------------------------------------------------
# 出品要素


class SellInfo(Enum):

    GAME_CLUB = {
        "INPUT_PHOTO_FOLDER_NAME": "01_GAME_CLUB",
        # 出品するをクリック
        "FIRST_SELL_BTN_BY": "xpath",
        "FIRST_SELL_BTN_VALUE": '//a[contains(@class, "btm-add")]',
        # 画像を添付
        "FILE_INPUT_BY": "id",
        "FILE_INPUT_VALUE": "item-images",
        # DOMの確認
        "CHECK_BY": "css",
        "CHECK_VALUE": "#sortableArea .upimages-item",
        # ゲームタイトル入力
        "GAME_TITLE_CLICK_BY": "id",
        "GAME_TITLE_CLICK_VALUE": "btn-search-title",
        # POPUPにゲームタイトルを入力
        "GAME_TITLE_INPUT_BY": "id",
        "GAME_TITLE_INPUT_VALUE": "search-title-input",
        # POPUPにゲームタイトルをクリック
        "GAME_TITLE_SELECT_BY": "css",
        "GAME_TITLE_SELECT_VALUE": "div.syllabary-list > div.item",
        # カテゴリ選択
        "CATEGORY_INTAI_SELECT_VALUE": '//*[@id="account-type-id-10"]',
        "CATEGORY_RISEMARA_SELECT_VALUE": '//*[@id="account-type-id-20"]',
        "CATEGORY_ITEM_SELECT_VALUE": '//*[@id="account-type-id-30"]',
        "CATEGORY_DAIKO_SELECT_VALUE": '//*[@id="account-type-id-40"]',
        # 出品タイトル
        "SELL_TITLE_INPUT_BY": "id",
        "SELL_TITLE_INPUT_VALUE": "name",
        # 商品説明
        "SELL_EXPLANATION_INPUT_BY": "id",
        "SELL_EXPLANATION_INPUT_VALUE": "input-body-text",
        # 課金総額
        "CHARGE_VALUE": '//input[@name="subcategory_unique_property_1_value"]',
        # 買い手への初回msg
        "FIRST_MSG_BY": "id",
        "FIRST_MSG_VALUE": "firstchat",
        # 出品を通知
        "USER_NOTIFY": "//input[@type='text' and @name='notify_user_id']",
        # 出品方法
        "SELL_METHOD_FURIMA_VALUE": "//label[contains(text(), 'フリマ販売')]",
        "SELL_METHOD_TIME_SALE_VALUE": "//label[contains(text(), 'タイムセール')]",
        # 商品価格
        "PRICE_VALUE": '//input[@name="price"]',
        # 暗証番号にレ点
        "PIN_CHECK_CLICK_VALUE": "//input[@type='checkbox' and @name='pin_checkbox']",
        # 暗証番号を入力
        "PIN_INPUT_AREA_BY": "id",
        "PIN_INPUT_AREA_VALUE": "pin",
        "PIN_INPUT_VALUE": os.getenv("PIN_VALUE"),
        # 確認する
        "CHECK_VALUE": '//button[@id="btn-confirm"]',
        # 出品する
        "SELL_BTN": '//button[@id="btn-add"]',
        # POPUPを消去
        "POPUP_DELETE_BTN_VALUE": '//div[@class="btn-modal-close"]',
        # マイページに戻る
        "MY_PAGE_VALUE": '//div[@class="header-top-btns"]/a[@class="icon-user"]',
    }

    ##########

    MA_CLUB = {
        "INPUT_PHOTO_FOLDER_NAME": "02_MA_CLUB",
        # 出品する
        "FIRST_SELL_BTN_BY": "xpath",
        "FIRST_SELL_BTN_VALUE": '//a[contains(@class, "btm-add")]',
        # 画像添付
        "FILE_INPUT_BY": "id",
        "FILE_INPUT_VALUE": "item-images",
        # DOM確認
        "CHECK_BY": "css",
        "CHECK_VALUE": "#sortableArea .upimages-item",
        # 案件カテゴリーをクリック
        "CASE_TITLE_CLICK_BY": "id",
        "CASE_TITLE_CLICK_VALUE": "btn-search-title",
        # POPUPに入力
        "CASE_TITLE_INPUT_BY": "id",
        "CASE_TITLE_INPUT_VALUE": "search-title-input",
        # POPUPから選択
        "CASE_TITLE_SELECT_BY": "css",
        "CASE_TITLE_SELECT_VALUE": "div.syllabary-list > div.item",
        # 種別を選択
        "CATEGORY_JYOTO_SELECT_VALUE": '//*[@id="account-type-id-10"]',
        "CATEGORY_SELL_SELECT_VALUE": '//*[@id="account-type-id-20"]',
        "CATEGORY_OTHER_SELECT_VALUE": '//*[@id="account-type-id-30"]',
        "CATEGORY_UNYODAIKO_SELECT_VALUE": '//*[@id="account-type-id-40"]',
        # 案件タイトル
        "SELL_TITLE_INPUT_BY": "id",
        "SELL_TITLE_INPUT_VALUE": "name",
        # 案件説明
        "SELL_EXPLANATION_INPUT_BY": "id",
        "SELL_EXPLANATION_INPUT_VALUE": "input-body-text",
        # 買い手への初回msg
        "FIRST_MSG_BY": "id",
        "FIRST_MSG_VALUE": "firstchat",
        # 案件の登録を通知
        "USER_NOTIFY": "//input[@type='text' and @name='notify_user_id']",
        # 売却価格
        "PRICE_VALUE": '//input[@name="price"]',
        # 暗証番号にレ点
        "PIN_CHECK_CLICK_VALUE": "//input[@type='checkbox' and @name='pin_checkbox']",
        # 暗証番号を入力
        "PIN_INPUT_AREA_BY": "id",
        "PIN_INPUT_AREA_VALUE": "pin",
        "PIN_INPUT_VALUE": os.getenv("PIN_VALUE"),
        # 確認する
        "CHECK_VALUE": '//button[@id="btn-confirm"]',
        # 出品する
        "SELL_BTN": '//button[@id="btn-add"]',
        # POPUPを削除
        "POPUP_DELETE_BTN_VALUE": '//div[@class="btn-modal-close"]',
        # マイページに戻る
        "MY_PAGE_VALUE": '//div[@class="header-top-btns"]/a[@class="icon-user"]',
    }

    ##########

    RMT_CLUB = {
        "INPUT_PHOTO_FOLDER_NAME": "03_RMT_CLUB",
        # 売りたいをクリック
        "SELL_BTN_ONE": "//div[@class='footer_contents fbox']//a[@href='/deals/add']",
        "SELL_SELECT_BTN": "//label[@for='DealRequest0']",
        # タイトル入力
        "SELL_TITLE_INPUT_BY": "id",
        "SELL_TITLE_INPUT_VALUE": "suggest_title",
        # 代行
        "CATEGORY_ACCOUNT_SELECT_VALUE": "//div[@id='deal_account_list']/input[@value='1']",
        "CATEGORY_ITEM_SELECT_VALUE": "//div[@id='deal_account_list']/input[@value='2']",
        "CATEGORY_RISEMARA_SELECT_VALUE": "//div[@id='deal_account_list']/input[@value='3']",
        "CATEGORY_DAIKO_SELECT_VALUE": "//div[@id='deal_account_list']/input[@value='4']",
        # 掲載タイトル
        "COMMENT_TITLE_BY": "id",
        "COMMENT_TITLE_VALUE": "DealDealTitle",
        # タグ
        "TAG_BY": "id",
        "TAG_VALUE": "DealTag",
        # 詳細内容
        "SELL_EXPLANATION_INPUT_BY": "id",
        "SELL_EXPLANATION_INPUT_VALUE": "DealInfo",
        # 画像取り込み
        "FILE_INPUT_BY": "id",
        "FILE_INPUT_VALUE": "//label[@id='add_upload_file']/input[@type='file']",
        # DOMで確認する箇所
        "CHECK_BY": "css",
        "CHECK_VALUE": "#sortableArea .upimages-item",
        # ユーザーに出品を通知
        "USER_NOTIFY_BY": "id",
        "USER_NOTIFY_VALUE": "DealUserName",
        # 取引価格
        "PRICE_BY": "id",
        "PRICE_VALUE": "kakaku",
        # 確認ボタン
        "CHECK_VALUE": "//input[@type='submit' and @value='確認']",
        # 同意するにクリック
        "AGREE_VALUE": "//input[@type='checkbox' and @name='data[Deal][agreement]']",
        # 出品する
        "SELL_BTN": "//button[@type='submit' and contains(text(), '出品する')]",
        # マイページに戻る
        "MY_PAGE_VALUE": "//a[@class='btn_mypage fade' and text()='マイページ']",
        "": "",
    }


# ----------------------------------------------------------------------------------


class GuiInfo(Enum):
    GAME_CLUB = {
        "JSON_KEY_NAME": "sns-auto-430920-08274ad68b41.json",
        "SORT_WORD_LIST": [
            "GAME_CLUB",
            "GC",
            "ゲームクラブ",
            "GAME",
            "game_club",
            "game",
            "game club",
        ],
        "GSS_INPUT_TITLE": "Spreadsheet 情報",
        "MAIN_WINDOW_TITLE": "GAME_CLUB Automation Tool",
        "FOLDER_NAME": "01_GAME_CLUB",
        "COL_NAME": "画像フォルダ",
        "GUI_WIDTH": 300,
        "GUI_HEIGHT": 600,
        "X_RATIO": 0.94,
        "Y_RATIO": 0.55,
        "BACKGROUND_COLOR": "#FFFFFF",
        "LOGO_NAME": "gc_logo",
        "USER_INPUT_TITLE": "USER情報",
        "INPUT_EXAMPLE_ID": "対象のIDを入力",
        "INPUT_EXAMPLE_PASS": "対象のPassを入力",
        "INPUT_EXAMPLE_GSS_URL": "対象のスプレッドシートのURLを入力",
        "ID_LABEL": "USER ID",
        "PASS_LABEL": "PASSWORD",
        "GSS_URL_LABEL": "URL",
        "DROPDOWN_LABEL": "Worksheet",
        "INTERVAL_TIME_GROUP_TITLE": "出品間隔",
        "INPUT_EXAMPLE_INTERVAL_MIN": "下限",
        "INPUT_BETWEEN_LABEL": "分 から",
        "INPUT_EXAMPLE_INTERVAL_MAX": "上限",
        "INPUT_LAST_LABEL": "分 まで",
        "UPTIME_TIME_GROUP_TITLE": "稼働時間",
        "INPUT_START_UPTIME_TITLE": "開始時間",
        "INPUT_EXAMPLE_START_UPTIME": "カレンダーから選択",
        "INPUT_END_UPTIME_TITLE": "終了時間",
        "INPUT_EXAMPLE_END_UPTIME": "カレンダーから選択",
        "UPDATE_SELECT_GROUP_TITLE": "自動 更新処理",
        "RADIO_BTN_TRUE_TITLE": "あり",
        "RADIO_BTN_FALSE_TITLE": "なし",
        "PROCESS_BTN_NAME": "START",
        "CANCEL_BTN_NAME": "STOP",
        "GSS_URL_BTN": "取得",
        "GSS_FOLDER_CHECK_BTN": "確認",
    }

    MA_CLUB = {
        "JSON_KEY_NAME": "sns-auto-430920-08274ad68b41.json",
        "SORT_WORD_LIST": ["M&A", "MA", "エムアンドエー", "MA_CLUB", "M&A_CLUB"],
        "GSS_INPUT_TITLE": "Spreadsheet 情報",
        "MAIN_WINDOW_TITLE": "M&A_CLUB Automation Tool",
        "FOLDER_NAME": "02_MA_CLUB",
        "COL_NAME": "画像フォルダ",
        "GUI_WIDTH": 300,
        "GUI_HEIGHT": 600,
        "X_RATIO": 0.72,
        "Y_RATIO": 0.55,
        "BACKGROUND_COLOR": "#FFFFFF",
        "LOGO_NAME": "ma_logo",
        "USER_INPUT_TITLE": "USER情報",
        "INPUT_EXAMPLE_ID": "対象のIDを入力",
        "INPUT_EXAMPLE_PASS": "対象のPassを入力",
        "INPUT_EXAMPLE_GSS_URL": "対象のスプレッドシートのURLを入力",
        "ID_LABEL": "USER ID",
        "PASS_LABEL": "PASSWORD",
        "GSS_URL_LABEL": "URL",
        "DROPDOWN_LABEL": "Worksheet",
        "INTERVAL_TIME_GROUP_TITLE": "出品間隔",
        "INPUT_EXAMPLE_INTERVAL_MIN": "下限",
        "INPUT_BETWEEN_LABEL": "分 から",
        "INPUT_EXAMPLE_INTERVAL_MAX": "上限",
        "INPUT_LAST_LABEL": "分 まで",
        "UPTIME_TIME_GROUP_TITLE": "稼働時間",
        "INPUT_START_UPTIME_TITLE": "開始時間",
        "INPUT_EXAMPLE_START_UPTIME": "カレンダーから選択",
        "INPUT_END_UPTIME_TITLE": "終了時間",
        "INPUT_EXAMPLE_END_UPTIME": "カレンダーから選択",
        "UPDATE_SELECT_GROUP_TITLE": "自動 更新処理",
        "RADIO_BTN_TRUE_TITLE": "あり",
        "RADIO_BTN_FALSE_TITLE": "なし",
        "PROCESS_BTN_NAME": "START",
        "CANCEL_BTN_NAME": "STOP",
        "GSS_URL_BTN": "取得",
        "GSS_FOLDER_CHECK_BTN": "確認",
    }

    RMT_CLUB = {
        "JSON_KEY_NAME": "sns-auto-430920-08274ad68b41.json",
        "SORT_WORD_LIST": ["RMT", "rmt", "アールエムティ", "RMT_CLUB", "rmt_club"],
        "GSS_INPUT_TITLE": "Spreadsheet 情報",
        "MAIN_WINDOW_TITLE": "RMT_CLUB Automation Tool",
        "FOLDER_NAME": "02_MA_CLUB",
        "COL_NAME": "画像フォルダ",
        "GUI_WIDTH": 300,
        "GUI_HEIGHT": 600,
        "X_RATIO": 0.5,
        "Y_RATIO": 0.55,
        "BACKGROUND_COLOR": "#FFFFFF",
        "LOGO_NAME": "ma_logo",
        "USER_INPUT_TITLE": "USER情報",
        "INPUT_EXAMPLE_ID": "対象のIDを入力",
        "INPUT_EXAMPLE_PASS": "対象のPassを入力",
        "INPUT_EXAMPLE_GSS_URL": "対象のスプレッドシートのURLを入力",
        "ID_LABEL": "USER ID",
        "PASS_LABEL": "PASSWORD",
        "GSS_URL_LABEL": "URL",
        "DROPDOWN_LABEL": "Worksheet",
        "INTERVAL_TIME_GROUP_TITLE": "出品間隔",
        "INPUT_EXAMPLE_INTERVAL_MIN": "下限",
        "INPUT_BETWEEN_LABEL": "分 から",
        "INPUT_EXAMPLE_INTERVAL_MAX": "上限",
        "INPUT_LAST_LABEL": "分 まで",
        "UPTIME_TIME_GROUP_TITLE": "稼働時間",
        "INPUT_START_UPTIME_TITLE": "開始時間",
        "INPUT_EXAMPLE_START_UPTIME": "カレンダーから選択",
        "INPUT_END_UPTIME_TITLE": "終了時間",
        "INPUT_EXAMPLE_END_UPTIME": "カレンダーから選択",
        "UPDATE_SELECT_GROUP_TITLE": "自動 更新処理",
        "RADIO_BTN_TRUE_TITLE": "あり",
        "RADIO_BTN_FALSE_TITLE": "なし",
        "PROCESS_BTN_NAME": "START",
        "CANCEL_BTN_NAME": "STOP",
        "GSS_URL_BTN": "取得",
        "GSS_FOLDER_CHECK_BTN": "確認",
    }


# ----------------------------------------------------------------------------------


class UpdateInfo(Enum):
    GAME_CLUB = {
        "SELL_ITEM_BTN_VALUE": "//div[@class='side-mypage-menu']//a[@href='/mypage/products' and contains(text(), '出品した商品')]",
        "ITEM_SORT_BTN_VALUE": "//select[@name='sort_index']",
        "SELECT_VALUE": "1",
        "DISABLE_ELEMENT_VALUE": "//a[@class='btn btn-boost btn-disabled' and @href='javascript:void(0)']",
        "UPDATE_BTN_VALUE": "//div[@class='boost-modal-content']//a[@class='btn btn-boost ']",
        "": "",
    }

    ##########

    MA_CLUB = {
        "SELL_ITEM_BTN_VALUE": "//div[@class='side-mypage-menu']//a[@href='/mypage/products' and contains(text(), '売却登録した案件')]",
        "ITEM_SORT_BTN_VALUE": "//select[@name='sort_index']",
        "SELECT_VALUE": "1",
        "DISABLE_ELEMENT_VALUE": "//a[@class='btn btn-boost btn-disabled' and @href='javascript:void(0)']",
        "UPDATE_BTN_VALUE": "//div[@class='boost-modal-content']//a[@class='btn btn-boost ']",
        "": "",
    }


# ----------------------------------------------------------------------------------
