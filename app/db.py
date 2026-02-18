import sqlite3
from datetime import datetime

DB_PATH = "verillm.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            model TEXT,
            prompt TEXT,
            parameters TEXT,
            response TEXT,
            prompt_hash TEXT,
            response_hash TEXT,
            session_hash TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_session(data):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO sessions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, data)
    conn.commit()
    conn.close()
