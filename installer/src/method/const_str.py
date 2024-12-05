#  coding: utf-8
# 文字列をすべてここに保管する
# ----------------------------------------------------------------------------------
# 2024/7/17 更新
# tree -I 'venv|resultOutput|__pycache__'

# ----------------------------------------------------------------------------------
from enum import Enum


# ----------------------------------------------------------------------------------
#! 基本必須

class Dir(Enum):
    result='resultOutput'
    input='inputData'


# ----------------------------------------------------------------------------------
#! 基本必須

class SubDir(Enum):
    pickles='pickles'
    cookies='cookies'
    DBSubDir='DB'
    SCREEN_SHOT='screenshot'
    RESULT_SUMMARY='result_summary'


# ----------------------------------------------------------------------------------
#! 基本必須

class FileName(Enum):
    RESULT_FILE='result_summary'
    TRUE_HISTORY='True 検知履歴'
    FALSE_HISTORY='False 検知履歴'


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



# ----------------------------------------------------------------------------------
# サイトURL

class MAClubInfo(Enum):
    LOGIN_URL='https://gameclub.jp/signin'
    HOME_URL='https://www.xdomain.ne.jp/'
    TARGET_URL=''

    GSS_URL=''


# ----------------------------------------------------------------------------------
# サイトURL

class GameClubInfo(Enum):
    LOGIN_URL='https://gameclub.jp/signin'
    HOME_URL='https://www.xdomain.ne.jp/'
    TARGET_URL=''

    GSS_URL=''


# ----------------------------------------------------------------------------------
# サイトURL

class rrmtClubInfo(Enum):
    LOGIN_URL='https://gameclub.jp/signin'
    HOME_URL='https://www.xdomain.ne.jp/'
    TARGET_URL=''

    GSS_URL=''


# ----------------------------------------------------------------------------------
class GssInfo(Enum):
    SITE='https://docs.google.com/spreadsheets/d/1PJd_nTjYDh_jfxSJ4vNaQ13be90IHrBqVQ7srjPYu1A/export?format=csv&gid=0'

    ID_COL='site_id'

    NAME_COL='site_name'

    URL_COL='site_url'



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
# アカウントID

class AccountId(Enum):
    pass


# ----------------------------------------------------------------------------------
# GCPのjsonファイルなどのKeyFile

class KeyFile(Enum):
    gssKeyFile='sns-auto-430920-08274ad68b41.json'


# ----------------------------------------------------------------------------------
# スプシID

class GssSheetId(Enum):
    XSheetId=''
    InstagramSheetId=''


# ----------------------------------------------------------------------------------
# スプシのColumn

class GssColumns(Enum):
    pass


# ----------------------------------------------------------------------------------
# Endpoint

class EndPoint(Enum):
    Line ="https://notify-api.line.me/api/notify"
    Chatwork = 'https://api.chatwork.com/v2'
    Slack = 'https://slack.com/api/chat.postMessage'
    Discord = 'https://discord.com/api/webhooks/1220239805204660314/niMRY1OVJwYh3PY9X9EfF2O6C7ZPhukRDoXfsXlwGBz4n1HKE81MA1B6TQiy2FUnzHfk'

    ChatGPT = 'https://api.openai.com/v1/engines/{}/completions'
    X_image = 'https://upload.twitter.com/1.1/media/upload.json'
    X = 'https://api.twitter.com/2/tweets'

    Instagram = 'https://graph.facebook.com/v16.0/{}/media'
    InstagramImage = 'https://graph.facebook.com/v16.0/{}/media_publish'


# ----------------------------------------------------------------------------------


class SendMessage(Enum):
    CHATWORK="""
    **{siteName}** に **{domain}** があることを確認できました！

    詳細はスクリーンショットにてご確認ください。
    """




# ----------------------------------------------------------------------------------
# ChatgptUtils

class ChatgptUtils(Enum):
    # "gpt-4o-mini-2024-07-18" or "gpt-4o-2024-08-06"
    model='gpt-4o-mini-2024-07-18'

    endpointUrl='https://api.openai.com/v1/chat/completions'

    MaxToken=16000

# ----------------------------------------------------------------------------------


class ChatGptPrompt(Enum):
    recommend="""
    次の物件情報に基づいて、不動産物件の紹介文を作成してください。紹介文は**{minLen}文字以上、{maxlen}文字以内で、物件の魅力を引き立てる文章にしてください。以下の4つの特徴の中から最も物件のアピールにつながる特徴を選んで**文章を作成してください。

    特徴1: {item0}
    特徴2: {item1}
    特徴3: {item2}
    特徴4: {item3}

    必ず守ってほしい条件:
    ・女性がコメントしているような口調で、親しみやすい文章にしてください。
    ・指定された内容以外のテキスト（例えばコメントや補足説明、不要な情報）は生成しないでください。Prompt以外の内容を返さないでください。
    ・指定された情報や文言のみを使用して、簡潔かつ正確な文章を作成してください。
    ・文末はきちんと完結させてください。途中で終わらないようにしてください。
    ・特徴1〜4までの中で2つ以上は入れて下さい。
    ・{minLen}文字以上、{maxlen}文字以内で作成して下さい。

    物件を探している人が興味を持つように、女性らしい視点でシンプルで魅力的な紹介文を作成してください。
    """

    fixedPrompt="""
    「前回生成されたテキストは指定した文字数をオーバーしていました。以下の条件を守りながら、再度テキストを生成してください。

    ・最大文字数: {charLimit}文字
    ・必ず、指定された内容以外のテキスト（例えばコメントや補足説明、不要な情報）は生成しないでください。Prompt以外の内容を返さないでください。
    ・指定された情報や文言のみを使って、簡潔かつ正確な文章を作成してください。
    ・文末はきちんと完結させてください。途中で終わらないようにしてください。

    前回のテキスト: "{beforePrompt}"

    修正してほしい内容:

    ・指定文字数を超えないように調整してください。」
    """


# ----------------------------------------------------------------------------------


class NGWordList(Enum):
    ngWords=[
        'バス有',
        # 'バストイレ同室',

    ]

# ----------------------------------------------------------------------------------

class Address(Enum):
    addressList = [
    '北海道', '青森県', '岩手県', '宮城県', '秋田県', '山形県', '福島県',
    '茨城県', '栃木県', '群馬県', '埼玉県', '千葉県', '東京都', '神奈川県',
    '新潟県', '富山県', '石川県', '福井県', '山梨県', '長野県', '岐阜県',
    '静岡県', '愛知県', '三重県', '滋賀県', '京都府', '大阪府', '兵庫県',
    '奈良県', '和歌山県', '鳥取県', '島根県', '岡山県', '広島県', '山口県',
    '徳島県', '香川県', '愛媛県', '高知県', '福岡県', '佐賀県', '長崎県',
    '熊本県', '大分県', '宮崎県', '鹿児島県', '沖縄県'
]

# ----------------------------------------------------------------------------------
