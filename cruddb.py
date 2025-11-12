# cruddb.py — versi dengan like_any + guard NULL + raw
import pymysql
from contextlib import contextmanager

DB_CONFIG = {
    "host":       "127.0.0.1",
    "user":       "root",
    "password":   "",              # isi sesuai punyamu
    "database":   "visual3_2210010610",
    "charset":    "utf8mb4",
    "autocommit": True,
    "cursorclass": pymysql.cursors.DictCursor,
}

@contextmanager
def get_conn():
    conn = pymysql.connect(**DB_CONFIG)
    try:
        yield conn
    finally:
        try:
            conn.close()
        except Exception:
            pass


class Crud:
    def __init__(self, table, pk="id", columns=None):
        self.table   = table
        self.pk      = pk
        self.columns = columns or []

    # ================== READ ==================
    def all(self, order_by=None, limit=None):
        sql = f"SELECT * FROM {self.table}"
        if order_by:
            sql += f" ORDER BY {order_by}"
        if limit:
            sql += " LIMIT %s"
            params = (int(limit),)
        else:
            params = ()
        with get_conn() as c, c.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()

    def get(self, pk_val):
        if pk_val is None:
            return None
        sql = f"SELECT * FROM {self.table} WHERE {self.pk}=%s"
        with get_conn() as c, c.cursor() as cur:
            cur.execute(sql, (pk_val,))
            return cur.fetchone()

    def raw(self, sql, params=None):
        """
        Eksekusi SQL mentah.
        CATATAN: kalau pakai LIKE, pakai '%%' di string Python agar tidak bentrok dengan format jadul.
        """
        with get_conn() as c, c.cursor() as cur:
            cur.execute(sql, params or ())
            # fetchall aman untuk SELECT; untuk DML akan mengembalikan []
            return cur.fetchall()

    def like_any(self, columns, keyword, order_by=None, limit=None):
        """
        Cari dengan LIKE ke banyak kolom: LOWER(col) LIKE CONCAT('%%', LOWER(%s), '%%')
        columns: list[str]
        keyword: str
        """
        kw = (keyword or "").strip()
        if not kw:
            return self.all(order_by=order_by, limit=limit)

        where = []
        params = []
        for col in columns:
            # kalau kolom bisa numerik (id), cast ke CHAR biar LIKE jalan
            expr = f"LOWER({col}) LIKE CONCAT('%%', LOWER(%s), '%%')"
            if col.lower() == "id":
                expr = "LOWER(CAST(id AS CHAR)) LIKE CONCAT('%%', LOWER(%s), '%%')"
            where.append(expr)
            params.append(kw)

        sql = f"SELECT * FROM {self.table} WHERE " + " OR ".join(where)
        if order_by:
            sql += f" ORDER BY {order_by}"
        if limit:
            sql += " LIMIT %s"
            params.append(int(limit))

        return self.raw(sql, tuple(params))

    # ================== WRITE ==================
    def insert(self, data: dict):
        cols = []
        vals = []
        ph   = []
        for k in self.columns:
            cols.append(k)
            v = data.get(k, None)
            # ubah "" jadi None biar kolom DATE/INT/NOT NULL gak drama
            if isinstance(v, str) and v.strip() == "":
                v = None
            vals.append(v)
            ph.append("%s")
        sql = f"INSERT INTO {self.table} ({','.join(cols)}) VALUES ({','.join(ph)})"
        with get_conn() as c, c.cursor() as cur:
            cur.execute(sql, tuple(vals))
            return cur.lastrowid

    def update(self, pk_val, data: dict):
        sets = []
        vals = []
        for k in self.columns:
            v = data.get(k, None)
            if isinstance(v, str) and v.strip() == "":
                v = None
            sets.append(f"{k}=%s")
            vals.append(v)
        vals.append(pk_val)
        sql = f"UPDATE {self.table} SET {', '.join(sets)} WHERE {self.pk}=%s"
        with get_conn() as c, c.cursor() as cur:
            cur.execute(sql, tuple(vals))
            return cur.rowcount

    def delete(self, pk_val):
        sql = f"DELETE FROM {self.table} WHERE {self.pk}=%s"
        with get_conn() as c, c.cursor() as cur:
            cur.execute(sql, (pk_val,))
            return cur.rowcount
