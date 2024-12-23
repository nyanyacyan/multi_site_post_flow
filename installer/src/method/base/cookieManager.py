# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import time
from selenium.webdriver.chrome.webdriver import WebDriver


# 自作モジュール
from .utils import Logger
from .SQLite import SQLite
from .loginWithId import LoginID
from ..const_domain_search import TableName, ColumnsName
from const_str import FileName

from .decorators import Decorators

decoInstance = Decorators()


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************


class CookieManager:
    def __init__(self, chrome: WebDriver, homeUrl: str, loginUrl: str):
        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

        self.chrome = chrome
        self.homeUrl = homeUrl
        self.loginUrl = loginUrl

        self.tableName = TableName.Cookie.value

        self.columnsName = ColumnsName.Cookies.value
        self.primaryKey = ColumnsName.PRIMARY_KEY.value
        self.currentTime = int(time.time())

        # インスタンス
        self.sqlite = SQLite()
        self.loginID = LoginID(
            chrome=self.chrome,
            homeUrl=self.homeUrl,
            loginUrl=self.loginUrl,
        )

    # ----------------------------------------------------------------------------------
    # start①
    # DBが存在確認

    @decoInstance.funcBase
    def startBoolFilePath(self, url: str, loginInfo: dict):
        if self.sqlite.boolFilePath():
            self.sqlite.checkTableExists()
            return self.cookieDataExistsInDB(url=url, loginInfo=loginInfo)
        else:
            self.logger.debug(
                f"{self.tableName} が作られてません。これよりテーブル作成開始"
            )
            self.sqlite.isFileExists()  # ファイルを作成
            self.sqlite.createAllTable()  # 全てのテーブルを作成
            return self.getCookieFromAction2(url=url, loginInfo=loginInfo)

    # ----------------------------------------------------------------------------------
    # ②
    # DBにCookieの存在確認

    @decoInstance.funcBase
    def cookieDataExistsInDB(self, url: str, loginInfo: dict):
        DBColNames = self.sqlite.columnsExists(tableName=self.tableName)

        self.logger.debug(f"DBColNames: {DBColNames}")
        self.logger.debug(f"self.columnsName: {self.columnsName}")

        # self.columnsNameの中にあるものがDBColNamesに全て入っているのかを確認
        result = all(cokName in DBColNames for cokName in self.columnsName)
        if result is True:
            self.logger.info(f"DBの中にcookieのテーブルを発見\n{DBColNames}")
            return self.checkCookieLimit(url=url, loginInfo=loginInfo)
        else:
            self.logger.warning(
                f"{self.tableName} のテーブルデータがありません。Cookieを取得します"
            )
            return self.getCookieFromAction2(url=url, loginInfo=loginInfo)

    # ----------------------------------------------------------------------------------
    # ③
    # DBにあるCookieの有効期限が有効化を確認

    @decoInstance.funcBase
    def checkCookieLimit(self, url: str, loginInfo: dict):
        newCookieData = self.sqlite.getColMaxValueRow(
            tableName=self.tableName, primaryKey=self.primaryKey
        )

        self.logger.warning(f"newCookieData: {newCookieData}")

        if newCookieData:

            # sqlite3.Row オブジェクトの中身を確認
            row_data = newCookieData[0]

            # すべての値をリストとして取得
            all_values = list(row_data)
            self.logger.info(f"All values in row: {all_values}")

            # キーと値のペアをループで表示
            for key in row_data.keys():
                self.logger.info(f"{key}: {row_data[key]}")

            expiresValue = newCookieData[0][5]  # タプルの場合には数値で拾う
            maxAgeValue = newCookieData[0][6]
            createTimeValue = newCookieData[0][7]

            self.logger.warning(
                f"\nexpiresValue: {expiresValue}\nmaxAgeValue: {maxAgeValue}\ncreateTimeValue: {createTimeValue}\n"
            )

            if maxAgeValue:
                return self._getMaxAgeLimit(
                    maxAgeValue=maxAgeValue, createTimeValue=createTimeValue
                )

            elif expiresValue:
                return self._getExpiresLimit(
                    expiresValue=expiresValue, url=url, loginInfo=loginInfo
                )

            else:
                self.logger.warning("Cookieの有効期限が設定されてません")
                return self.getCookieFromAction2(url=url, loginInfo=loginInfo)

        else:
            self.logger.error(
                f"DBテーブルの中にcookieのデータが存在しません: {newCookieData}"
            )
            return self.getCookieFromAction2(url=url, loginInfo=loginInfo)

    # ----------------------------------------------------------------------------------

    @decoInstance.noneRetryAction()
    def getCookieFromAction(self, url: str, loginInfo: dict):
        # IDログイン
        self.loginID.flowLoginID(url=url, loginInfo=loginInfo)

        # Cookieを取得
        cookie = self.getCookie()
        Cookie = self.insertCookieData(cookie=cookie)
        return self.canValueInCookie(cookie=Cookie)

    # ----------------------------------------------------------------------------------
    # いい生活Clickを追加したバージョン

    @decoInstance.noneRetryAction()
    def getCookieFromAction2(self, url: str, loginInfo: dict):
        # サイトにいってClickしてからIDログイン
        self.loginID.actionBeforeLogin(url=url, loginInfo=loginInfo)

        # Cookieを取得
        cookie = self.getCookie()
        Cookie = self.insertCookieData(cookie=cookie)
        return self.canValueInCookie(cookie=Cookie)

    # ----------------------------------------------------------------------------------

    # ④
    # Cookieがちゃんと取得できてるかどうかを確認
    # リトライ実施

    @decoInstance.funcBase
    def getCookie(self):
        cookies = self._getCookies()
        self.logger.debug(f"cookies: {cookies}")
        cookie = cookies[0]
        if cookie:
            return cookie
        else:
            return None

    # ----------------------------------------------------------------------------------

    def _getCookies(self):
        return self.chrome.get_cookies()

    # ----------------------------------------------------------------------------------
    # # ⑤
    # Cookieの値が入っているか確認

    @decoInstance.funcBase
    def canValueInCookie(self, cookie: dict):
        if not cookie.get("name") or not cookie.get("value"):
            self.logger.warning(f"cookieに必要な情報が記載されてません")
            return None
        else:
            return cookie

    # ----------------------------------------------------------------------------------
    # 有効期限をクリアしたmethod
    # DBよりcookie情報を取得する

    @decoInstance.funcBase
    def insertCookieData(self, cookie):
        cookieName = cookie["name"]
        cookieValue = cookie.get("value")
        cookieDomain = cookie.get("domain")
        cookiePath = cookie.get("path")
        cookieExpires = cookie.get("expiry")
        cookieMaxAge = cookie.get(
            "max-age"
        )  # expiresよりも優先される、〇〇秒間、持たせる権限
        cookieCreateTime = int(time.time())

        # 値をtuple化
        values = (
            cookieName,
            cookieValue,
            cookieDomain,
            cookiePath,
            cookieExpires,
            cookieMaxAge,
            cookieCreateTime,
        )

        # データを入れ込む
        self.sqlite.insertData(
            tableName=self.tableName, col=self.columnsName, values=values
        )
        return cookie

    # ----------------------------------------------------------------------------------
    # SQLiteからcookieを復元

    @decoInstance.funcBase
    def cookieMakeAgain(self):
        cookieAllData = self.sqlite.getColMaxValueRow(
            tableName=self.tableName, primaryKey=self.primaryKey
        )
        cookieData = cookieAllData[0]

        if cookieAllData:
            cookie = {
                "name": cookieData[1],
                "value": cookieData[2],
                "domain": cookieData[3],
                "path": cookieData[4],
            }

            if cookieData[6]:
                cookie["expiry"] = self.currentTime + cookieData[6]
            elif cookieData[5]:
                cookie["expiry"] = cookieData[5]
            self.logger.debug(f"cookie:\n{cookie}")

            return cookie

    # ----------------------------------------------------------------------------------
    # # SQLiteにCookieのデータから有効期限を確認する

    #     @decoInstance.funcBase
    #     def checkCookieLimit(self):
    #         cookieAllData = self.sqlite.getColMaxValueRow(tableName=self.tableName, primaryKey=self.primaryKey)

    #         if cookieAllData:
    #             cookieData = cookieAllData[0]
    #             expiresValue = cookieData[5]   # タプルの場合には数値で拾う
    #             maxAgeValue = cookieData[6]
    #             createTimeValue = cookieData[7]

    #             if maxAgeValue:
    #                 return self._getMaxAgeLimit(maxAgeValue=maxAgeValue, createTimeValue=createTimeValue)

    #             elif expiresValue:
    #                 return self._getExpiresLimit(expiresValue=expiresValue)

    #             else:
    #                 self.logger.warning("Cookieの有効期限が設定されてません")
    #                 return None

    #         else:
    #             self.logger.error(f"cookieが存在しません: {cookieData}")
    #             return None

    # ----------------------------------------------------------------------------------
    # max-ageの時間の有効性を確認する

    @decoInstance.funcBase
    def _getMaxAgeLimit(
        self, maxAgeValue: int, createTimeValue: int, url: str, loginInfo: dict
    ):
        limitTime = maxAgeValue + createTimeValue

        if self.currentTime < limitTime:
            self.logger.info("cookieが有効: 既存のCookieを使ってログインを行います")
            return self.cookieMakeAgain()
        else:
            self.logger.error(
                "有効期限切れのcookie: 既存のCookieを消去して再度IDログイン実施"
            )
            return self.getCookieFromAction2(url=url, loginInfo=loginInfo)

    # ----------------------------------------------------------------------------------
    # expiresの時間の有効性を確認する

    @decoInstance.funcBase
    def _getExpiresLimit(self, expiresValue: int, url: str, loginInfo: dict):
        if self.currentTime < expiresValue:
            self.logger.info("cookieが有効: 既存のCookieを使ってログインを行います")
            return self.cookieMakeAgain()
        else:
            self.logger.error(
                "有効期限切れのcookie: 既存のCookieを消去して再度IDログイン実施"
            )
            return self.getCookieFromAction2(url=url, loginInfo=loginInfo)


# ----------------------------------------------------------------------------------
