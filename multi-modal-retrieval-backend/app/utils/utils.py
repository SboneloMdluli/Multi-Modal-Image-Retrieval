import functools
import sqlite3
import time

from app.core.logging_config import logger


def timing_decorator(func):
    """Decorator to measure and log function execution time."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        logger.info(f"Starting {func.__name__}")
        try:
            result = func(*args, **kwargs)
            end_time = time.time()
            duration = end_time - start_time
            logger.info(f"Completed {func.__name__} (took: {duration:.2f} seconds)")
            return result
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            raise

    return wrapper


@timing_decorator
def get_table_name():
    """Get the correct table name from the database"""
    conn = sqlite3.connect("data/online_store.db")
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        feature_tables = [t[0] for t in tables if "features" in t[0].lower()]
        if feature_tables:
            logger.info(f"Found feature table: {feature_tables[0]}")
            return feature_tables[0]
        logger.warning("No feature tables found in database")
        return None
    finally:
        conn.close()


def list_table_columns():
    """List all tables and their column names in the database"""
    conn = sqlite3.connect("data/online_store.db")
    cursor = conn.cursor()

    try:
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        results = {}
        for table in tables:
            table_name = table[0]
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = [col[1] for col in cursor.fetchall()]
            results[table_name] = columns

        return results
    finally:
        conn.close()
