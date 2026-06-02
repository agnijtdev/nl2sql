"""
db_executor.py
Executes the generated SQL on the connected SQLite database.
Handles errors gracefully and returns results as list of dicts.
"""

import sqlite3
from typing import Optional


class DBExecutor:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def execute(self, sql: str) -> dict:
        """
        Execute SQL and return results.
        Returns: { success, rows, columns, row_count, error }
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(sql)

            if sql.strip().upper().startswith("SELECT"):
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                data = [dict(row) for row in rows]
                conn.close()
                return {
                    "success": True,
                    "rows": data,
                    "columns": columns,
                    "row_count": len(data),
                    "error": None,
                }
            else:
                conn.commit()
                affected = cursor.rowcount
                conn.close()
                return {
                    "success": True,
                    "rows": [],
                    "columns": [],
                    "row_count": affected,
                    "error": None,
                    "message": f"Query executed. {affected} row(s) affected.",
                }

        except sqlite3.Error as e:
            return {
                "success": False,
                "rows": [],
                "columns": [],
                "row_count": 0,
                "error": str(e),
            }

    def validate_sql(self, sql: str) -> tuple[bool, Optional[str]]:
        """
        Validates SQL syntax without executing it.
        Returns (is_valid, error_message)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute(f"EXPLAIN {sql}")
            conn.close()
            return True, None
        except sqlite3.Error as e:
            return False, str(e)