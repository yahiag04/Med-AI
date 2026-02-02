import sqlite3
from pathlib import Path
from typing import Iterable, Optional, Tuple

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "app.db"


def init_db(db_path: Path) -> None:
    conn = sqlite3.connect(str(db_path))
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                dob TEXT,
                gender TEXT,
                notes TEXT,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS xrays (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                filename TEXT NOT NULL,
                original_filename TEXT NOT NULL,
                prediction_label TEXT NOT NULL,
                probability REAL NOT NULL,
                urgency TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (patient_id) REFERENCES patients (id)
            );
            """
        )
    finally:
        conn.close()


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def fetch_one(conn: sqlite3.Connection, query: str, params: Tuple = ()) -> Optional[sqlite3.Row]:
    cur = conn.execute(query, params)
    return cur.fetchone()


def fetch_all(conn: sqlite3.Connection, query: str, params: Tuple = ()) -> Iterable[sqlite3.Row]:
    cur = conn.execute(query, params)
    return cur.fetchall()


def execute(conn: sqlite3.Connection, query: str, params: Tuple = ()) -> int:
    cur = conn.execute(query, params)
    conn.commit()
    return cur.lastrowid
