# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# Pathの設定 export PYTHONPATH="${PYTHONPATH}:/Users/nyanyacyan/Desktop/project_file/SNS_auto_upper/installer/src/method/base"

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import

from unittest.mock import patch, MagicMock
from PIL import Image

# 自作モジュール
from installer.src.method.base.imageEditor import ImageEditor, PatternAEditor, PatternBEditor, PatternCEditor, PatternDEditor


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************
# モック用のデータ
all_data = {
    'A': [
        {'image_path': 'path/to/imageA1.png', 'text': 'テキストA1'},
        {'text': 'テキストA2'},
        {'text': 'テキストA3'}
    ],
    'B': [
        {'image_path': 'path/to/imageB1.png', 'text': 'テキストB1'},
        {'image_path': 'path/to/imageB2.png', 'text': 'テキストB2'}
    ],
    'C': [
        {'image_path': 'path/to/imageC1.png', 'text': 'テキストC1'},
        {'image_path': 'path/to/imageC2.png', 'text': 'テキストC2'}
    ],
    'D': [
        {'image_path': 'path/to/imageD1.png', 'text': 'テキストD1'},
        {'image_path': 'path/to/imageD2.png', 'text': 'テキストD2'}
    ]
}

# **********************************************************************************


# **********************************************************************************
# ----------------------------------------------------------------------------------


@patch("installer.src.method.base.imageEditor.ImageEditor.logger")
@patch("os.path.exists", return_value=True)
@patch("PIL.Image.open")
def test_all_patterns_available(mock_open, mock_exists, mock_logger):
    """
    A~Dまですべてのデータが揃っているバージョンのテスト
    """
    # モックの設定
    mock_open.return_value = MagicMock(spec=Image.Image)
    editor = ImageEditor('A', all_data)
    editor.execute_pattern_editors(all_data, 'path/to/font.ttf', 'output_folder')

    # loggerのinfoメソッドが「画像処理が完了しました。」と呼ばれることを確認
    mock_logger.info.assert_any_call("画像処理が完了しました。")


# ----------------------------------------------------------------------------------


@patch("installer.src.method.base.imageEditor.ImageEditor.logger")
@patch("os.path.exists", side_effect=lambda path: not path.endswith("imageD2.png"))
@patch("PIL.Image.open")
def test_missing_pattern_d(mock_open, mock_exists, mock_logger):
    """
    Dのデータが揃っていない場合のテスト
    """
    mock_open.return_value = MagicMock(spec=Image.Image)
    editor = ImageEditor('A', all_data)
    editor.execute_pattern_editors(all_data, 'path/to/font.ttf', 'output_folder')

    # loggerのerrorメソッドが「パターン D の画像データが揃ってないため、以降のパターンをスキップします。」と呼ばれることを確認
    mock_logger.error.assert_any_call("パターン D の画像データが揃ってないため、以降のパターンをスキップします。")




# ----------------------------------------------------------------------------------


@patch("installer.src.method.base.imageEditor.ImageEditor.logger")
@patch("os.path.exists", side_effect=lambda path: not path.endswith("imageC2.png"))
@patch("PIL.Image.open")
def test_missing_pattern_c_and_beyond(mock_open, mock_exists, mock_logger):
    """
    C以降にデータが揃っていない場合のテスト
    """
    mock_open.return_value = MagicMock(spec=Image.Image)
    editor = ImageEditor('A', all_data)
    editor.execute_pattern_editors(all_data, 'path/to/font.ttf', 'output_folder')

    # loggerのerrorメソッドが「パターン C の画像データが揃ってないため、以降のパターンをスキップします。」と呼ばれることを確認
    mock_logger.error.assert_any_call("パターン C の画像データが揃ってないため、以降のパターンをスキップします。")


# ----------------------------------------------------------------------------------
