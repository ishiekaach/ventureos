import sqlite3
from contextlib import contextmanager
from pathlib import Path
import pandas as pd
from config import DB_PATH, DATA_DIR, BASE_DIR

@contextmanager
def get_connection():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    schema = (BASE_DIR / "database" / "schema.sql").read_text(encoding="utf-8")
    with get_connection() as conn:
        conn.executescript(schema)

def query_df(sql: str, params=()) -> pd.DataFrame:
    with get_connection() as conn:
        return pd.read_sql_query(sql, conn, params=params)

def execute(sql: str, params=()):
    with get_connection() as conn:
        cur = conn.execute(sql, params)
        return cur.lastrowid

def log_action(entity_type: str, entity_id: int | None, action: str, details: str = ""):
    execute("INSERT INTO audit_log(entity_type, entity_id, action, details) VALUES(?,?,?,?)",
            (entity_type, entity_id, action, details))
