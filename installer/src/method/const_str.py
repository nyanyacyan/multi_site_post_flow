#  coding: utf-8
# 文字列をすべてここに保管する
# ----------------------------------------------------------------------------------
# 2024/7/17 更新
# tree -I 'venv|resultOutput|__pycache__'

# ----------------------------------------------------------------------------------
from enum import Enum


# ----------------------------------------------------------------------------------
#! 基本必須 → pathで使ってる

class Dir(Enum):
    result='resultOutput'
    input='inputData'


# ----------------------------------------------------------------------------------
#! 基本必須

class SubDir(Enum):
    pickles='pickles'
    cookies='cookies'
    DBSubDir='DB'
    BUCK_UP= 'buck_up'
    SCREEN_SHOT='screenshot'
    INPUT_PHOTO='input_photo'
    LOGO='logo'


# ----------------------------------------------------------------------------------
#! 基本必須

class FileName(Enum):
    LOG_FILE_NAME='multi_site_post_flow_log_file'
    DB_FILE_NAME='multi_site_data'
    CHROME_OP_CAPTCHA='hlifkpholllijblknnmbfagnkjneagid.crx'
    CHROME_OP_IFRAME='uBlock-Origin.crx'


# ----------------------------------------------------------------------------------
#! 基本必須

class Extension(Enum):
    text='.txt'
    csv='.csv'
    json='.json'
    pickle='.pkl'
    excel='.xlsx'
    yaml='.yaml'
    cookie='cookie.pkl'
    DB='.db'
    PNG='.png'
    ICO='.ico'


# ----------------------------------------------------------------------------------
#! 基本必須 → popupで使ってる

class ErrorComment(Enum):
    PHOTO_TITLE='画像がありません'
    PHOTO_COMMENT='指定のフォルダに画像がありません。\n指定のフォルダをご確認ください\n{}'


# ----------------------------------------------------------------------------------

class SeleniumWait(Enum):
    BY = {
        'xpath': 'By.XPATH',
        'id': 'By.ID',
        'css': 'By.CSS_SELECTOR',
        'class': 'By.CLASS_NAME',
        'name': 'By.NAME',
        'tag': 'By.TAG_NAME',
        'link_text': 'By.LINK_TEXT',
    }

# ----------------------------------------------------------------------------------


class StatusName(Enum):
    RECAPTCHA_CHECKBOX='aria-checked'


# ----------------------------------------------------------------------------------


class SiteName(Enum):
    GAME_CLUB='GAME_CLUB'
    MA_CLUB='MA_CLUB'
    RMT_CLUB='RMT_CLUB'


# ----------------------------------------------------------------------------------


class TableName(Enum):
    Cookie='cookiesDB'
    TEXT='text'
    IMAGE='image'


# ----------------------------------------------------------------------------------


class Encoding(Enum):
    utf8='utf-8'


# ----------------------------------------------------------------------------------
# DiscordUrl

class Debug(Enum):
    discord = 'https://discord.com/api/webhooks/1220239805204660314/niMRY1OVJwYh3PY9X9EfF2O6C7ZPhukRDoXfsXlwGBz4n1HKE81MA1B6TQiy2FUnzHfk'


# ----------------------------------------------------------------------------------
# 通知メッセージ

class ErrorMessage(Enum):
    chromeDriverManagerErrorTitle = "ChromeDriver セットアップエラー"
    chromeDriverManagerError = (
        "ChromeDriver のセットアップに失敗しました。以下の手順を確認してください：\n"
        "1. ChromeDriver のバージョンがインストールされている Chrome ブラウザと一致しているか\n"
        "2. 必要な権限が不足していないか\n"
        "3. PATH 環境変数に ChromeDriver のパスが正しく設定されているか\n"
        "4. 必要であれば、システムを再起動して環境をリフレッシュしてください。\n"
        "詳細なエラー内容はログをご確認ください。"
    )


# ----------------------------------------------------------------------------------
# GCPのjsonファイルなどのKeyFile

class KeyFile(Enum):
    gssKeyFile='sns-auto-430920-08274ad68b41.json'


# ----------------------------------------------------------------------------------
# Endpoint

class EndPoint(Enum):
    Line ="https://notify-api.line.me/api/notify"
    Chatwork = 'https://api.chatwork.com/v2'
    Slack = 'https://slack.com/api/chat.postMessage'
    Discord = 'https://discord.com/api/webhooks/1220239805204660314/niMRY1OVJwYh3PY9X9EfF2O6C7ZPhukRDoXfsXlwGBz4n1HKE81MA1B6TQiy2FUnzHfk'


# ----------------------------------------------------------------------------------
