# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# export PYTHONPATH="/Users/nyanyacyan/Desktop/project_file/multi_site_post_flow/installer/src"

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import base64, cv2, re
from pytesseract import image_to_string

# 自作モジュール
# from base.utils import Logger
from base.chrome import ChromeManager
from base.loginWithId import SingleSiteIDLogin
from base.seleniumBase import SeleniumBasicOperations
from base.elementManager import ElementManager
from base.time_manager import TimeManager

# const


# ----------------------------------------------------------------------------------
# **********************************************************************************
# 一連の流れ


class TestFlow:
    def __init__(self):
        # logger
        # self.getLogger = Logger()
        # self.logger = self.getLogger.getLogger()

        # chrome
        self.chromeManager = ChromeManager()
        self.chrome = self.chromeManager.flowSetupChrome()

        # インスタンス
        self.login = SingleSiteIDLogin(chrome=self.chrome)
        self.random_sleep = SeleniumBasicOperations(chrome=self.chrome)
        self.element = ElementManager(chrome=self.chrome)
        self.time_manager = TimeManager()
        self.selenium = SeleniumBasicOperations(chrome=self.chrome)
        # self.path = BaseToPath()

    ####################################################################################


    def _test_photo_data(self, url: str):
        # ページを開く
        self.chrome.get(url)

        # Canvas要素を取得
        canvas = self.element.getElement(by='id', value="price-7550")

        # JavaScriptを使用してCanvasの内容をBase64データとして取得
        image_data = self.chrome.execute_script("""
            const canvas = arguments[0];
            return canvas.toDataURL('image/png');
        """, canvas)

        # "data:image/png;base64," の部分を削除
        image_data = image_data.split(",")[1]

        # Base64データを画像ファイルとして保存
        image_data_name = "canvas_image.png"
        with open(image_data_name, "wb") as image_file:
            image_file.write(base64.b64decode(image_data))

        print(f"画像が保存されました: {image_data_name}")

        # 画像をOpenCVで読み込み
        image = cv2.imread(image_data_name)

        # グレースケール化
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # ヒストグラム均等化でコントラストを改善
        equalized_image = cv2.equalizeHist(gray_image)

        # 適応的二値化で文字を強調
        binary_image = cv2.adaptiveThreshold(
            equalized_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )

        # ノイズ除去
        processed_image = cv2.GaussianBlur(binary_image, (5, 5), 0)

        # 加工後の画像を保存（デバッグ用）
        processed_image_name = "processed_image.png"
        cv2.imwrite(processed_image_name, processed_image)
        print(f"加工後の画像を保存しました: {processed_image_name}")

        # Tesseract OCRのカスタム設定
        custom_config = r'--oem 3 --psm 7'  # LSTMエンジンを使用し、1行テキスト用に設定

        # OCRでテキストを抽出
        extracted_text = image_to_string(processed_image, config=custom_config, lang="eng")
        print(f"OCRで抽出されたテキスト: {extracted_text}")

        # 正規表現で数字部分を抽出
        match = re.search(r"(\d{1,3}(,\d{3})*)", extracted_text)
        if match:
            price = match.group(1)
            print(f"抽出された価格: {price}")
        else:
            print("価格情報が見つかりませんでした")


if __name__ == '__main__':

    url = "https://www.1-chome.com/elec"
    test_flow = TestFlow()
    test_flow._test_photo_data(url=url)
