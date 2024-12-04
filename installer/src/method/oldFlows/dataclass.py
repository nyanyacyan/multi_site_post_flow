# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
from dataclasses import dataclass
from typing import Dict, Any, List, Tuple


# 自作モジュール


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************


@dataclass
class ListPageInfo:
    stationBy: str  # 駅名
    stationValue: str
    trainLineBy: str  # 路線名
    trainLineValue: str
    walkingBy: str  # 徒歩
    walkingValue: str


# **********************************************************************************


@dataclass
class DetailPageInfo:
    nameBy: str  # 物件名
    nameValue: str
    adBy: str  # 広告可否
    adValue: str
    areaBy: str  # 専有面積
    areaValue: str
    itemBy: str  # 設備
    itemValue: str
    addressBy: str  # 都道府県
    addressValue: str
    rentBy: str  # 賃料
    rentValue: str
    managementCostBy: str  # 管理費等
    managementCostValue: str
    depositBy: str  # 管理費等
    depositValue: str
    keyMoneyBy: str  # 管理費等
    keyMoneyValue: str

# **********************************************************************************


@dataclass
class ImageInfo:
    nameBy: str  # 物件名
    nameValue: str
    url: str
    id: str



# **********************************************************************************
