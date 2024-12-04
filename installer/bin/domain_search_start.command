#!/bin/bash

# エンコード設定
export PYTHONIOENCODING=utf-8

# デバッグ: 開始メッセージ
echo "スクリプトを開始します。"

# ログファイルの設定
LOG_FILE="log.txt"
echo "" > "$LOG_FILE"

# スクリプトのディレクトリを取得
BIN_DIR="$(cd "$(dirname "$0")" && pwd)"
echo "BIN_DIR: $BIN_DIR" >> "$LOG_FILE"

# プロジェクトのルートディレクトリを設定
PROJECT_ROOT="$BIN_DIR/../../.."
echo "PROJECT_ROOT: $PROJECT_ROOT" >> "$LOG_FILE"

# 仮想環境のディレクトリを設定
VENV_DIR="$BIN_DIR/venv"
echo "VENV_DIR: $VENV_DIR" >> "$LOG_FILE"

# requirements.txt のパスを設定
REQUIREMENTS_FILE="$PROJECT_ROOT/installer/bin/requirements.txt"
if [ ! -f "$REQUIREMENTS_FILE" ]; then
    echo "ERROR: requirements.txt が見つかりません。" >> "$LOG_FILE"
    echo "ERROR: requirements.txt が見つかりません。"
    exit 1
fi
echo "REQUIREMENTS_FILE: $REQUIREMENTS_FILE" >> "$LOG_FILE"

# 仮想環境の作成（初回のみ）
if [ ! -d "$VENV_DIR" ]; then
    echo "仮想環境を作成します..." >> "$LOG_FILE"
    python3 -m venv "$VENV_DIR" >> "$LOG_FILE" 2>&1
    if [ $? -ne 0 ]; then
        echo "ERROR: 仮想環境の作成に失敗しました。" >> "$LOG_FILE"
        echo "ERROR: 仮想環境の作成に失敗しました。"
        exit 1
    fi
else
    echo "仮想環境が既に存在します。" >> "$LOG_FILE"
fi

# 仮想環境を有効化
source "$VENV_DIR/bin/activate"
if [ $? -ne 0 ]; then
    echo "ERROR: 仮想環境の有効化に失敗しました。" >> "$LOG_FILE"
    echo "ERROR: 仮想環境の有効化に失敗しました。"
    exit 1
fi
echo "仮想環境が有効化されました。" >> "$LOG_FILE"

# requirements.txt のインストール（初回のみ）
INSTALL_FLAG="$BIN_DIR/requirements_installed.flag"
if [ ! -f "$INSTALL_FLAG" ]; then
    echo "requirements.txt をインストールします..." >> "$LOG_FILE"
    pip install --upgrade pip >> "$LOG_FILE" 2>&1
    pip install -r "$REQUIREMENTS_FILE" >> "$LOG_FILE" 2>&1
    if [ $? -ne 0 ]; then
        echo "ERROR: requirements.txt のインストールに失敗しました。" >> "$LOG_FILE"
        echo "ERROR: requirements.txt のインストールに失敗しました。"
        exit 1
    fi
    touch "$INSTALL_FLAG"
else
    echo "requirements.txt は既にインストール済みです。" >> "$LOG_FILE"
fi

# main.py の検索
MAIN_FILE=$(find "$PROJECT_ROOT/installer/src" -name "main.py" | head -n 1)
if [ -z "$MAIN_FILE" ]; then
    echo "ERROR: main.py が見つかりませんでした。" >> "$LOG_FILE"
    echo "ERROR: main.py が見つかりませんでした。"
    exit 1
fi
echo "MAIN_FILE: $MAIN_FILE" >> "$LOG_FILE"

# main.py の実行
echo "main.py を実行します..." >> "$LOG_FILE"
python "$MAIN_FILE" >> "$LOG_FILE" 2>&1
if [ $? -ne 0 ]; then
    echo "ERROR: main.py の実行中にエラーが発生しました。" >> "$LOG_FILE"
    echo "ERROR: main.py の実行中にエラーが発生しました。"
    open "$LOG_FILE"
    exit 1
fi

# 仮想環境を無効化
deactivate
echo "仮想環境を無効化しました。" >> "$LOG_FILE"

# 完了メッセージ
echo "スクリプトの実行が完了しました。" >> "$LOG_FILE"
open "$LOG_FILE"
exit 0
