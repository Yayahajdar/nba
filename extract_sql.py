import sqlite3, os
RAW_DIR = "data/raw"
os.makedirs(RAW_DIR, exist_ok=True)

def run_sql():
    conn = sqlite3.connect(f"{RAW_DIR}/mirror.db")
    conn.execute("CREATE TABLE IF NOT EXISTS mirror_teams(id INT PRIMARY KEY, name TEXT);")
    conn.execute("INSERT OR IGNORE INTO mirror_teams VALUES (1,'Lakers'),(2,'Celtics');")
    conn.commit(); conn.close()
    print("SQLite mirror.db updated")
