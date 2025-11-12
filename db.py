# db.py (ringkas)
import pymysql
from contextlib import contextmanager

DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,          # ganti kalau 3307
    "user": "root",     # atau root
    "password": "",  # kosongkan "" jika root XAMPP default
    "database": "visual3_2210010610",
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
    "autocommit": True,
}

@contextmanager
def get_conn():
    conn = pymysql.connect(**DB_CONFIG)
    try: yield conn
    finally: conn.close()
