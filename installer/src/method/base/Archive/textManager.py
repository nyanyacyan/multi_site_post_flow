# coding: utf-8
# ----------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------
# import
from typing import List


# 自作モジュール
from ..utils import Logger

# **********************************************************************************


class TextManager:
    def __init__(self):
        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

    # ----------------------------------------------------------------------------------
    # 大元のリストからNGWordを除外したリストを作成

    def filterWords(self, textList: list, ngWords: list):
        self.logger.warning(f"\ntextList: {textList}\nngWords: {ngWords}")
        self.logger.warning(f"\ntextList: {len(textList)}\nngWords: {len(ngWords)}")
        self.logger.warning(
            f"\ntextListType: {type(textList)}\nngWordsType: {type(ngWords)}"
        )

        if (
            isinstance(textList, list)
            and len(textList) == 1
            or isinstance(textList, str)
        ):
            self.logger.info(f"textListが {len(textList)} つしかないためリスト編集実施")
            textList = textList.split("，")

        textList = [word.strip() for word in textList]
        ngWords = [word.strip() for word in ngWords]

        self.logger.warning(f"\ntextList: {textList}\nngWords: {ngWords}")
        self.logger.warning(f"\ntextList: {len(textList)}\nngWords: {len(ngWords)}")
        self.logger.warning(
            f"\ntextListType: {type(textList)}\nngWordsType: {type(ngWords)}"
        )

        self.logger.warning(f"textList: {textList[0]}\n\nngWords: {ngWords[0]}")

        filterWords = [word for word in textList if word not in ngWords]
        self.logger.warning(f"filterWords: {filterWords}")
        return filterWords

    # ----------------------------------------------------------------------------------
    # テキストを複数結合させる(Noneは除外する)

    def textJoin(self, joinWordsList: list, joint: str = ""):
        result = filter(None, joinWordsList)
        return joint.join(result)

    # ----------------------------------------------------------------------------------
    # リストの最初にテキストを追加

    def addListFirstLast(self, lst: List, firstWord: str, lastWord: str):
        lst.insert(0, firstWord)
        lst.append(lastWord)
        return lst


# ----------------------------------------------------------------------------------
