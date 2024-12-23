# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import os, requests
from PIL import Image, ImageDraw, ImageFont
from typing import Tuple
from io import BytesIO


# 自作モジュール
from .utils import Logger
from .path import BaseToPath
from ..constElementInfo import ImageInfo
from const_str import FileName, Extension


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************


class ImageEditor:
    def __init__(self):
        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

        self.path = BaseToPath()

        self.imageSize = (1080, 1080)

    # ----------------------------------------------------------------------------------

    def executePatternEditors(self, dataDict: dict, buildingName: str):
        patterns = ["A", "B", "C", "D"]

        for pattern in patterns:
            if pattern not in dataDict:
                self.logger.error(
                    f"{pattern} パターンのデータが欠けているため、{pattern} とそれ以降のすべてのパターンをスキップします。"
                )
                break

            # パターン固有のデータを取得
            pattern_data = dataDict[pattern]
            baseImageFileName = ImageInfo.BASE_IMAGE_FILE_NAME.value[pattern]
            baseImagePath = self.inputDataFolderPath(fileName=baseImageFileName)

            fontSize = ImageInfo.FONT_SIZES.value[pattern]
            commentSize = ImageInfo.COMMENT_SIZE.value
            fontFileName = ImageInfo.FONT_NAME.value
            fontPath = self.inputDataFolderPath(fileName=fontFileName)
            fontColor = ImageInfo.FONT_COLORS.value[
                pattern
            ]  # パターンに対応するフォントカラーを取得
            underBottomSize = ImageInfo.UNDER_BOTTOM_SIZE.value
            underBottomColor = ImageInfo.UNDER_BOTTOM_COLOR.value

            # 画像作成メソッドにパターン固有の情報を渡す
            if not self.createImage(
                pattern_data,
                fontPath,
                baseImagePath,
                fontSize,
                commentSize,
                pattern,
                fontColor,
                underBottomSize,
                underBottomColor,
                buildingName,
            ):
                self.logger.error(
                    f"パターン {pattern} の画像データが揃ってないため、以降のパターンをスキップします。"
                )
                break

        self.logger.info(f"画像処理が完了しました。")

    # ----------------------------------------------------------------------------------

    def checkImageAndTextCount(self, data: dict, pattern: str):
        # 必要な項目をパターンごとに定義
        required_keys = {
            "A": ["imagePath_1", "text_1", "text_2", "text_3"],
            "B": ["imagePath_1", "imagePath_2", "text_1", "text_2", "text_3"],
            "C": ["imagePath_1", "imagePath_2", "text_1", "text_2"],
            "D": ["imagePath_1", "imagePath_2", "text_1", "text_2"],
        }

        # 必要なキーが存在し、かつそのキーに値があるかをチェック
        missing_or_empty_keys = [
            key for key in required_keys[pattern] if key not in data or not data[key]
        ]

        if missing_or_empty_keys:
            self.logger.error(
                f"{pattern} に必要なデータが不足しています。欠けているキーまたは空のキー: {missing_or_empty_keys}"
            )
            return False

        # imagePath の有効性をチェック
        image_keys = [key for key in required_keys[pattern] if "imagePath" in key]
        for key in image_keys:
            try:
                response = requests.head(data[key], allow_redirects=True)
                if response.status_code < 200 or response.status_code >= 400:
                    self.logger.error(
                        f"{pattern} の画像が見つかりません: \n{data[key]}"
                    )
                    return False
            except requests.RequestException as e:
                self.logger.error(
                    f"{pattern} の画像データにアクセスできません: \n{data[key]}\nエラー: {e}"
                )
                return False

        return True

    # ----------------------------------------------------------------------------------

    def createImage(
        self,
        data: dict,
        fontPath: str,
        baseImagePath: str,
        fontSize: int,
        commentSize,
        pattern: str,
        fontColor: Tuple[int, int, int],
        underBottomSize: int,
        underBottomColor: Tuple[int, int, int],
        buildingName: str,
    ):
        """
        fontPath→使用したいフォントを指定する
        baseImagePath→ベース画像を指定する
        """
        self.logger.info(
            f"createImage 呼び出し時の {pattern} の data の型: {type(data)}"
        )
        self.logger.info(f"createImage 呼び出し時の {pattern} の data の内容: {data}")

        # 画像データが揃っているかをチェック
        if not self.checkImageAndTextCount(data, pattern):
            return False

        # ベース画像の読み込み
        base_image = Image.open(baseImagePath).resize(self.imageSize).convert("RGBA")

        # 各パターンの配置情報を取得
        positions = ImageInfo.POSITIONS.value[pattern]

        # 画像の配置
        if pattern == "A":
            # Pattern A の場合
            if "imagePath_1" in data:
                # 1. Image1 の配置
                self.drawImageWithMode(
                    base_image, data["imagePath_1"], positions["IMAGE_CENTER"]
                )

            # 2. 半透明のラインの描画（BACK_BOTTOM）
            if "BACK_TOP" in positions:
                back_bottom_box = positions["BACK_TOP"]

                # ライン用の新しい透明なレイヤーを作成
                overlay = Image.new("RGBA", base_image.size, (255, 255, 255, 0))
                overlay_draw = ImageDraw.Draw(overlay)

                # 半透明のラインを描画
                overlay_draw.rectangle(back_bottom_box, fill=(255, 255, 255, 150))

                # ベース画像とラインを合成
                base_image = Image.alpha_composite(base_image, overlay)

            # 2. 半透明のラインの描画（BACK_BOTTOM）
            if "BACK_BOTTOM" in positions:
                back_bottom_box = positions["BACK_BOTTOM"]

                # ライン用の新しい透明なレイヤーを作成
                overlay = Image.new("RGBA", base_image.size, (255, 255, 255, 0))
                overlay_draw = ImageDraw.Draw(overlay)

                # 半透明のラインを描画
                overlay_draw.rectangle(back_bottom_box, fill=(255, 255, 255, 150))

                # ベース画像とラインを合成
                base_image = Image.alpha_composite(base_image, overlay)

            # 3. テキストの配置
            draw = ImageDraw.Draw(base_image)
            font = ImageFont.truetype(str(fontPath), fontSize)

            print(f"font: {font}, type:{type(font)}")

            # テキスト1を右揃えで配置（アウトライン付き）
            if "text_1" in data and "TEXT_LEFT_TOP" in positions:
                self.drawTextWithOutline(
                    draw,
                    data["text_1"],
                    positions["TEXT_LEFT_TOP"],
                    fontPath,
                    initialFontSize=fontSize,
                    lineHeight=fontSize,
                    fill=fontColor,
                    outline_fill=(255, 255, 255),
                    outline_width=2,
                    center=False,
                )

            # テキスト2を枠の中央に配置（アウトライン付き）
            if "text_2" in data and "TEXT_RIGHT_TOP" in positions:
                self.drawTextWithOutline(
                    draw,
                    data["text_2"],
                    positions["TEXT_RIGHT_TOP"],
                    fontPath,
                    initialFontSize=fontSize,
                    lineHeight=fontSize,
                    fill=fontColor,
                    outline_fill=(255, 255, 255),
                    outline_width=2,
                    right=True,
                )

            # テキスト3は通常の横書き（アウトライン付き）
            if "text_3" in data and "TEXT_BOTTOM_LEFT" in positions:
                self.drawTextWithOutline(
                    draw,
                    data["text_3"],
                    positions["TEXT_BOTTOM_LEFT"],
                    fontPath,
                    initialFontSize=fontSize,
                    lineHeight=40,
                    fill=fontColor,
                    outline_fill=(255, 255, 255),
                    outline_width=2,
                )

        # Pattern B の場合
        elif pattern == "B":
            if "imagePath_1" in data:
                self.drawImageWithMode(
                    base_image, data["imagePath_1"], positions["IMAGE_TOP_LEFT"]
                )

            if "imagePath_2" in data:
                self.drawImageWithMode(
                    base_image, data["imagePath_2"], positions["IMAGE_BOTTOM_LEFT"]
                )

            # テキストの配置
            draw = ImageDraw.Draw(base_image)
            if "text_1" in data and "TEXT_TOP_RIGHT" in positions:
                self.drawTextWithOutline(
                    draw,
                    data["text_1"],
                    positions["TEXT_TOP_RIGHT"],
                    fontPath,
                    initialFontSize=fontSize,
                    fill=fontColor,
                    lineHeight=40,
                    outline_fill=(255, 255, 255),
                    outline_width=2,
                )

            if "text_2" in data and "TEXT_BOTTOM_RIGHT" in positions:
                self.drawTextWithOutline(
                    draw,
                    data["text_2"],
                    positions["TEXT_BOTTOM_RIGHT"],
                    fontPath,
                    initialFontSize=fontSize,
                    fill=fontColor,
                    lineHeight=40,
                    outline_fill=(255, 255, 255),
                    outline_width=2,
                    center=True,
                )

            if "text_3" in data and "TEXT_UNDER_BOTTOM" in positions:
                self.drawTextWithOutline(
                    draw,
                    data["text_3"],
                    positions["TEXT_UNDER_BOTTOM"],
                    fontPath,
                    initialFontSize=underBottomSize,
                    fill=underBottomColor,
                    lineHeight=40,
                    outline_fill=(255, 255, 255),
                    outline_width=2,
                )

        else:
            # Pattern C, D の場合
            if "imagePath_1" in data:
                self.drawImageWithMode(
                    base_image, data["imagePath_1"], positions["IMAGE_TOP_LEFT"]
                )

            if "imagePath_2" in data:
                self.drawImageWithMode(
                    base_image, data["imagePath_2"], positions["IMAGE_BOTTOM_LEFT"]
                )

            # テキストの配置
            draw = ImageDraw.Draw(base_image)
            if "text_1" in data and "TEXT_TOP_RIGHT" in positions:
                self.drawTextWithOutline(
                    draw,
                    data["text_1"],
                    positions["TEXT_TOP_RIGHT"],
                    fontPath,
                    initialFontSize=fontSize,
                    fill=fontColor,
                    lineHeight=40,
                    outline_fill=(255, 255, 255),
                    outline_width=2,
                )

            if "text_2" in data and "TEXT_BOTTOM_RIGHT" in positions:
                self.drawTextWithWrapping(
                    draw,
                    data["text_2"],
                    fontPath,
                    positions["TEXT_BOTTOM_RIGHT"],
                    initialFontSize=commentSize,
                    lineHeight=fontSize,
                    fill=fontColor,
                )

            if "text_3" in data and "TEXT_UNDER_BOTTOM" in positions:
                self.drawTextWithOutline(
                    draw,
                    data["text_3"],
                    positions["TEXT_UNDER_BOTTOM"],
                    fontPath,
                    initialFontSize=underBottomSize,
                    fill=underBottomColor,
                    lineHeight=40,
                    outline_fill=(255, 255, 255),
                    outline_width=2,
                )

        # 画像の保存
        extension = Extension.PNG.value
        fileName = f"{buildingName}_{pattern}"
        outputFilePath = self.getResultSubDirFilePath(
            subDirName=buildingName, fileName=fileName, extension=extension
        )
        base_image.save(outputFilePath, format="PNG")
        self.logger.info(f"保存完了: {outputFilePath}")

        return True

    # ----------------------------------------------------------------------------------

    def drawTextWithOutlineRightAligned(
        self,
        draw: ImageDraw.ImageDraw,
        text: str,
        boundingBox: Tuple[int, int, int, int],
        font: ImageFont.FreeTypeFont,
        fill: Tuple[int, int, int],
        outline_fill: Tuple[int, int, int] = (0, 0, 0),
        outline_width: int = 2,
    ):
        """
        テキストを右揃えにしてアウトライン付きで描画します。
        """
        # バウンディングボックスの幅と高さを取得
        box_width = boundingBox[2] - boundingBox[0]
        box_height = boundingBox[3] - boundingBox[1]

        # テキストの幅を取得し、右揃えの位置を計算
        text_width = draw.textlength(text, font=font)
        x = boundingBox[2] - text_width
        y = boundingBox[1]

        # アウトラインの描画
        for offset_x in range(-outline_width, outline_width + 1):
            for offset_y in range(-outline_width, outline_width + 1):
                if offset_x == 0 and offset_y == 0:
                    continue
                draw.text(
                    (x + offset_x, y + offset_y), text, font=font, fill=outline_fill
                )

        # テキスト本体を描画
        draw.text((x, y), text, font=font, fill=fill)

    # ----------------------------------------------------------------------------------

    def drawTextWithOutline(
        self,
        draw: ImageDraw.ImageDraw,
        text: str,
        boundingBox: Tuple[int, int, int, int],
        fontPath: str,
        initialFontSize: int,
        lineHeight: int,
        fill: Tuple[int, int, int] = (0, 0, 0),
        outline_fill: Tuple[int, int, int] = (255, 255, 255),
        outline_width: int = 2,
        center: bool = False,  # 中央揃えオプション
        right: bool = False,  # 右揃えオプション
    ):
        """
        アウトライン付きのテキストを描画し、必要であればフォントサイズを小さくして枠に収まるように調整します。
        """
        # バウンディングボックスの幅と高さを取得
        box_width = boundingBox[2] - boundingBox[0]
        box_height = boundingBox[3] - boundingBox[1]

        # 初期フォントサイズから開始
        font_size = initialFontSize
        font_path_str = str(fontPath)
        font = ImageFont.truetype(font_path_str, font_size)

        # フォントサイズを調整して枠に収める
        while True:
            text_width, text_height = draw.textbbox((0, 0), text, font=font)[2:4]
            if text_width <= box_width and text_height <= box_height:
                break
            font_size -= 2
            if font_size <= 0:  # 最小フォントサイズを超えた場合
                self.logger.error(
                    f"テキスト '{text}' を枠に収めるのに十分なフォントサイズが見つかりません。"
                )
                return
            font = ImageFont.truetype(font_path_str, font_size)

        # 改行を含むテキストを分割
        lines = text.split("\n")

        # 初期位置を設定
        x = boundingBox[0]
        y = boundingBox[1]

        # 中央揃えオプションが有効な場合
        if center:
            # ボックス内で垂直方向に中央揃え
            total_text_height = lineHeight * len(lines)
            y += (box_height - total_text_height) // 2

        # 各行を描画
        for line in lines:
            line_width = draw.textlength(line, font=font)

            # 中央揃えオプションが有効な場合は各行を中央に揃える
            if center:
                x = boundingBox[0] + (box_width - line_width) // 2
            elif right:
                x = boundingBox[2] - line_width

            # アウトラインの描画
            for offset_x in range(-outline_width, outline_width + 1):
                for offset_y in range(-outline_width, outline_width + 1):
                    if offset_x == 0 and offset_y == 0:
                        continue
                    draw.text(
                        (x + offset_x, y + offset_y), line, font=font, fill=outline_fill
                    )

            # テキスト本体を描画
            draw.text((x, y), line, font=font, fill=fill)

            # 次の行のy位置を計算（中央揃えオプションが有効な場合のみ行ごとに）
            y += lineHeight

    # ----------------------------------------------------------------------------------

    def drawTextWithWrapping(
        self,
        draw: ImageDraw.ImageDraw,
        text: str,
        fontPath: str,
        boundingBox: Tuple[int, int, int, int],
        initialFontSize: int,
        lineHeight: int,
        fill: Tuple[int, int, int] = (0, 0, 0),
    ):
        """
        指定されたバウンディングボックス内にテキストを描画し、必要であれば改行します。
        """
        # バウンディングボックスの幅と高さを取得
        box_width = boundingBox[2] - boundingBox[0]
        box_height = boundingBox[3] - boundingBox[1]

        # フォントの生成
        font_size = initialFontSize
        font_path_str = str(fontPath)
        font = ImageFont.truetype(font_path_str, font_size)

        # 初期位置を設定
        x = boundingBox[0]
        y = boundingBox[1]

        # テキスト全体の高さを計算し、枠に収まるようにフォントサイズを調整
        lines = []
        current_line = ""

        print(f"text: {text}")

        for char in text:
            # 1文字ずつ追加して幅を計算
            if draw.textlength(current_line + char, font=font) <= box_width:
                current_line += char
            else:
                # 枠の幅を超える場合は新しい行を追加
                lines.append(current_line)
                current_line = char

        # 最後の行を追加
        if current_line:
            lines.append(current_line)

        # テキストの中央揃えを行うための初期位置の計算（縦方向の中央揃え）
        total_text_height = len(lines) * lineHeight
        y = boundingBox[1] + (box_height - total_text_height) // 2

        # 各行を描画
        for line in lines:
            # 各行を横に中央揃え
            line_width = draw.textlength(line, font=font)
            x = boundingBox[0] + (box_width - line_width) // 2

            draw.text((x, y), line, font=font, fill=fill)
            y += lineHeight

    # ----------------------------------------------------------------------------------

    def drawImageWithMode(
        self,
        baseImage: Image.Image,
        imagePath: str,
        boundingBox: Tuple[
            int, int, int, int
        ],  # 新しいパラメータ、(x1, y1, x2, y2) のタプル
    ):
        # 画像を取得して `insertImage` を定義する
        if imagePath.startswith("http://") or imagePath.startswith("https://"):
            try:
                response = requests.get(imagePath, stream=True)
                response.raise_for_status()
                insertImage = Image.open(BytesIO(response.content)).convert("RGBA")
            except requests.RequestException as e:
                self.logger.error(f"画像の取得に失敗しました: {imagePath}\nエラー: {e}")
                return
        else:
            try:
                insertImage = Image.open(imagePath).convert("RGBA")
            except FileNotFoundError:
                self.log(f"ローカル画像ファイルが見つかりません: {imagePath}")
                return

        # バウンディングボックスの幅と高さを取得
        box_width = boundingBox[2] - boundingBox[0]
        box_height = boundingBox[3] - boundingBox[1]

        # 画像のリサイズ（アスペクト比を保ちながら枠に収める）
        insert_width, insert_height = insertImage.size
        aspect_ratio = insert_width / insert_height

        # ボックスに収まるようにリサイズ
        if (box_width / box_height) > aspect_ratio:
            # ボックスの幅に対して画像が細長い場合
            new_height = box_height
            new_width = int(new_height * aspect_ratio)
        else:
            # ボックスの高さに対して画像が幅広い場合
            new_width = box_width
            new_height = int(new_width / aspect_ratio)

        insertImage = insertImage.resize((new_width, new_height), Image.LANCZOS)

        # 画像を貼り付ける位置を決定する
        x_offset = boundingBox[0] + (box_width - new_width) // 2
        y_offset = boundingBox[1] + (box_height - new_height) // 2

        # 画像の貼り付け
        baseImage.paste(insertImage, (x_offset, y_offset), insertImage)

    # ----------------------------------------------------------------------------------
    # resultOutput

    def getResultSubDirFilePath(self, subDirName: str, fileName: str, extension: str):
        return self.path.getResultSubDirFilePath(subDirName, fileName, extension)

    # ----------------------------------------------------------------------------------

    def inputDataFolderPath(self, fileName: str):
        return self.path.getInputDataFilePath(fileName=fileName)


# ----------------------------------------------------------------------------------


data_A = {
    "imagePath_1": "https://property.es-img.jp/rent/img/1136293183700000023966/0000000001136293183700000023966_10.jpg?iid=509482932",
    "text_1": "物件情報",
    "text_2": "東京臨海高速鉄道りんかい線",
    "text_3": "リゾートゲートウェイ駅    徒歩30分",
}

data_B = {
    "imagePath_1": "https://property.es-img.jp/rent/img/1136293183700000019925/0000000001136293183700000019925_1.jpg?iid=4032567125",
    "imagePath_2": "https://property.es-img.jp/rent/img/1136293183700000019925/0000000001136293183700000019925_23.jpg?iid=3611105031",
    "text_1": "•　専有面積 22㎡\n\n•　モニタ付インターホン\n\n•　システムキッチン\n\n•　2口コンロ\n\n•　ガスコンロ",
    "text_2": "モニターが付いていることで、訪問者を事前に確認でき、不審者を防ぐことができます。特に賃貸物件では、他人と共有する空間が多いため、安心感が増します。",
    "text_3": "敷金 1ヶ月  礼金 1ヶ月",
}

data_C = {
    "imagePath_1": "https://property.es-img.jp/rent/img/1136293183700000019925/0000000001136293183700000019925_6.jpg?iid=3655407388",
    "imagePath_2": "https://property.es-img.jp/rent/img/1136293183700000019925/0000000001136293183700000019925_13.jpg?iid=119543694",
    "text_1": "•　モニタ付インターホン\n\n•　システムキッチン\n\n•　2口コンロ\n\n•　ガスコンロ",
    "text_2": "モニターが付いていることで、訪問者を事前に確認でき、不審者を防ぐことができます。特に賃貸物件では、他人と共有する空間が多いため、安心感が増します。",
}

data_D = {
    "imagePath_1": "https://property.es-img.jp/rent/img/1136293183700000019925/0000000001136293183700000019925_3.jpg?iid=3660388147",
    "imagePath_2": "https://property.es-img.jp/rent/img/1136293183700000019925/0000000001136293183700000019925_5.jpg?iid=147986314",
    "text_1": "•　モニタ付インターホン\n\n•　システムキッチン\n\n•　2口コンロ\n\n•　ガスコンロ",
    "text_2": "モニターが付いていることで、訪問者を事前に確認でき、不審者を防ぐことができます。特に賃貸物件では、他人と共有する空間が多いため、安心感が増します。",
}

# 各データをパターンごとにまとめる辞書
data = {"A": data_A, "B": data_B, "C": data_C, "D": data_D}

buildingName = "ネオマイム横浜阪東橋弐番館 802号室"


# Instantiate the main ImageEditor class and execute pattern editors
if __name__ == "__main__":
    image_editor = ImageEditor()
    image_editor.executePatternEditors(data, buildingName)
