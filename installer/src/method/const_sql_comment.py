# SQLのpromptを保管
# ----------------------------------------------------------------------------------
# 2024/7/17 更新
# tree -I 'venv|resultOutput|__pycache__'

# ----------------------------------------------------------------------------------
# import
from enum import Enum

# ----------------------------------------------------------------------------------


class SqlitePrompt(Enum):
    TABLES_CREATE="CREATE TABLE IF NOT EXISTS {table_name} ({cols_info});"

    TABLES_EXISTS="SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"

    COLUMNS_EXISTS="PRAGMA table_info({table_name});"

    TRANSACTION="BEGIN TRANSACTION;"

    INSERT="INSERT INTO {table_name} ({table_column_names}) VALUES ({placeholders})"

    UPDATE="UPDATE {table_name} SET {update_placeholders} WHERE {filter_keys_placeholders}"

    READ="SELECT * FROM {table_name}"

    READ_WHERE=" WHERE {filter_keys_placeholders}"
