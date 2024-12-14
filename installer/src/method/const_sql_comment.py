# SQLのpromptを保管
# ----------------------------------------------------------------------------------
# 2024/7/17 更新
# tree -I 'venv|resultOutput|__pycache__'

# ----------------------------------------------------------------------------------
# import
from enum import Enum

# ----------------------------------------------------------------------------------


class SqlitePromptExists(Enum):
    TABLES_EXISTS="CREATE TABLE IF NOT EXISTS {table_name} ({column_info});"

    COLUMNS_EXISTS="PRAGMA table_info({table_name});"

