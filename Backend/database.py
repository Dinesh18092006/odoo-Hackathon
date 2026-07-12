"""
AssetFlow — MySQL connection pool using mysql-connector-python.
Import `get_db` and use as a FastAPI dependency.
"""

import mysql.connector
from mysql.connector.pooling import MySQLConnectionPool
from contextlib import contextmanager
from functools import lru_cache
import os
from dotenv import load_dotenv

load_dotenv()

_pool: MySQLConnectionPool | None = None


def _create_pool() -> MySQLConnectionPool:
    return MySQLConnectionPool(
        pool_name="assetflow",
        pool_size=10,
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", 3306)),
        database=os.getenv("DB_NAME", "assetflow"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        charset="utf8mb4",
        autocommit=False,
        time_zone="+00:00",
    )


def get_pool() -> MySQLConnectionPool:
    global _pool
    if _pool is None:
        _pool = _create_pool()
    return _pool


@contextmanager
def get_db():
    """
    Yields a (connection, cursor) tuple.
    Auto-commits on success, rolls back on exception, always closes.
    """
    pool = get_pool()
    conn = pool.get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        yield conn, cursor
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def db_dep():
    """FastAPI dependency that yields (conn, cursor) via get_db context manager."""
    with get_db() as (conn, cursor):
        yield conn, cursor