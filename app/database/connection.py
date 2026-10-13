import sqlite3
from typing import Any, Dict, List, Tuple
from app.config import settings

def get_db_schema() -> str:
    """Extracts DDL statements for active tables."""
    conn = sqlite3.connect(settings.database_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = cursor.fetchall()
    conn.close()
    return "\n\n".join([f"-- Table: {name}\n{sql};" for name, sql in tables])

def execute_raw_sql(sql: str) -> Tuple[List[Dict[str, Any]] | None, str | None]:
    """Executes validated SQL and returns row dictionaries or an error string."""
    try:
        conn = sqlite3.connect(settings.database_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        result = [dict(row) for row in rows]
        conn.close()
        return result, None
    except sqlite3.Error as e:
        return None, str(e)