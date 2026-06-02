"""
schema_loader.py
Reads the connected database and extracts table/column info.
This schema is injected into the NL→SQL model as context.
"""

import sqlite3
from sqlalchemy import create_engine, inspect, text


class SchemaLoader:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.engine = create_engine(f"sqlite:///{db_path}")
        self.inspector = inspect(self.engine)

    def get_tables(self) -> list[str]:
        """Return all table names in the database."""
        return self.inspector.get_table_names()

    def get_columns(self, table_name: str) -> list[dict]:
        """Return columns with name and type for a table."""
        return self.inspector.get_columns(table_name)

    def get_schema_string(self) -> str:
        """
        Build a compact schema string to inject into the model prompt.
        Format: "table1(col1:type, col2:type) | table2(col1:type)"
        """
        tables = self.get_tables()
        parts = []
        for table in tables:
            cols = self.get_columns(table)
            col_str = ", ".join(
                f"{c['name']}:{str(c['type'])}" for c in cols
            )
            parts.append(f"{table}({col_str})")
        return " | ".join(parts)

    def get_schema_display(self) -> dict:
        """
        Returns schema as dict for pretty terminal display.
        { table_name: [(col_name, col_type), ...] }
        """
        result = {}
        for table in self.get_tables():
            cols = self.get_columns(table)
            result[table] = [(c["name"], str(c["type"])) for c in cols]
        return result

    def get_db_name(self) -> str:
        """Extract database name from path."""
        return self.db_path.split("/")[-1].replace(".db", "")