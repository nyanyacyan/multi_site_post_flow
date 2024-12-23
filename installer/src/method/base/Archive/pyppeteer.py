# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import asyncio
from typing import Any, Dict
from datetime import datetime
from pyppeteer import launch
from pyppeteer.errors import TimeoutError
from pyppeteer.page import Page

# 自作モジュール
from .utils import Logger
from .fileWrite import AsyncLimitSabDirFileWrite
from .fileRead import AsyncResultFileRead
from ..const_domain_search import SubDir


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************


class PyppeteerUtils:
    def __init__(self, debugMode=True):

        # logger
        self.getLogger = Logger(
            moduleName=FileName.LOG_FILE_NAME.value, debugMode=debugMode
        )
        self.logger = self.getLogger.getLogger()

        self.currentDate = datetime.now().strftime("%y%m%d")

        self.chrome = None
        self.file_write = AsyncLimitSabDirFileWrite(debugMode=debugMode)
        self.file_read = AsyncResultFileRead(debugMode=debugMode)

    # ----------------------------------------------------------------------------------
    # Chromeブラウザの設定

    async def launch_chrome(self):
        self.chrome = await launch(
            headless=False, slowMo=50  # 各操作に指定したミリ秒の遅延を追加
        )
        return self.chrome

    # ----------------------------------------------------------------------------------
    # 新しくbrowserを立ち上げる

    async def new_page(self):
        # chromeが初期化状態だったら立ち上げる
        if not self.chrome:
            await self.launch_chrome()
        pages = await self.chrome.pages()
        page = pages[0]
        return page

    # ----------------------------------------------------------------------------------

    async def goto_page(self, page: Page, url: str, timeout: int = 10000):
        try:
            await page.goto(url, timeout=timeout, waitUntil="load")
            self.logger.info(f"指定のURLへアクセス:\n{url}")

        except TimeoutError:
            self.logger.error(f"タイムアウト: 指定のURLへアクセス失敗 {url}")

        except Exception as e:
            self.logger.error(f"サイトへアクセス中にエラーが発生: {e}")

    # ----------------------------------------------------------------------------------
    # Clickアクション
    # ? target_selectorは'css' or 'xpath'

    async def click_action(
        self, page: Page, target_selector: str, timeout: int = 20000
    ):
        try:
            # visible=Trueにすることで画面に表示されてることを確認
            await page.waitForSelector(target_selector, visible=True, Timeout=timeout)
            self.logger.debug(f"クリックする要素がClick可能状態")

            # Click実施
            await page.click(target_selector)
            self.logger.debug(f"クリックに成功")

            # Click後のロードが完了してるか確認
            await page.waitForNavigation(waitUntil="load")
            self.logger.debug(f"Click後のロードが完了")

        except TimeoutError:
            self.logger.error(
                f"タイムアウト: 要素が見つからないです。 {target_selector}"
            )

        except Exception as e:
            self.logger.error(f"Clickアクション中ににエラーが発生: {e}")

    # ----------------------------------------------------------------------------------
    # テキストの入力
    # ? target_selectorは'css' or 'xpath'

    async def text_input(self, page: Page, target_selector: str, input_text: Any):
        try:
            await page.waitForSelector(target_selector, visible=True)
            self.logger.debug(f"入力が可能状態")

            await page.type(target_selector, input_text)
            self.logger.debug(f"入力成功")

        except TimeoutError:
            self.logger.error(
                f"タイムアウト: 入力フィールドが見つからないです。 {target_selector}"
            )

    # ----------------------------------------------------------------------------------
    # 現在のURLを取得

    async def _get_current_url(self, page: Page):
        return page.url

    # ----------------------------------------------------------------------------------
    # 同じbrowser内で新しいタブを作成

    async def new_tab_page(self):
        newPage = await self.chrome.newPage()
        return newPage

    # ----------------------------------------------------------------------------------
    # Chromeを閉じる

    async def close_browser(self):
        if self.chrome:
            await self.chrome.close()

    # ----------------------------------------------------------------------------------
    # 今あるページの最後に開いた部分にアクセス

    async def access_tab_change(self):
        allPage = await self.chrome.pages()
        last_page = allPage[-1]

        # 指定されたページを全面に持ってくる
        await last_page.bringToFront()
        last_page_title = last_page.title()
        self.logger.info(f"新しいページに切り替えました: {last_page_title}")

    # ----------------------------------------------------------------------------------

    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Cookieを取得して保管

    async def _get_cookie(self, page: Page):
        # cookieを取得
        cookies = await page.cookies
        for cookie in cookies:
            self.logger.info(
                f"クッキー名: {cookie['name']}, 値: {cookie['value']}, ドメイン: {cookie['domain']}"
            )

        self._pickle_write(
            data=cookies, subDirName=SubDir.pickles.value, fileName=self.currentDate
        )
        return cookies

    # ----------------------------------------------------------------------------------
    #! Cookieを使ってログイン

    async def cookie_login(self, page: Page, url: str):
        try:
            await self._get_cookie(page=page)

            new_page = await self.new_page()

            cookies = await self._pickle_read()

            await page.setCookie(*cookies)

            await self.goto_page(page=new_page, url=url)

            await self.access_tab_change()

        except Exception as e:
            self.logger.error(f"Cookieログイン中にエラーが発生: {e}")

    # ----------------------------------------------------------------------------------

    def _pickle_write(self, data: Any, subDirName: str, fileName: str):
        self.file_write.asyncWriteSabDirToPickle(
            data=data, subDirName=subDirName, fileName=fileName
        )

    # ----------------------------------------------------------------------------------

    def _pickle_read(self):
        return self.file_read.asyncWriteSabDirToPickle()


# ----------------------------------------------------------------------------------
# TODO　db用のCookieログインを作成


# ----------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------
