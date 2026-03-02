import argparse
import os
import sqlite3
from pathlib import Path

import psycopg
from psycopg import sql

from db import init_db


def reset_sequence(conn: psycopg.Connection, table_name: str) -> None:
    with conn.cursor() as cur:
        cur.execute(
            sql.SQL(
                """
                SELECT setval(
                    pg_get_serial_sequence(%s, 'id'),
                    COALESCE(MAX(id), 1),
                    MAX(id) IS NOT NULL
                )
                FROM {table_name}
                """
            ).format(table_name=sql.Identifier(table_name)),
            (table_name,),
        )


def migrate(sqlite_path: Path, truncate: bool) -> None:
    database_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/medai")
    init_db()

    sqlite_conn = sqlite3.connect(str(sqlite_path))
    sqlite_conn.row_factory = sqlite3.Row

    pg_conn = psycopg.connect(database_url)

    try:
        users = sqlite_conn.execute(
            "SELECT id, username, password_hash, salt, created_at FROM users ORDER BY id"
        ).fetchall()
        patients = sqlite_conn.execute(
            "SELECT id, first_name, last_name, dob, gender, notes, created_at FROM patients ORDER BY id"
        ).fetchall()
        xrays = sqlite_conn.execute(
            """
            SELECT id, patient_id, filename, original_filename, prediction_label, probability, urgency, created_at
            FROM xrays ORDER BY id
            """
        ).fetchall()

        with pg_conn.cursor() as cur:
            if truncate:
                cur.execute("TRUNCATE TABLE xrays, patients, users RESTART IDENTITY CASCADE")

            cur.executemany(
                """
                INSERT INTO users (id, username, password_hash, salt, created_at)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
                """,
                [(r["id"], r["username"], r["password_hash"], r["salt"], r["created_at"]) for r in users],
            )
            cur.executemany(
                """
                INSERT INTO patients (id, first_name, last_name, dob, gender, notes, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
                """,
                [
                    (
                        r["id"],
                        r["first_name"],
                        r["last_name"],
                        r["dob"],
                        r["gender"],
                        r["notes"],
                        r["created_at"],
                    )
                    for r in patients
                ],
            )
            cur.executemany(
                """
                INSERT INTO xrays (id, patient_id, filename, original_filename, prediction_label, probability, urgency, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
                """,
                [
                    (
                        r["id"],
                        r["patient_id"],
                        r["filename"],
                        r["original_filename"],
                        r["prediction_label"],
                        r["probability"],
                        r["urgency"],
                        r["created_at"],
                    )
                    for r in xrays
                ],
            )

        reset_sequence(pg_conn, "users")
        reset_sequence(pg_conn, "patients")
        reset_sequence(pg_conn, "xrays")
        pg_conn.commit()

        print(f"Migrated users={len(users)} patients={len(patients)} xrays={len(xrays)}")
    finally:
        sqlite_conn.close()
        pg_conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migrate MedAI data from SQLite to PostgreSQL")
    parser.add_argument("--sqlite-path", default="app.db", help="Path to SQLite database file")
    parser.add_argument(
        "--truncate",
        action="store_true",
        help="Truncate PostgreSQL tables before import",
    )
    args = parser.parse_args()

    migrate(Path(args.sqlite_path), args.truncate)
