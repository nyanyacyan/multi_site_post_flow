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

    GAME_CLUB_COOKIES_TABLE_COLUMNS = {
        "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "name": "TEXT NOT NULL",
        "value": "TEXT NOT NULL",
        "domain": "TEXT",
        "path": "TEXT",
        "expires": "INTEGER",
        "maxAge": "INTEGER",
        "createTime": "INTEGER NOT NULL",
    }


# ----------------------------------------------------------------------------------
# サブ辞書
# priorityは優先順位→若い番号ほど順位が高い


    MA_CLUB_COOKIES_TABLE_COLUMNS = {
        "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "name": "TEXT NOT NULL",
        "value": "TEXT NOT NULL",
        "domain": "TEXT",
        "path": "TEXT",
        "expires": "INTEGER",
        "maxAge": "INTEGER",
        "createTime": "INTEGER NOT NULL",
    }


# ----------------------------------------------------------------------------------
# サブ辞書

    RRMT_CLUB_COOKIES_TABLE_COLUMNS = {
        "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "name": "TEXT NOT NULL",
        "value": "TEXT NOT NULL",
        "domain": "TEXT",
        "path": "TEXT",
        "expires": "INTEGER",
        "maxAge": "INTEGER",
        "createTime": "INTEGER NOT NULL",
    }


# ----------------------------------------------------------------------------------
#* メイン辞書

    TABLE_PATTERN = {
        "game_club_cookies": GAME_CLUB_COOKIES_TABLE_COLUMNS,
        "ma_club_cookies": MA_CLUB_COOKIES_TABLE_COLUMNS,
        "rrmt_club_cookies": RRMT_CLUB_COOKIES_TABLE_COLUMNS
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
        "createTime"
    )