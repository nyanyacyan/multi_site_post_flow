# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# export PYTHONPATH="/Users/nyanyacyan/Desktop/project_file/multi_site_post_flow/installer/src"

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import base64, cv2, re
import numpy as np
from pytesseract import image_to_string
from selenium.webdriver.remote.webelement import WebElement

# 自作モジュール
from base.utils import Logger
from method.base.path import BaseToPath
from base.chrome import ChromeManager
from base.loginWithId import SingleSiteIDLogin
from base.seleniumBase import SeleniumBasicOperations
from base.elementManager import ElementManager
from base.time_manager import TimeManager

# const


# ----------------------------------------------------------------------------------
# **********************************************************************************
# 一連の流れ


class CanvasImageAnalysis:
    def __init__(self):
        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

        # chrome
        self.chromeManager = ChromeManager()
        self.chrome = self.chromeManager.flowSetupChrome()

        # インスタンス
        self.login = SingleSiteIDLogin(chrome=self.chrome)
        self.random_sleep = SeleniumBasicOperations(chrome=self.chrome)
        self.element = ElementManager(chrome=self.chrome)
        self.time_manager = TimeManager()
        self.selenium = SeleniumBasicOperations(chrome=self.chrome)
        self.path = BaseToPath()

    ####################################################################################
    # 1行のみあるtext画像のOCR抽出(canvas画像)

    def flow_process(self, by: str, value: str):
        # canvas素材の取得
        canvas_element = self._get_canvas_element(by=by, value=value)

        # canvasデータから画像データを抽出
        base64_data_base = self._get_js_base64_to_canvas(canvas_element=canvas_element)

        # OpenCVで読み込むためにBase64にてデコードして保存
        base64_image_path = self._decoding_white(base64_data_base=base64_data_base)

        # OpenCVで読み込むためにBase64にてデコードして保存
        image = self._open_image_openCV(file_path=base64_image_path)

        # 画像をOCRが読み込みしやすくするための設定
        clean_image = self._clean_image_for_ocr(image=image)

        # 読み込みやすく編集したデータを保存
        self._clean_image_keep(image=clean_image)

        # OCRでテキストを抽出
        extracted_text = self._OCR_text_one_row(clean_image=clean_image)

        # 正規表現で数字部分を抽出
        price = self._extract_regular_num(extracted_text=extracted_text)

        return price

    # ----------------------------------------------------------------------------------
    # canvas素材の取得

    def _get_canvas_element(self, by: str, value: str):
        canvas_element = self.element.getElement(by=by, value=value)
        self.logger.debug(f'canvas_element: {canvas_element}')
        return canvas_element

    # ----------------------------------------------------------------------------------
    # canvasデータから画像データを抽出

    def _get_js_base64_to_canvas(self, canvas_element: WebElement):
        base64_data_base = self.chrome.execute_script("""
            const canvas = arguments[0];
            return canvas.toDataURL('image/png');
        """, canvas_element)

        # 元データ（Base64データ）の例 data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...
        self.logger.debug(f'base64_data_base: {base64_data_base}')

        # 2つ目のデータがイメージデータ
        image_data = base64_data_base.split(",")[1]
        self.logger.debug(f'image_data: {image_data}')

        return base64_data_base

    # ----------------------------------------------------------------------------------
    # OpenCVで読み込むためにBase64にてデコードして保存

    def _decoding_white(self, image_data_name: str, base64_data_base: str):
        base64_image_path = self._get_image_path(fileName=image_data_name)
        self.logger.debug(f'image_data_name: {image_data_name}\nimage_data_name: {image_data_name}')

        with open(base64_image_path, "wb") as image_file:
            image_file.write(base64.b64decode(base64_data_base))

        return base64_image_path

    # ----------------------------------------------------------------------------------
    # Input > File

    def _get_image_path(self, fileName: str):
        file_path = self.path.getInputDataFilePath(fileName=fileName)
        self.logger.debug(f'file_path: {file_path}')
        return file_path

    # ----------------------------------------------------------------------------------
    # 画像をOpenCVで読み込み

    def _open_image_openCV(self, file_path: str):
        image = cv2.imread(file_path)
        self.logger.debug(f'image: {image}')
        return image

    # ----------------------------------------------------------------------------------
    # 画像のデバッグ

    def _debug_image_openCV(self, image: np.ndarray):
        if image is None:
            self.logger.error(f"imageデータがありません: {image}")
            return None

        # 画像をログに出すのではなく、ウィンドウで表示
        cv2.imshow('確認用', image)
        cv2.waitKey(0)  # キー入力があるまで待機
        cv2.destroyAllWindows()  # Windowを閉じる

        return image

    # ----------------------------------------------------------------------------------
    # 画像をOCRが読み込みしやすくするための設定

    def _clean_image_for_ocr(self, image: np.ndarray):
        # グレースケール化
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        self._debug_image_openCV(image=gray_image)

        # ヒストグラム均等化でコントラストを改善
        equalized_image = cv2.equalizeHist(gray_image)
        self._debug_image_openCV(image=equalized_image)

        # 適応的二値化で文字を強調
        binary_image = cv2.adaptiveThreshold(
            equalized_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        self._debug_image_openCV(image=binary_image)

        # ノイズ除去
        clean_image = cv2.GaussianBlur(binary_image, (5, 5), 0)
        self._debug_image_openCV(image=clean_image)

        return clean_image

    # ----------------------------------------------------------------------------------
    # 読み込みやすく編集したデータを保存

    def _clean_image_keep(self, image: np.ndarray):
        image_name = "analyze_image.png"
        image_file_path = self._get_image_path(fileName=image_name)
        cv2.imwrite(image_file_path, image)
        self.logger.info(f'編集したデータの書込成功: {image_file_path}')
        return image_file_path

    # ----------------------------------------------------------------------------------
    # OCRでテキストを抽出

    def _OCR_text_one_row(self, clean_image: np.ndarray):
        # Tesseract OCRのカスタム設定
        custom_config = r'--oem 3 --psm 7'  # LSTMエンジンを使用し、1行テキスト用に設定

        # OCRでテキストを抽出
        extracted_text = image_to_string(clean_image, config=custom_config, lang="eng")
        self.logger.info(f"OCRで抽出されたテキスト: {extracted_text}")

        return extracted_text

    # ----------------------------------------------------------------------------------
    # 正規表現で数字部分を抽出

    def _extract_regular_num(self, extracted_text: str):
        # \d{1,3} == 1〜3桁の数字（100, 250, 999など）
        # (,\d{3})* == カンマ+3桁の数字を繰り返し（,000 / ,500 / ,000 など）
        match = re.search(r"(\d{1,3}(,\d{3})*)", extracted_text)
        if match:
            price = match.group(1)  # 見つけたものを選択（1つ目のものを選択）
            self.logger.info(f"抽出された価格: {price}")
            return price
        else:
            print("価格情報が見つかりませんでした")

    # ----------------------------------------------------------------------------------
