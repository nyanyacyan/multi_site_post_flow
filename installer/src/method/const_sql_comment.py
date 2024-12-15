# SQLのpromptを保管
# ----------------------------------------------------------------------------------
# 2024/7/17 更新
# tree -I 'venv|resultOutput|__pycache__'

# ----------------------------------------------------------------------------------
# import
from enum import Enum

# ----------------------------------------------------------------------------------


class SqlitePromptExists(Enum):
    TABLES_CREATE="CREATE TABLE IF NOT EXISTS {table_name} ({column_info});"

    TABLES_EXISTS="SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"

    COLUMNS_EXISTS="PRAGMA table_info({table_name});"

    INSERT="INSERT INTO {tableName} {table_columnNames} VALUES ({placeholders}"
