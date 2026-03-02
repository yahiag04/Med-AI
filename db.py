import os
from collections.abc import Iterable
from typing import Any, Optional, Tuple

import psycopg
from psycopg.rows import dict_row

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/medai")


def _connect() -> psycopg.Connection:
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)


def init_db() -> None:
    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS patients (
                    id SERIAL PRIMARY KEY,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    dob TEXT,
                    gender TEXT,
                    notes TEXT,
                    created_at TEXT NOT NULL
                );
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS xrays (
                    id SERIAL PRIMARY KEY,
                    patient_id INTEGER NOT NULL REFERENCES patients (id),
                    filename TEXT NOT NULL,
                    original_filename TEXT NOT NULL,
                    prediction_label TEXT NOT NULL,
                    probability DOUBLE PRECISION NOT NULL,
                    urgency TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                """
            )
        conn.commit()
    finally:
        conn.close()


def get_db() -> Iterable[psycopg.Connection]:
    conn = _connect()
    try:
        yield conn
    finally:
        conn.close()


def fetch_one(conn: psycopg.Connection, query: str, params: Tuple[Any, ...] = ()) -> Optional[dict[str, Any]]:
    with conn.cursor() as cur:
        cur.execute(query, params)
        return cur.fetchone()


def fetch_all(conn: psycopg.Connection, query: str, params: Tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    with conn.cursor() as cur:
        cur.execute(query, params)
        return cur.fetchall()


def execute(conn: psycopg.Connection, query: str, params: Tuple[Any, ...] = ()) -> None:
    with conn.cursor() as cur:
        cur.execute(query, params)
    conn.commit()


def execute_returning_id(conn: psycopg.Connection, query: str, params: Tuple[Any, ...] = ()) -> int:
    with conn.cursor() as cur:
        cur.execute(query, params)
        row = cur.fetchone()
    conn.commit()
    if not row:
        raise RuntimeError("Query did not return an id.")
    return int(row["id"])
