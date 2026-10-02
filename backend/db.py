"""SQLite storage for PaisaPilot."""
import os
import sqlite3
import time

DB_PATH = os.environ.get("PAISAPILOT_DB", os.path.join(os.path.dirname(__file__), "paisapilot.db"))

SCHEMA = """
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL NOT NULL,
    currency TEXT DEFAULT 'INR',
    category TEXT NOT NULL,
    note TEXT DEFAULT '',
    created_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS budgets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT UNIQUE NOT NULL,
    monthly_limit REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS watchlist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    url TEXT DEFAULT '',
    target_price REAL NOT NULL,
    last_price REAL,
    last_checked INTEGER,
    alerted INTEGER DEFAULT 0
);
"""


_initialized = False


def get_db():
    global _initialized
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    if not _initialized:
        conn.executescript(SCHEMA)
        conn.commit()
        _initialized = True
    return conn


def init_db():
    conn = get_db()
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()


def now_ts():
    return int(time.time())


# ---- expenses ----
def add_expense(amount, category, note=""):
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO expenses (amount, currency, category, note, created_at) VALUES (?, 'INR', ?, ?, ?)",
        (amount, category, note, now_ts()),
    )
    conn.commit()
    eid = cur.lastrowid
    conn.close()
    return eid


def list_expenses(month=None, limit=200):
    conn = get_db()
    if month:
        rows = conn.execute(
            "SELECT * FROM expenses WHERE strftime('%Y-%m', datetime(created_at, 'unixepoch')) = ? ORDER BY created_at DESC LIMIT ?",
            (month, limit),
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM expenses ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_expense(eid):
    conn = get_db()
    conn.execute("DELETE FROM expenses WHERE id = ?", (eid,))
    conn.commit()
    conn.close()


def spend_by_category(month):
    conn = get_db()
    rows = conn.execute(
        """SELECT category, SUM(amount) AS total FROM expenses
           WHERE strftime('%Y-%m', datetime(created_at, 'unixepoch')) = ?
           GROUP BY category ORDER BY total DESC""",
        (month,),
    ).fetchall()
    conn.close()
    return [(r["category"], r["total"] or 0) for r in rows]


def category_spend(category, month):
    conn = get_db()
    row = conn.execute(
        """SELECT SUM(amount) AS total FROM expenses
           WHERE category = ? AND strftime('%Y-%m', datetime(created_at, 'unixepoch')) = ?""",
        (category, month),
    ).fetchone()
    conn.close()
    return row["total"] or 0


# ---- budgets ----
def set_budget(category, monthly_limit):
    conn = get_db()
    conn.execute(
        "INSERT INTO budgets (category, monthly_limit) VALUES (?, ?) "
        "ON CONFLICT(category) DO UPDATE SET monthly_limit = excluded.monthly_limit",
        (category, monthly_limit),
    )
    conn.commit()
    conn.close()


def list_budgets():
    conn = get_db()
    rows = conn.execute("SELECT category, monthly_limit FROM budgets ORDER BY category").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_budget(category):
    conn = get_db()
    conn.execute("DELETE FROM budgets WHERE category = ?", (category,))
    conn.commit()
    conn.close()


# ---- watchlist ----
def add_watch(name, target_price, url=""):
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO watchlist (name, url, target_price) VALUES (?, ?, ?)", (name, url, target_price)
    )
    conn.commit()
    wid = cur.lastrowid
    conn.close()
    return wid


def list_watches():
    conn = get_db()
    rows = conn.execute("SELECT * FROM watchlist ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_watch(wid):
    conn = get_db()
    conn.execute("DELETE FROM watchlist WHERE id = ?", (wid,))
    conn.commit()
    conn.close()


def update_watch_price(wid, price, alerted):
    conn = get_db()
    conn.execute(
        "UPDATE watchlist SET last_price = ?, last_checked = ?, alerted = ? WHERE id = ?",
        (price, now_ts(), 1 if alerted else 0, wid),
    )
    conn.commit()
    conn.close()
