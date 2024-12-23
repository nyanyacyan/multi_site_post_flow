# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import time, os
from selenium.webdriver.chrome.webdriver import WebDriver
from datetime import datetime
from typing import Dict, Any, List
from dotenv import load_dotenv
from pprint import pprint

from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementClickInterceptedException,
)
from selenium.common.exceptions import TimeoutException


# 自作モジュール
from .utils import Logger
from .elementManager import ElementManager
from .AiOrder import ChatGPTOrder
from .textManager import TextManager
from ..dataclass import ListPageInfo, DetailPageInfo
from .SQLite import SQLite
from .decorators import Decorators
from .jumpTargetPage import JumpTargetPage
from ..const import ChatGptPrompt, ChatgptUtils, TableName
from ..constElementInfo import ElementPath, ElementSpecify, ErrorElement
from ..constSqliteTable import TableSchemas

decoInstance = Decorators(debugMode=True)

load_dotenv()

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************


class InsertSql:
    def __init__(self, chrome: WebDriver, debugMode=True):
        # logger
        self.getLogger = Logger(
            moduleName=FileName.LOG_FILE_NAME.value, debugMode=debugMode
        )
        self.logger = self.getLogger.getLogger()

        self.chrome = chrome

        # テーブルName
        self.textTableName = TableName.TEXT.value
        self.imageTableName = TableName.IMAGE.value

        self.currentDate = datetime.now().strftime("%y%m%d_%H%M%S")
        self.element = ElementManager(chrome=self.chrome, debugMode=debugMode)
        self.chatGPT = ChatGPTOrder(debugMode=debugMode)
        self.textManager = TextManager(debugMode=debugMode)
        self.SQLite = SQLite(debugMode=debugMode)
        self.jumpTargetPage = JumpTargetPage(chrome=self.chrome, debugMode=debugMode)

    # ----------------------------------------------------------------------------------
    # flow
    # 一覧の物件リストから詳細ページへ移動して取得する

    @decoInstance.funcBase
    def getListPageInfo(self):

        # ジャンプしてURLへ移動して検索画面を消去まで実施
        self.popupRemove()

        #! テスト中に設定
        maxRetries = 10
        pageCount = 0
        count = 0
        listPageInfoDict = {}

        while pageCount <= maxRetries:
            # 一覧ページにある物件詳細リンクを全て取得
            linkList = self._getLinkList()
            self.logger.warning(
                f"linkList: {linkList}: {len(linkList)}個のリンクを取得"
            )

            # newのカウントを行う
            newElement = self._getClassElementList()
            self.logger.warning(
                f"newElement: {newElement}: {len(newElement)}個の[NEW]の要素を発見"
            )

            #! テスト時はnewElementの要素を制限
            # if len(newElement) > 2:
            #     newElement = newElement[:2]  # 最初の2つの要素のみを使用

            if len(newElement) == 0:
                self.logger.warning(
                    f"処理可能な[NEW]要素が見つからなくなりました。処理を終了します。"
                )
                break

            print(f"newElement: {newElement}\nnewElementの数: {len(newElement)}個")

            for i in range(len(newElement)):
                url = linkList[i].get_attribute("href")
                newText = newElement[i].text
                newTextList = newText.split("\u3000")  # \u3000は全角の空白

                station = newTextList[0] + "駅"
                trainName = newTextList[1]
                walking = newTextList[2]

                stationWord = "  ".join([station, walking])

                count += 1

                listPageInfoDict[count] = {
                    "url": url,
                    "station": station,
                    "walking": walking,
                    "trainName": trainName,
                    "stationWord": stationWord,
                }

                print(f"{count} 個目 listPageInfo: \n{listPageInfoDict[count]}")

                # #! テスト中に設定
                # pageCount += 1

            # ! テスト中はコメントアウト→本番の際には解除
            try:
                # 次へのページをClick
                self.element.clickElement(
                    by="xpath",
                    value='//div[@class="numberArea"]//a[contains(text(), ">")]',
                )
                pageCount += 1

            except NoSuchElementException:
                self.logger.error(
                    f"次のページが見当たらないため処理を終了: {count}目実施"
                )
                break

            except ElementClickInterceptedException:
                self.logger.error(f"再度検索画面が出現。")
                self.popupRemove()
                continue

        print(f"listPageInfo{count}個 全データ:\n{listPageInfoDict}")
        return listPageInfoDict

    # ----------------------------------------------------------------------------------

    async def getDetailPageInfo(self, listPageInfoDict: Dict, delay: int = 2):

        listNum = len(listPageInfoDict)
        print(f"listPageInfoDict: {listPageInfoDict}\nlistNum: {listNum}")
        allTextAndImageDict = {}
        for i in range(1, listNum + 1):  # 最初の引数がstart 2つ目の引数がend
            # サブ辞書からデータ部分を抽出
            listPageInfo = listPageInfoDict[i]

            # 物件詳細リンクにアクセス
            detailPageUrl = listPageInfo["url"]
            self.logger.debug(f"detailPageUrl: {detailPageUrl}")
            self.chrome.get(url=detailPageUrl)
            time.sleep(delay)

            # 詳細からtextデータをスクレイピング
            detailPageInfo = self._getDetailPageData()

            # webElementをtext化
            fixedDetailPageInfo = self.webElementToText(webElementData=detailPageInfo)
            self.logger.warning(f"fixedDetailPageInfo: {fixedDetailPageInfo}")

            # 取得したtextデータをマージ
            textMergeDict = {**listPageInfo, **fixedDetailPageInfo}

            # textデータをSQLiteへ入れ込む
            id = self._textInsertData(mergeDict=textMergeDict)
            self.logger.debug(f"id: {id}")

            # ２〜４枚目に必要なコメントを生成
            updateColumnsData = await self._generateComments(
                id=id, mergeDict=textMergeDict
            )

            # pprint(f"updateColumnsData: {updateColumnsData}")

            # すべてのテキストをマージ
            allTextMergeDict = {**textMergeDict, **updateColumnsData}
            print(
                f"updateColumnsData: {updateColumnsData}\n\nlistPageInfo: {listPageInfo}\n\nallTextMergeDict: {allTextMergeDict}"
            )

            # Sortする
            sortAllTextDict = self._sortOrderDict(
                dataDict=allTextMergeDict, sortOrder=TableSchemas.SORT_TEXT_KEY
            )
            self.logger.warning(f"sortAllTextDict: {sortAllTextDict}")

            # 生成したコメントをSQLiteへ格納（アップデート）
            self._updateDataInSQlite(id=id, updateColumnsData=sortAllTextDict)

            # 詳細ページから画像データを取得
            imageDict = self._mergeImageTableData(id=id, mergeDict=allTextMergeDict)

            # imageデータをSQLiteへ入れ込む
            self._ImageInsertData(imageDict=imageDict)

            # テキストデータと画像データをまとめてサブ辞書として格納
            allTextAndImageDict[i] = {"text": sortAllTextDict, "image": imageDict}

            self.logger.info(f"{i}回目実施完了 {allTextAndImageDict[i]}")

        self.logger.info(f"すべてのデータ\n{allTextAndImageDict}")

        # debug確認
        self.SQLite.getRecordsAllData(tableName=self.textTableName)

        # debug確認
        self.SQLite.getRecordsAllData(tableName=self.imageTableName)

        self.logger.warning(f"allTextAndImageDict:\n{allTextAndImageDict}")
        return allTextAndImageDict

    # ----------------------------------------------------------------------------------
    # webElementのTextを抽出して辞書に組み替える
    # 値がwebElementだったら[element.text]をかける

    def webElementToText(self, webElementData: dict):
        return {
            key: element.text if isinstance(element, WebElement) else element
            for key, element in webElementData.items()
        }

    # ----------------------------------------------------------------------------------
    # 2つの辞書データをマージさせる

    def _mergeImageTableData(self, id: int, mergeDict: Dict):
        dataInMergeDict = self._getImageTableToColInMergeData(
            id=id, mergeDict=mergeDict
        )
        self.logger.info(f"imageDataにて使うデータ: {dataInMergeDict}")

        imageDict = self._imagesDict()

        return {**dataInMergeDict, **imageDict}

    # ----------------------------------------------------------------------------------
    # mergeDataに有るImageDataに必要データを取得

    def _getImageTableToColInMergeData(self, id: int, mergeDict: Dict):
        self.logger.debug(f"mergeDict: {mergeDict}\nid: {id}")

        name = mergeDict["name"]
        createTime = mergeDict["createTime"]
        url = mergeDict["url"]

        return {"id": id, "name": name, "createTime": createTime, "url": url}

    # ----------------------------------------------------------------------------------

    def _imagesDict(self):
        # display: noneがあったら解除
        self.element.unlockDisplayNone()

        imageElements = self._getImageList()
        self.logger.info(f"imageElements: {imageElements}")

        imageData = {}
        titleCount = {}
        for element in imageElements:
            imageUrl = element.get_attribute("href")
            self.logger.debug(f"imageUrl: {imageUrl}")

            try:
                # 要素を絞り込み
                imageTag = self.element.filterElement(
                    parentElement=element, by="tag", value="img"
                )
            except NoSuchElementException:
                self.logger.warning(f"<img>タグが見つかりませんでした: {element}")
                continue

            self.logger.info(f"imageTag: {imageTag}")

            imageTitle = imageTag.get_attribute("title") or imageTag.get_attribute(
                "alt"
            )
            self.logger.debug(f"imageTitle: {imageTitle}")

            # 同じtitleがあるかを検知
            if imageTitle in imageData:
                if imageTitle in titleCount:
                    titleCount[imageTitle] += 1
                else:
                    titleCount[imageTitle] = 1  # titleCountに入ってなかったら初期値設定
                # 重複していたらユニーク数を追記
                imageTitle = f"{imageTitle}_{titleCount[imageTitle]}"

            imageData[imageTitle] = imageUrl

        print(f"imageData: {imageData}")

        sortedImageData = self._sortOrderDict(
            dataDict=imageData, sortOrder=TableSchemas.SORT_IMAGE_KEY
        )

        self.logger.warning(f"Sortが完了してるimageData:\n{sortedImageData}")

        # image.key()は辞書のKeyオブジェクトを返すためListに変換する必要あり
        imageKeys = list(imageData.keys())
        self.logger.warning(f"imageDataのKey一覧:\n{imageKeys}")

        return sortedImageData

    # ----------------------------------------------------------------------------------
    # すべての画像データを取得する

    def _sortOrderDict(self, dataDict: Dict, sortOrder: List):
        sortedDict = {k: dataDict[k] for k in sortOrder if k in dataDict}
        self.logger.info(f"sortedDict: {sortedDict}")
        return sortedDict

    # ----------------------------------------------------------------------------------
    # すべての画像データを取得する

    def _getImageList(self):
        return self.element.getElements(
            by="xpath", value="//div[@id='box_main_gallery']//li//a"
        )

    # ----------------------------------------------------------------------------------
    # 特定のクラスの要素をすべて取得する

    def _getClassElementList(self):
        return self.element.getElements(by="class", value="new")

    # ----------------------------------------------------------------------------------
    # 一覧ページからすべてのリンクを取得してリストにする

    @decoInstance.funcBase
    def _getLinkList(self):
        linkList = self.element.getElements(
            by="xpath", value="//a[contains(text(), '物件画像')]"
        )
        return linkList

    # ----------------------------------------------------------------------------------
    # 入力を実行。入力先のIDを返す

    @decoInstance.funcBase
    def _textInsertData(self, mergeDict: Dict):
        self.SQLite.checkTableExists()

        id = self.SQLite.insertDictData(
            tableName=self.textTableName, inputDict=mergeDict
        )
        return id

    # ----------------------------------------------------------------------------------
    # 入力を実行。入力先のIDを返す

    @decoInstance.funcBase
    def _ImageInsertData(self, imageDict: Dict):
        id = self.SQLite.insertDictData(
            tableName=self.imageTableName, inputDict=imageDict
        )
        return id

    # ----------------------------------------------------------------------------------
    # # 指定のIDのcolumnを指定してアップデートする

    @decoInstance.funcBase
    def _updateDataInSQlite(self, id: int, updateColumnsData: Dict):
        # self.SQLite.checkTableExists()

        self.SQLite.updateData(
            tableName=self.textTableName, updateColumnsData=updateColumnsData, rowId=id
        )
        return id

    # ----------------------------------------------------------------------------------
    # tableValueは一覧の中の何個目かどうか

    @decoInstance.funcBase
    def _getListPageData(self, tableValue: Any):
        listPageInfo = self._listPageInfo(tableValue=tableValue)
        return listPageInfo

    # ----------------------------------------------------------------------------------

    @decoInstance.funcBase
    def _getDetailPageData(self):
        metaInfo = self._metaInfo()
        detailPageInfo = self._detailPageInfo()
        return {**metaInfo, **detailPageInfo}

    # ----------------------------------------------------------------------------------

    @decoInstance.funcBase
    async def _generateComments(self, id: int, mergeDict: Dict):
        # 2ページ目のコメント
        secondComment = self.createSecondPageComment(mergeDict=mergeDict)

        selectItems = self.element.textCleaner(textList=mergeDict["item"])

        # 3ページ目のコメント
        thirdComment = await self.chatGPTComment(
            selectItems=selectItems, itemStartValue=4, maxlen=100
        )

        # 4ページ目のコメント
        fourthComment = await self.chatGPTComment(
            selectItems=selectItems, itemStartValue=8, maxlen=100
        )

        return {
            "id": id,
            "secondComment": secondComment,
            "thirdComment": thirdComment,
            "fourthComment": fourthComment,
            "selectItems": selectItems,
        }

    # ----------------------------------------------------------------------------------

    @decoInstance.retryAction
    def _navigateToTargetPage(self, delay: int):

        # self.jumpTargetPage.flowJumpTargetPage(targetUrl=targetUrl)
        # time.sleep(delay)

        # 念の為、Refresh
        self.chrome.refresh()
        time.sleep(delay)

        # 検索画面を消去
        self.element.clickElement(
            by=ElementSpecify.XPATH.value,
            value=ElementPath.SEARCH_DELETE_BTN_PATH.value,
        )
        time.sleep(delay)
        self.logger.debug(f"新しいページに移動後、Refresh完了")

    # ----------------------------------------------------------------------------------

    def popupRemove(self, delay: int = 2):
        try:
            while True:
                # self.chrome.refresh()
                # time.sleep(delay)

                # 検索画面を消去
                popupElement = self.element.clickElement(
                    by=ElementSpecify.XPATH.value,
                    value=ElementPath.SEARCH_DELETE_BTN_PATH.value,
                )
                # エラーが起きる可能性があるため検知しやすくするためスリープ
                time.sleep(delay)

                if not popupElement:
                    self.logger.info(f"除去完了")
                    return True

                self.logger.info(f"除去が終わってません。再試行")

        # 別のページが開いてる
        except TimeoutException:
            self.errorPageDetect(
                by=ErrorElement.ERROR_PAGE_BY.value,
                value=ErrorElement.ERROR_CLICK_BY.value,
                errorPageActionFunc=lambda: self.element.clickElement(
                    by=ErrorElement.ERROR_CLICK_BY.value,
                    value=ErrorElement.ERROR_CLICK_VALUE.value,
                ),
            )

    # ----------------------------------------------------------------------------------

    def errorPageDetect(
        self, by: str, value: str, errorMessage: str, errorPageActionFunc
    ):
        self.logger.warning(f"エラーページが表示されている可能性があります。")

        errorElement = self.element.getElement(by=by, value=value)
        if errorMessage in errorElement:
            self.logger.warning(f"エラーページを検知しました。")

            errorPageActionFunc()

    # ----------------------------------------------------------------------------------
    # ChatGPTのコメント生成

    @decoInstance.funcBase
    async def chatGPTComment(self, selectItems: List, itemStartValue: int, maxlen: int):
        prompt = self.ChatGPTPromptCreate(
            selectItems=selectItems, itemStartValue=itemStartValue, maxlen=maxlen
        )
        result = await self.chatGPT.resultOutput(
            prompt=prompt,
            fixedPrompt=ChatGptPrompt.fixedPrompt.value,
            endpointUrl=ChatgptUtils.endpointUrl.value,
            model=ChatgptUtils.model.value,
            apiKey=os.getenv("CHATGPT_APIKEY"),
            maxlen=maxlen,
            maxTokens=ChatgptUtils.MaxToken.value,
        )
        self.logger.info(f"コメント: {result}")
        self.logger.info(
            f"コメント文字数（文字制限:{maxlen}文字まで）: {len(result)}文字"
        )
        return result

    # ----------------------------------------------------------------------------------
    # Prompt生成
    # 文字数制限はここで入力

    @decoInstance.funcBase
    def ChatGPTPromptCreate(self, selectItems: List, itemStartValue: int, maxlen: int):
        # items = self.element.textCleaner(textList=mergeDict['item'])

        self.logger.info(f"selectItems: {selectItems}")

        def getItemOrDefault(index: int, default: str = "なし"):
            """指定したインデックスのアイテムを取得、なければデフォルト値を返す"""
            return selectItems[index] if index < len(selectItems) else default

        prompt = ChatGptPrompt.recommend.value.format(
            maxlen=maxlen,
            minLen=maxlen - 20,
            item0=getItemOrDefault(itemStartValue),
            item1=getItemOrDefault(itemStartValue + 1),
            item2=getItemOrDefault(itemStartValue + 2),
            item3=getItemOrDefault(itemStartValue + 3),
        )

        self.logger.info(f"prompt: {prompt}")

        return prompt

    # ----------------------------------------------------------------------------------
    # 2ページ目のコメント作成

    @decoInstance.funcBase
    def createSecondPageComment(self, mergeDict: str):
        # 2枚目コメント→つなぎ合わせたもの
        result = self.SQLite.getSortColOneData(
            tableName=self.textTableName,
            primaryKeyCol="name",
            sortCol="createTime",
            primaryKeyColValue=mergeDict.get("name"),
            cols=["trainName", "station", "walking", "rent", "managementCost"],
        )
        resultDict = dict(result)

        print(f"result: {resultDict}")

        trainName = resultDict.get("trainName", "-")
        station = resultDict.get("station", "-")
        walking = resultDict.get("walking", "-")
        rent = resultDict.get("rent", "-")
        managementCost = resultDict.get("managementCost", "なし")

        rent_int = self._int_to_Str(rent)
        managementCost_int = self._int_to_Str(managementCost)

        commentParts = [
            "今回は",
            f"{trainName} の",
            f"{station} から",
            f"{walking} の物件です。",
            f"賃料は {rent_int} 円",
            f"管理費等は {managementCost_int} 円",
            "紹介するよ！",
        ]

        self.logger.info(f"secondComment:\n{commentParts}")

        secondComment = "\n".join(commentParts)
        return secondComment

    # ----------------------------------------------------------------------------------
    # テキストから数値を抜き出す→円がある場合にはそれまでの数値を抜き出す

    def _int_to_Str(self, strData: str):
        if "円" in strData:
            strData = strData.split("円")[0]

        # 数値になる文字列のみを残す
        filteredStr = "".join(filter(str.isdigit, strData))

        # もし数値になる文字列がなかったら
        if not filteredStr:
            self.logger.error(f"数値ではない文字列を検知しました: {strData}")
            return 0

        number = int(filteredStr)
        self.logger.info(f"文字列から数値に変換: {number}")
        return number

    # ----------------------------------------------------------------------------------
    # 一覧ページから取得
    # tableValueは何個目かどうか

    @decoInstance.funcBase
    def _listPageInfo(self, tableValue: int) -> Dict[str, WebElement]:
        listInstance = self._listPageInfoValue(tableValue)
        return self._getListPageElement(listPageInfo=listInstance)

    # ----------------------------------------------------------------------------------
    # 詳細ページからデータを取得

    @decoInstance.funcBase
    def _detailPageInfo(self) -> Dict[str, WebElement]:
        detailInstance = self._detailPageInfoValue()
        return self._getDetailPageElement(detailPageInfo=detailInstance)

    # ----------------------------------------------------------------------------------

    def _metaInfo(self):
        currentUrl = self.chrome.current_url
        currentDate = self.currentDate

        dataDict = {"url": currentUrl, "createTime": currentDate}
        return dataDict

    # ----------------------------------------------------------------------------------
    # tableValueは何個目かどうか

    def _listPageInfoValue(self, tableValue: int):
        return ListPageInfo(
            stationBy=ElementSpecify.XPATH.value,
            stationValue=ElementPath.STATION_VALUE.value.format(tableValue),
            trainLineBy=ElementSpecify.XPATH.value,
            trainLineValue=ElementPath.TRAIN_LINE.value.format(tableValue),
            walkingBy=ElementSpecify.XPATH.value,
            walkingValue=ElementPath.WAKING.value.format(tableValue),
        )

    # ----------------------------------------------------------------------------------

    def _detailPageInfoValue(self) -> DetailPageInfo:
        return DetailPageInfo(
            nameBy=ElementSpecify.XPATH.value,
            nameValue=ElementPath.NAME.value,
            adBy=ElementSpecify.XPATH.value,
            adValue=ElementPath.AD.value,
            areaBy=ElementSpecify.XPATH.value,
            areaValue=ElementPath.AREA.value,
            itemBy=ElementSpecify.XPATH.value,
            itemValue=ElementPath.ITEM.value,
            addressBy=ElementSpecify.XPATH.value,
            addressValue=ElementPath.ADDRESS.value,
            rentBy=ElementSpecify.XPATH.value,
            rentValue=ElementPath.RENT.value,
            managementCostBy=ElementSpecify.XPATH.value,
            managementCostValue=ElementPath.MANAGEMENT_COST.value,
            depositBy=ElementSpecify.XPATH.value,
            depositValue=ElementPath.DEPOSIT.value,
            keyMoneyBy=ElementSpecify.XPATH.value,
            keyMoneyValue=ElementPath.KEY_MONEY.value,
        )

    # ----------------------------------------------------------------------------------

    @decoInstance.funcBase
    def _getListPageElement(self, listPageInfo: ListPageInfo):
        trainLine = self.element.getElement(
            by=listPageInfo.trainLineBy, value=listPageInfo.trainLineValue
        )
        station = self.element.getElement(
            by=listPageInfo.stationBy, value=listPageInfo.stationValue
        )
        walking = self.element.getElement(
            by=listPageInfo.walkingBy, value=listPageInfo.walkingValue
        )

        dataDict = {
            "trainLine": trainLine,  # 路線名
            "station": station,  # 駅名
            "walking": walking,  # 徒歩
        }

        return dataDict

    # ----------------------------------------------------------------------------------

    @decoInstance.funcBase
    def _getDetailPageElement(
        self, detailPageInfo: DetailPageInfo
    ) -> Dict[str, WebElement]:
        # html = self.chrome.page_source
        # self.logger.info(f"html: \n{html}")

        name = self.element.getElement(
            by=detailPageInfo.nameBy, value=detailPageInfo.nameValue
        )
        ad = self.element.getElement(
            by=detailPageInfo.adBy, value=detailPageInfo.adValue
        )
        area = self.element.getElement(
            by=detailPageInfo.areaBy, value=detailPageInfo.areaValue
        )
        item = self.element.getElement(
            by=detailPageInfo.itemBy, value=detailPageInfo.itemValue
        )
        address = self.element.getElement(
            by=detailPageInfo.addressBy, value=detailPageInfo.addressValue
        )
        rent = self.element.getElement(
            by=detailPageInfo.rentBy, value=detailPageInfo.rentValue
        )
        managementCost = self.element.getElement(
            by=detailPageInfo.managementCostBy, value=detailPageInfo.managementCostValue
        )
        deposit = self.element.getElement(
            by=detailPageInfo.depositBy, value=detailPageInfo.depositValue
        )
        keyMoney = self.element.getElement(
            by=detailPageInfo.keyMoneyBy, value=detailPageInfo.keyMoneyValue
        )

        dataDict = {
            "name": name,  # 物件名
            "ad": ad,  # 広告可否
            "area": area,  # 路線名
            "item": item,  # 駅名
            "address": address,  # 徒歩
            "rent": rent,  # 徒歩
            "managementCost": managementCost,  # 徒歩
            "deposit": deposit,  # 徒歩
            "keyMoney": keyMoney,  # 徒歩
        }

        return dataDict


# ----------------------------------------------------------------------------------
