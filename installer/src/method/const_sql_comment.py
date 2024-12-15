# SQLのpromptを保管
# ----------------------------------------------------------------------------------
# 2024/7/17 更新
# tree -I 'venv|resultOutput|__pycache__'

# ----------------------------------------------------------------------------------
# import
from enum import Enum

# ----------------------------------------------------------------------------------


class SqlitePrompt(Enum):
    TABLES_CREATE="CREATE TABLE IF NOT EXISTS {table_name} ({column_info});"

    TABLES_EXISTS="SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"

    COLUMNS_EXISTS="PRAGMA table_info({table_name});"

    INSERT="INSERT INTO {table_name} {table_column_names} VALUES ({placeholders}"

    SELECT_LAST_ROW="SELECT * FROM {table_name} ORDER BY id DESC LIMIT 1"

    TRANSACTION="BEGIN TRANSACTION;"
