import os
import json
import aiosqlite

class DataModel:
    def __init__(self):
        db_folder = os.path.dirname(os.path.abspath(__file__))
        database_folder = os.path.join(db_folder, "..", "database")
        os.makedirs(database_folder, exist_ok=True)
        self.db_path = os.path.join(database_folder, "accounts.db")

    async def create_table(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    discordUserId INTEGER,
                    discordGuildId INTEGER,
                    username TEXT NOT NULL,
                    cookies TEXT,
                    timestamp INTEGER,
                    good INTEGER
                )
            """)
            await db.commit()

    async def save_account(self, account: dict):
        cookies_json = json.dumps(account.get("cookies", {}))
        good_int = 1 if account.get("good") else 0
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO accounts (discordUserId, discordGuildId, username, cookies, timestamp, good)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                account["discordUserId"],
                account["discordGuildId"],
                account["name"],
                cookies_json,
                account["timestamp"],
                good_int
            ))
            await db.commit()

    async def read_account_by_username(self, username: str) -> dict:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT * FROM accounts WHERE username = ?", (username,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return {
                        "discordUserId": row[1],
                        "discordGuildId": row[2],
                        "name": row[3],
                        "cookies": json.loads(row[4]),
                        "timestamp": row[5],
                        "good": bool(row[6])
                    }
                return {}

    async def read_account_by_id(self, discordUserId: int) -> dict:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT * FROM accounts WHERE discordUserId = ?", (discordUserId,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return {
                        "discordUserId": row[1],
                        "discordGuildId": row[2],
                        "name": row[3],
                        "cookies": json.loads(row[4]),
                        "timestamp": row[5],
                        "good": bool(row[6])
                    }
                return {}

    async def get_all_accounts(self) -> list:
        """
        Retrieves all account records asynchronously.
        Returns:
            A list of dictionaries, each representing an account.
        """
        accounts = []
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT * FROM accounts") as cursor:
                async for row in cursor:
                    accounts.append({
                        "discordUserId": row[1],
                        "discordGuildId": row[2],
                        "name": row[3],
                        "cookies": json.loads(row[4]),
                        "timestamp": row[5],
                        "good": bool(row[6])
                    })
        return accounts