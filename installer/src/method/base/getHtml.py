#  coding: utf-8
# 2024/7/9 更新
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import

import requests
from bs4 import BeautifulSoup

from const_str import FileName

# 自作モジュール
from .utils import Logger


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************


class GetHtml:
    def __init__(self):

        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

    # ----------------------------------------------------------------------------------
    # htmlを取得する

    def get_html(self, url: str):
        try:
            self.logger.info(f"******** get_html start ********")

            self.logger.debug(f"url: {url}")

            if url:
                response = requests.get(url)

                if response.status_code == 200:

                    # htmlソースを取得
                    html_content = response.text
                    self.logger.info(f"html_content:\n{html_content[:20]}")
                    self.logger.info(f"******** get_html end ********")

                    return html_content

                elif response.status_code == 404:
                    self.logger.error(f"ページが見つかりません: {url}")
                    raise Exception(f"404 Not Found: {url}")

                elif response.status_code == 500:
                    self.logger.error(f"サーバーエラー: {url}")
                    raise Exception(f"500 Internal Server Error: {url}")

                else:
                    self.logger.error(
                        f"予期しないHTTPステータスコード: {response.status_code} - {response.reason}"
                    )
                    raise Exception(
                        f"HTTPエラー: {response.status_code} - {response.reason}"
                    )

            else:
                self.logger.error(f"urlが存在しない or 無効です{url}")
                raise

        except requests.exceptions.RequestException as e:
            self.logger.error(f"HTTPリクエスト中にエラーが発生しました: {str(e)}")
            raise

    # ----------------------------------------------------------------------------------
    # htmlから残したい部分のみを抽出

    def extracted_html(self, html: str, keep_element: str):
        self.logger.info(f"******** extract_in_html start ********")

        if html and keep_element:
            # htmlを取得して解析する（パース）
            soup = BeautifulSoup(html, "html.parser")

            extracted_element = soup.find(keep_element)

            self.logger.info(f"extracted_element:\n{str(extracted_element)[:100]}")
            self.logger.info(f"******** extract_in_html end ********")

            return str(extracted_element)

        else:
            self.logger.error(f"html_content,elementが無い{html} {keep_element}")
            raise ValueError(f"指定した要素がhtmlの中にない{keep_element}")

    # ----------------------------------------------------------------------------------
    # htmlから特定のものを除去する

    def removed_html(self, html: str, remove_tags_elements: str):
        self.logger.info(f"******** remove_element start ********")

        if html and remove_tags_elements:
            # htmlを取得して解析する（パース）
            soup = BeautifulSoup(html, "html.parser")

            for remove_element in soup.find_all(remove_tags_elements):
                # 除去したい要素を除去を実施
                # 除去を実施されると自動的にsoupを更新する
                remove_element.decompose()

            # 除去された要素のインデントなどを綺麗にしてhtml要素
            # prettify()はインデントをhtml用にきれいにしてくれるメソッド→除去したあとに整理
            removed_html = soup.prettify()
            self.logger.debug(f"removed_html: {removed_html[:20]}")
            self.logger.info(f"******** remove_element end ********")

            return removed_html

        else:
            self.logger.error("htmlまたはremove_tags_elementsが指定されていません")
            raise ValueError("htmlまたはremove_tags_elementsが指定されていません")

    # ----------------------------------------------------------------------------------
    # classの除外リスト取得

    def class_remove_in_html(self, html, remove_class_names: str):
        self.logger.info(f"******** class_remove_in_html start ********")

        if html and remove_class_names:
            # htmlを取得して解析する（パース）
            soup = BeautifulSoup(html, "html.parser")

            for remove_class_name in remove_class_names:
                elements = soup.find_all(class_=remove_class_name)
                for element in elements:
                    self.logger.debug(f"除去される class_element: {element}")
                    element.decompose()

            return str(soup)

        self.logger.info(f"******** class_remove_in_html end ********")

    # ----------------------------------------------------------------------------------
    # 整理されたhtmlを取得

    def organized_html(
        self,
        url: str,
        keep_element: str,
        remove_tags_elements: str,
        remove_class_names: str,
    ):

        self.logger.info(f"******** organized_html start ********")

        # htmlを取得する
        original_html = self.get_html(url=url)

        # htmlから残す部分のみを抽出
        extracted_html = self.extracted_html(
            html=original_html, keep_element=keep_element
        )

        # htmlから特定のタグを除去する
        remove_tags_html = self.removed_html(
            html=extracted_html, remove_tags_elements=remove_tags_elements
        )

        # htmlから特定のclassを除去する
        organized_html = self.class_remove_in_html(
            html=remove_tags_html, remove_class_names=remove_class_names
        )

        self.logger.info(f"******** organized_html end ********")

        return organized_html


# ----------------------------------------------------------------------------------
# **********************************************************************************
