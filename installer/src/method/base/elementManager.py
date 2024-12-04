# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from datetime import datetime
from typing import Dict, Any, List, Tuple
from selenium.common.exceptions import ElementClickInterceptedException

# 自作モジュール
from .utils import Logger
from ..const_domain_search import NGWordList, Address
from .decorators import Decorators
from .textManager import TextManager
from .driverDeco import ClickDeco


decoInstance = Decorators(debugMode=True)


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************


class ElementManager:
    def __init__(self, chrome: WebDriver, debugMode=True):
        # logger
        self.getLogger = Logger(__name__, debugMode=debugMode)
        self.logger = self.getLogger.getLogger()

        self.chrome = chrome
        self.currentDate = datetime.now().strftime('%y%m%d_%H%M%S')
        self.textManager = TextManager(debugMode=debugMode)
        self.clickWait = ClickDeco(debugMode=debugMode)



# ----------------------------------------------------------------------------------


    def getElement(self, value: str, by: str = 'xpath'):
        self.clickWait.jsPageChecker(chrome=self.chrome)
        if by == "id":
            return self.chrome.find_element_by_id(value)
        elif by == "css":
            return self.chrome.find_element_by_css_selector(value)
        elif by == "xpath":
            return self.chrome.find_element_by_xpath(value)
        elif by == "tag":
            return self.chrome.find_element_by_tag_name(value)
        elif by == "link":
            return self.chrome.find_element_by_link_text(value)
        elif by == "name":
            return self.chrome.find_element_by_name(value)
        elif by == "class":
            return self.chrome.find_element_by_class_name(value)
        else:
            raise ValueError("定義してるもの以外のものを指定してます")


# ----------------------------------------------------------------------------------
# 複数

    def getElements(self, value: str, by: str = 'xpath'):
        self.clickWait.jsPageChecker(chrome=self.chrome)
        if by == "id":
            return self.chrome.find_elements_by_id(value)
        elif by == "css":
            return self.chrome.find_elements_by_css_selector(value)
        elif by == "xpath":
            return self.chrome.find_elements_by_xpath(value)
        elif by == "tag":
            return self.chrome.find_elements_by_tag_name(value)
        elif by == "link":
            return self.chrome.find_elements_by_link_text(value)
        elif by == "name":
            return self.chrome.find_elements_by_name(value)
        elif by == "class":
            return self.chrome.find_elements_by_class_name(value)
        else:
            raise ValueError("定義してるもの以外のものを指定してます")


# ----------------------------------------------------------------------------------
# 要素を絞り込み

    def filterElement(self, parentElement: str, value: str, by: str = 'xpath'):
        self.clickWait.jsPageChecker(chrome=self.chrome)

        if by == "id":
            return parentElement.find_element_by_id(value)
        elif by == "css":
            return parentElement.find_element_by_css_selector(value)
        elif by == "xpath":
            return parentElement.find_element_by_xpath(value)
        elif by == "tag":
            return parentElement.find_element_by_tag_name(value)
        elif by == "link":
            return parentElement.find_element_by_link_text(value)
        elif by == "name":
            return parentElement.find_element_by_name(value)
        elif by == "class":
            return parentElement.find_element_by_class_name(value)
        else:
            raise ValueError("定義しているもの以外のものを指定しています")


# ----------------------------------------------------------------------------------
# 親要素から絞り込んで要素を取得

    def _get_sort_element(self, parent_path: str, child_path: str):
        scope_element = self.getElement(value=parent_path)
        child_element = self.filterElement(parentElement=scope_element, value=child_path)
        self.logger.debug(f"\nscope_element: {scope_element}\nchild_element: {child_element}")
        return child_element


# ----------------------------------------------------------------------------------
# 親要素から絞り込んだ要素からtextを取得

    def _get_sort_element_text(self, parent_path: str, child_path: str):
        scope_element = self._get_sort_element(parent_path=parent_path, child_path=child_path)
        text = self._get_text(element=scope_element)
        self.logger.debug(f"\nscope_element: {scope_element}\ntext: {text}")
        return text


# ----------------------------------------------------------------------------------
    @decoInstance.funcBase
    def clickClearInput(self, by: str, value: str, inputText: str):
        self.clickWait.canWaitClick(chrome=self.chrome, by=by, value=value, timeout=3)
        element = self.getElement(by=by, value=value)
        try:
            element.click()
        except ElementClickInterceptedException:
            self.logger.debug(f'popupなどでClickができません: {element}')
            self.chrome.execute_script("arguments[0].click();", element)

        element.clear()
        element.send_keys(inputText)
        self.clickWait.jsPageChecker(chrome=self.chrome)




# ----------------------------------------------------------------------------------


    def clickElement(self, by: str, value: str):
        self.clickWait.canWaitClick(chrome=self.chrome, by=by, value=value, timeout=3)
        element = self.getElement(by=by, value=value)
        try:
            element.click()
        except ElementClickInterceptedException:
            self.logger.debug(f'popupなどでClickができません: {element}')
            self.chrome.execute_script("arguments[0].click();", element)

        self.clickWait.jsPageChecker(chrome=self.chrome)
        return


# ----------------------------------------------------------------------------------
# 絞り込んだ要素にあるテキストを取得

    @decoInstance.funcBase
    def _get_text(self, element: WebElement):
        return element.text.strip()  # 前後の余白を除去


# ----------------------------------------------------------------------------------


    @decoInstance.funcBase
    def getImageUrl(self, by: str, value: str):
        element = self.getElement(by=by, value=value)
        return element.get_attribute("src")


# ----------------------------------------------------------------------------------


    def _getItemsList(self, by: str, value: str):
        itemElements = self.getElement(by=by, value=value)
        itemsText = itemElements.text
        itemsList = itemsText.split(', ')
        return itemsList


# ----------------------------------------------------------------------------------
# NGWordを除外リスト

    def textCleaner(self, textList: List, minLen: int = 12):
        ngWords = NGWordList.ngWords.value
        filterWordsList = self.textManager.filterWords(textList=textList, ngWords=ngWords)

        self.logger.warning(f"filterWordsList: {filterWordsList}\ntextList: {textList}")
        filterWordsListNum = len(filterWordsList)

        print(f"filterWordsListNum: {filterWordsListNum}")
        if minLen >= filterWordsListNum:
            newTextList = textList.split('，')
            print(f"newTextList: {newTextList}")
            return newTextList

        return filterWordsList


# ----------------------------------------------------------------------------------


    def _getAddress(self, by: str, value: str):
        fullAddress = self.getElement(by=by, value=value)
        addressList = Address.addressList.value

        for address in addressList:
            if fullAddress.startswith(address):
                return address


# ----------------------------------------------------------------------------------
# 辞書dataの初期化

    def _initDict(self, name: str):# -> dict[str, dict]:
        return {name: {}}


# ----------------------------------------------------------------------------------
# サブ辞書の中身を入れ込む

    def updateSubDict(self, dictBox: Dict[str, Dict[str, Any]], name: str, inputDict: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        dictBox[name].update(inputDict)
        return dictBox


# ----------------------------------------------------------------------------------
# 特定の値だった場合にNoneを返す

    def _returnNoneIfValue(self, value: Any, ifValueList: List):
        for ifValue in ifValueList:
            if value == ifValue:
                return None
            else:
                return value


# ----------------------------------------------------------------------------------
# 要素を繰り返し取得してリストにする
# conditions=[(by, value), (otherBy, otherValue)]のようにtupleのリストを返す


    def _getElementList(self, conditions: List[Tuple[str, str]], ifValueList: List):
        elementList = []
        for by, value in conditions:
            element = self.getElement(by=by, value=value)
            # 特定のリストは除外する
            element = self._returnNoneIfValue(value=element, ifValueList=ifValueList)
            elementList.append(element)
        return elementList


# ----------------------------------------------------------------------------------
# 広告、検索画面などを検知して消去する

    def closePopup(self, by: str, value: str):
        element = self.clickWait.canWaitClick(chrome=self.chrome, by=by, value=value)
        if element:
            self.clickElement(by=by, value=value)
            self.logger.info(f"不要物を除去: {element}")
        else:
            self.logger.info(f"modalは出力されませんでした。")
            return


# ----------------------------------------------------------------------------------
# クリックした新しいページに切り替え

    def clickMove(self, by: str, value: str):
        self.clickElement(by=by, value=value)
        allHandles = self.chrome.window_handles  # すべてのWindowハンドルを取得
        self.chrome.switch_to.window(allHandles[-1])  # 元々のWindowはallHandles[0]
        return self.logger.info(f"クリックした新しいページタイトル「{self.chrome.title}」")


# ----------------------------------------------------------------------------------


    def unlockDisplayNone(self):
        elements = self._searchDisplayNone
        for element in elements:
            if "display: none" in element.get_attribute("style"):
                self.chrome.execute_script("arguments[0].style.display='block';", element)
                self.logger.info(f"display: noneになってる部分を解除実施: {element}")

            else:
                self.logger.debug(f"display: noneになっている部分はありません")


# ----------------------------------------------------------------------------------


    @property
    def _searchDisplayNone(self):
        return self.getElements(by='xpath', value="//*[contains(@style, 'display: none')]")


# ----------------------------------------------------------------------------------




# ----------------------------------------------------------------------------------
