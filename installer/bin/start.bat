@echo on
chcp 65001 > nul
set PYTHONIOENCODING=utf-8

REM デバッグ: 開始メッセージ
echo スクリプトを開始します。

REM ログファイルの設定
set LOG_FILE=log.txt
echo > %LOG_FILE%

REM バッチファイルのパスを取得（バッチファイルがあるディレクトリ）
set BIN_DIR=%~dp0
echo BIN_DIR: %BIN_DIR% >> %LOG_FILE%

set PROJECT_ROOT=%BIN_DIR%..\..
echo PROJECT_ROOT: %PROJECT_ROOT% >> %LOG_FILE%

set VENV_DIR=%BIN_DIR%venv
echo VENV_DIR: %VENV_DIR% >> %LOG_FILE%

REM requirements.txt のパスを設定
set REQUIREMENTS_FILE=%PROJECT_ROOT%\installer\bin\requirements.txt
if not exist "%REQUIREMENTS_FILE%" (
    echo ERROR: requirements.txt が見つかりません。 >> %LOG_FILE%
    echo ERROR: requirements.txt が見つかりません。
    pause
    exit /b 1
)
echo REQUIREMENTS_FILE: %REQUIREMENTS_FILE% >> %LOG_FILE%

REM 仮想環境の作成（初回のみ）
if not exist "%VENV_DIR%" (
    echo 仮想環境を作成します... >> %LOG_FILE%
    python -m venv "%VENV_DIR%" >> %LOG_FILE% 2>&1
    if errorlevel 1 (
        echo ERROR: 仮想環境の作成に失敗しました。 >> %LOG_FILE%
        echo ERROR: 仮想環境の作成に失敗しました。
        pause
        exit /b 1
    )
) else (
    echo 仮想環境が既に存在します。 >> %LOG_FILE%
)

REM 仮想環境の有効化
if not exist "%VENV_DIR%\Scripts\activate" (
    echo ERROR: 仮想環境の有効化スクリプトが見つかりませんでした。 >> %LOG_FILE%
    echo ERROR: 仮想環境の有効化スクリプトが見つかりませんでした。
    pause
    exit /b 1
)
call "%VENV_DIR%\Scripts\activate" >> %LOG_FILE% 2>&1
echo 仮想環境が有効化されました。 >> %LOG_FILE%

REM requirements.txt のインストール（初回のみ）
set INSTALL_FLAG=%BIN_DIR%requirements_installed.flag
if not exist "%INSTALL_FLAG%" (
    echo requirements.txt をインストールします... >> %LOG_FILE%
    pip install --upgrade pip >> %LOG_FILE% 2>&1
    pip install -r "%REQUIREMENTS_FILE%" >> %LOG_FILE% 2>&1
    if errorlevel 1 (
        echo ERROR: requirements.txt のインストールに失敗しました。 >> %LOG_FILE%
        echo ERROR: requirements.txt のインストールに失敗しました。
        pause
        exit /b 1
    )
    echo > "%INSTALL_FLAG%"
) else (
    echo requirements.txt は既にインストール済みです。 >> %LOG_FILE%
)

REM main.py の検索
set MAIN_FILE=
for /r "%PROJECT_ROOT%\installer\src" %%f in (main.py) do (
    set MAIN_FILE=%%f
    goto :found_main
)
:found_main
if not defined MAIN_FILE (
    echo ERROR: main.py が見つかりませんでした。 >> %LOG_FILE%
    echo ERROR: main.py が見つかりませんでした。
    pause
    exit /b 1
)
echo MAIN_FILE: %MAIN_FILE% >> %LOG_FILE%

REM main.py の実行
echo main.py を実行します... >> %LOG_FILE%
python "%MAIN_FILE%" >> %LOG_FILE% 2>&1
if errorlevel 1 (
    echo ERROR: main.py の実行中にエラーが発生しました。 >> %LOG_FILE%
    echo ERROR: main.py の実行中にエラーが発生しました。
    start "" "%LOG_FILE%"
    pause
    exit /b 1
)

REM 仮想環境を無効化
deactivate >> %LOG_FILE% 2>&1
echo 仮想環境を無効化しました。 >> %LOG_FILE%

REM 完了メッセージ
echo スクリプトの実行が完了しました。 >> %LOG_FILE%
pause
