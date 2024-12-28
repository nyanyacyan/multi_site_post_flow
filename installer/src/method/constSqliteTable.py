# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
from enum import Enum

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************


class TableSchemas(Enum):


# ----------------------------------------------------------------------------------
# サブ辞書

    GAME_CLUB = {
        "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "name": "TEXT NOT NULL",
        "value": "TEXT NOT NULL",
        "domain": "TEXT",
        "path": "TEXT",
        "expires": "INTEGER",
        "maxAge": "INTEGER",
        "secure": "INTEGER DEFAULT 0",
        "httpOnly": "INTEGER DEFAULT 0",
        "sameSite": "TEXT",
        "createTime": "INTEGER NOT NULL"
    }


# ----------------------------------------------------------------------------------
# サブ辞書
# priorityは優先順位→若い番号ほど順位が高い


    MA_CLUB = {
        "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "name": "TEXT NOT NULL",
        "value": "TEXT NOT NULL",
        "domain": "TEXT",
        "path": "TEXT",
        "expires": "INTEGER",
        "maxAge": "INTEGER",
        "secure": "INTEGER DEFAULT 0",
        "httpOnly": "INTEGER DEFAULT 0",
        "sameSite": "TEXT",
        "createTime": "INTEGER NOT NULL"
    }



# ----------------------------------------------------------------------------------
# サブ辞書

    RMT_CLUB = {
        "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "name": "TEXT NOT NULL",
        "value": "TEXT NOT NULL",
        "domain": "TEXT",
        "path": "TEXT",
        "expires": "INTEGER",
        "maxAge": "INTEGER",
        "secure": "INTEGER DEFAULT 0",
        "httpOnly": "INTEGER DEFAULT 0",
        "sameSite": "TEXT",
        "createTime": "INTEGER NOT NULL"
    }



# ----------------------------------------------------------------------------------
#* メイン辞書

    TABLE_PATTERN = {
        "GAME_CLUB": GAME_CLUB,
        "MA_CLUB": MA_CLUB,
        "RMT_CLUB": RMT_CLUB
    }


# ----------------------------------------------------------------------------------


    BASE_COOKIES_TABLE_COLUMNS = (
        "id",
        "name",
        "value",
        "domain",
        "path",
        "expires",
        "maxAge",
        "secure",
        "httpOnly",
        "sameSite",
        "createTime"
    )
