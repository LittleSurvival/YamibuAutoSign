import sqlite3
import os
import json

class DataModel:
    def __init__(self):
        db_folder = os.path.dirname(os.path.abspath(__file__))
        database_folder = os.path.join(db_folder, "..", "database")
        os.makedirs(database_folder, exist_ok=True)
        db_path = os.path.join(database_folder, "accounts.db")
        self.conn = sqlite3.connect(db_path)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                cookies TEXT,
                timestamp INTEGER,
                good INTEGER,
                error TEXT
            )
        """)
        self.conn.commit()

    def save_account(self, account: dict):
        cursor = self.conn.cursor()
        cookies_json = json.dumps(account.get("cookies", {}))
        good_int = 1 if account.get("good") else 0
        error_msg = account.get("error", "")
        cursor.execute("""
            INSERT INTO accounts (username, cookies, timestamp, good, error)
            VALUES (?, ?, ?, ?, ?)
        """, (account["name"], cookies_json, account["timestamp"], good_int, error_msg))
        self.conn.commit()

    def read_account(self, username: str) -> dict:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM accounts WHERE username = ?", (username,))
        row = cursor.fetchone()
        if row:
            return {
                "name": row[1],
                "cookies": json.loads(row[2]),
                "timestamp": row[3],
                "good": bool(row[4]),
                "error": row[5]
            }
        return {}
