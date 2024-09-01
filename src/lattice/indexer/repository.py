import sqlite3
import os


def init(db_url):
    # Connect to a database (or create it)
    conn = sqlite3.connect(db_url)  # 'example.db' is the name of your database file

    # Create a cursor object
    cur = conn.cursor()


def connect(db_url):
    if os.path.exists(db_url):
        conn = sqlite3.connect(db_url)
        # Create a cursor object
        return conn
    conn = sqlite3.connect(db_url)
    cur = conn.cursor()
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        age INTEGER
    )
    """
    )
