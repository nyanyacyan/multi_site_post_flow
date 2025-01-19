# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import
import os
import pandas as pd
from typing import List

# 自作モジュール
from .utils import Logger
from .path import BaseToPath


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************


class FolderChecker:
    def __init__(self):
        # logger
        self.getLogger = Logger()
        self.logger = self.getLogger.getLogger()

        # インスタンス
        self.path = BaseToPath()


    ####################################################################################
    # 画像フォルダを存在しているか確認、またファイルが存在しているのかを確認

    def folder_error_check(self, sub_dir_name: str, df: pd.DataFrame, col_name: str):
        unmatched_folders = self._check_unmatched_folders(sub_dir_name=sub_dir_name, df=df, col_name=col_name)
        if unmatched_folders:
            return unmatched_folders

        self.logger.info(f"画像フォルダOK")
        file_error_messages = self._check_files_in_folders(sub_dir_name=sub_dir_name, df=df, col_name=col_name)
        if file_error_messages:
            self.logger.error(file_error_messages)
            return file_error_messages

        return None

    ####################################################################################

    # ----------------------------------------------------------------------------------
    # フォルダのアンマッチを確認

    def _check_unmatched_folders(self, sub_dir_name: str, df: pd.DataFrame, col_name: str):
        # それぞれのリストを生成
        dir_name_list = self._get_dir_all_folder(sub_dir_name=sub_dir_name)
        gss_dir_name_list = self._get_dir_name_list_in_gss(df=df, col_name=col_name)

        # もし作成できてないディレクトリ合った場合に出力
        unmatched_list = self._not_match_list(dir_name_list=dir_name_list, gss_dir_name_list=gss_dir_name_list)
        if unmatched_list:
            comment = '\n'.join([f"[エラー] {diff_name} フォルダがありません" for diff_name in unmatched_list])
            self.logger.warning(comment)
            return comment
        # エラーなし
        return None


    # ----------------------------------------------------------------------------------
    # フォルダにファイルがあるかを確認

    def _check_files_in_folders(self, sub_dir_name: str, df: pd.DataFrame, col_name: str):
        gss_dir_name_list = self._get_dir_name_list_in_gss(df=df, col_name=col_name)
        # すべてマッチしていた→フォルダにファイルが存在しているか確認
        file_error_msg_list = []
        for sub_sub_dir_name in gss_dir_name_list:
            result, file_error_msg = self._is_check_file(sub_dir_name=sub_dir_name, sub_sub_dir_name=sub_sub_dir_name)
            if not result:
                file_error_msg_list.append(file_error_msg)

        # 対象のフォルダにファイルが無かった場合にエラーメッセージを返す
        if file_error_msg_list:
            file_error_comment = '\n'.join(file_error_msg_list)
            self.logger.error(f"file_error_msg: {file_error_comment}")
            return file_error_comment
        # エラーなし
        return None

    # ----------------------------------------------------------------------------------
    # input_photoディレクトリを指定

    def _get_photo_folder_path(self, sub_dir_name: str):
        dir_path = self.path._get_input_photo_subdir_path(subDirName=sub_dir_name)
        self.logger.debug(f'dir_path: {dir_path}')
        return dir_path

    # ----------------------------------------------------------------------------------
    # input_photoにあるフォルダ名を取得

    def _get_dir_all_folder(self, sub_dir_name: str):
        folder_path = self._get_photo_folder_path(sub_dir_name=sub_dir_name)
        dir_name_list = [dir_name for dir_name in os.listdir(folder_path)]
        self.logger.debug(f'dir_name_list: {dir_name_list}')
        return dir_name_list

    # ----------------------------------------------------------------------------------
    # 各ディレクトリにファイルがあるかどうかを確認する

    def _not_match_list(self, dir_name_list: List, gss_dir_name_list: List):
        dir_name_set = set(dir_name_list)
        return [not_match_item for not_match_item in gss_dir_name_list if not_match_item not in dir_name_set ]

    # ----------------------------------------------------------------------------------
    # データフレームを受け取って特定の値のリストを返す

    def _get_dir_name_list_in_gss(self, df: pd.DataFrame, col_name: str):
        gss_dir_name_list = df[col_name].tolist()
        self.logger.debug(f'gss_dir_name_list: {gss_dir_name_list}')
        return gss_dir_name_list

    # ----------------------------------------------------------------------------------
    # すべてのディレクトリにファイルが有るかを確認する

    def _is_check_file(self, sub_dir_name: str, sub_sub_dir_name: str):
        sub_dir_path = self._get_photo_path(sub_dir_name=sub_dir_name, sub_sub_dir_name=sub_sub_dir_name)
        result_bool = any(folder.is_file() for folder in sub_dir_path.iterdir())
        if result_bool:
            self.logger.info(f"{sub_sub_dir_name}のフォルダOK")
            return True, None
        else:
            error_msg = f"[エラー] {sub_sub_dir_name}のフォルダにファイルが1つもありません"
            self.logger.error(f'error_msg: {error_msg}')
            return False, error_msg

    # ----------------------------------------------------------------------------------
    # ファイルフォルダPath

    def _get_photo_path(self, sub_dir_name: str, sub_sub_dir_name: str):
        photo_dir = self._get_photo_folder_path(sub_dir_name=sub_dir_name)
        sub_dir_path = photo_dir / sub_sub_dir_name
        self.logger.debug(f'sub_dir_path: {sub_dir_path}')
        return sub_dir_path

    # ----------------------------------------------------------------------------------
