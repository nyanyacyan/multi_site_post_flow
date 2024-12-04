# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import os
from enum import Enum
from dotenv import load_dotenv

load_dotenv()


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************


class ElementSpecify(Enum):
    ID='id'
    XPATH='xpath'
    CSS='css'


# **********************************************************************************


class ElementPath(Enum):


# ----------------------------------------------------------------------------------
# flowMoveGetElement

    # 検索画面の消去する
    SEARCH_DELETE_BTN_PATH="//a[@class='w_close']"


    # 詳細ページの要素（.formatにて追記することで引数に充当）
    DETAIL_PAGE_BTN_PATH="//a[text()='物件画像'])[{}]"  # すべての//a[text()='物件画像']を取得→1個目


# ----------------------------------------------------------------------------------
# _listPageInfo

    STATION_VALUE="//div[@class='searchResultLsit'][{}]//tr[@class='searchResultLsitTabTr1']//div[@class='vicinityInfo']/p[@class='new']/span[1]"

    TRAIN_LINE="//div[@class='searchResultLsit'][{}]//tr[@class='searchResultLsitTabTr1']//div[@class='vicinityInfo']/p[@class='new']/span[2]"

    WAKING="//div[@class='searchResultLsit'][{}]//tr[@class='searchResultLsitTabTr1']//div[@class='vicinityInfo']/p[@class='new']/span[3]"


# ----------------------------------------------------------------------------------
# _detailPageInfo


    NAME="//th[text()='物件名']/following-sibling::td[1]/span"

    AD="//th[text()='広告可否']/following-sibling::td[1]/span"

    AREA="//th[text()='専有面積']/following-sibling::td[1]/span"

    ITEM="//th[text()='設備']/following-sibling::td[1]/span"

    ADDRESS="//th[text()='物件所在地']/following-sibling::td[1]/span"

    RENT="//th[text()='賃料']/following-sibling::td[1]/span"

    MANAGEMENT_COST="//th[text()='管理費等']/following-sibling::td[1]/span"

    DEPOSIT="//th[text()='敷金']/following-sibling::td[1]/span"

    KEY_MONEY="//th[text()='礼金']/following-sibling::td[1]/span"



# ----------------------------------------------------------------------------------
# ここでos.getenv("PASS")を定義してしまうと実行してしまう関係からここでは呼び出さない

class LoginElement(Enum):
    LOGIN_INFO = {
        "idBy": "id",
        "idValue": "username",
        "passBy": "id",
        "passValue": "password",
        "btnBy": "name",
        "btnValue": "action",
        "bypassIdBy": "xpath",
        "bypassIdValue": "//a[text()='いい生活アカウントでログイン']",
        "modalBy" : "xpath",
        "modalValue": "//a[@class='w_close']",
    }


    BYPASS_SITE_INFO = {
        'by': 'xpath',
        'value': "//a[text()='いい生活アカウントでログイン']"
    }

# ----------------------------------------------------------------------------------


# class TextInfo(Enum):



# ----------------------------------------------------------------------------------


class ImageInfo(Enum):
    #! 修正必要
    BASE_IMAGE_PATH = {
        "A": "/Users/nyanyacyan/Desktop/Project_file/ImageAutomation/installer/src/method/inputData/A.png",
        "B": "/Users/nyanyacyan/Desktop/Project_file/ImageAutomation/installer/src/method/inputData/B.png",
        "C": "/Users/nyanyacyan/Desktop/Project_file/ImageAutomation/installer/src/method/inputData/C.png",
        "D": "/Users/nyanyacyan/Desktop/Project_file/ImageAutomation/installer/src/method/inputData/D.png",
    }

    BASE_IMAGE_FILE_NAME = {
        "A": "A.png",
        "B": "B.png",
        "C": "C.png",
        "D": "D.png",
    }

    BASE_IMAGE_SIZE = (1080, 1080)

    FONT_SIZES = {
        "A": 50,
        "B": 30,
        "C": 30,
        "D": 30,
    }

    COMMENT_SIZE = 20
    UNDER_BOTTOM_SIZE = 20


# 白 (255, 255, 255), 黒 (0, 0, 0),赤 (255, 0, 0)
# 緑 (0, 255, 0), 青 (0, 0, 255), オレンジ (255, 165, 0)
    FONT_COLORS = {
        'A': (0, 200, 0),
        'B': (0, 0, 0),
        'C': (0, 0, 0),
        'D': (0, 0, 0),
    }

    UNDER_BOTTOM_COLOR = (180, 180, 180)

    #! 修正必要
    FONT_PATH = "/Users/nyanyacyan/Desktop/Project_file/ImageAutomation/installer/src/method/inputData/MPLUSRounded1c-ExtraBold.ttf"
    # /Users/nyanyacyan/Library/Mobile Documents/com~apple~CloudDocs/Downloads/MPLUSRounded1c-ExtraBold.ttf
    FONT_NAME = "MPLUSRounded1c-Medium.ttf"


    IMAGE_NUM = {
        "A": "1",
        "B": "2",
        "C": "2",
        "D": "2",
    }

    POSITIONS = {
        "A": {
            "IMAGE_CENTER": (0, 83, 1080, 998),
            "TEXT_LEFT_TOP": (50, 93, 300, 183),
            "TEXT_RIGHT_TOP": (400, 93, 1030, 183),
            "TEXT_BOTTOM_LEFT": (50, 910, 1020, 1000),
            "BACK_TOP": (0, 83, 1200, 180),
            "BACK_BOTTOM": (0, 900, 1200, 997),
        },
        "B": {
            "IMAGE_TOP_LEFT": (20, 190, 550, 500),
            "IMAGE_BOTTOM_LEFT": (20, 550, 450, 970),
            "TEXT_TOP_RIGHT": (600, 200, 1080, 500),
            "TEXT_BOTTOM_RIGHT": (725, 620, 995, 850),
            "TEXT_UNDER_BOTTOM": (440, 1020, 720, 1050)
        },
        "C": {
            "IMAGE_TOP_LEFT": (20, 190, 550, 500),
            "IMAGE_BOTTOM_LEFT": (20, 550, 480, 970),
            "TEXT_TOP_RIGHT": (600, 200, 1080, 440),
            "TEXT_BOTTOM_RIGHT": (790, 605, 1030, 745)
        },
        "D": {
            "IMAGE_TOP_LEFT": (20, 190, 550, 575),
            "IMAGE_BOTTOM_LEFT": (20, 585, 480, 970),
            "TEXT_TOP_RIGHT": (600, 200, 1080, 440),
            "TEXT_BOTTOM_RIGHT": (745, 530, 1015, 760)
        }
    }



    TOP_MAX_WIDTH = 120
    TOP_LINE_HEIGHT = 200
    MAX_WIDTH = 300
    LINE_HEIGHT = 30


    FILL_COLOR_BLACK = (0, 0, 0)
    FILL_COLOR_GREEN = (0, 255, 0)
    FILL_COLOR_WHITE = (255, 255, 255)


    TOP_IMAGE_SIZE = (700, 1300)
    IMAGE_SIZE = (300, 300)
    IMAGE_SIZE_SMALL = (150, 150)



# ----------------------------------------------------------------------------------
