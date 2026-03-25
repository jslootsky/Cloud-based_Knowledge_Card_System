import sqlite3
import json

db_path = "db.sqlite3"

with sqlite3.connect(db_path) as conn:
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    tables = [r[0] for r in cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
    )]
    for table in tables:
        print(f"\n== {table} ==")
        rows = cur.execute(f"SELECT * FROM {table}").fetchall()
        if not rows:
            print("<empty>")
            continue
        cols = rows[0].keys()
        print(" | ".join(cols))
        for row in rows:
            print(" | ".join(str(row[c]) for c in cols))