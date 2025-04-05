import os
import json
import aiosqlite

class Account:
    """
    Data structure representing a Yamibo account with associated Discord information.
    """
    def __init__(self, discord_user_id, discord_guild_id, username="", cookies={ }, timestamp=0, good=False, autosign=False):
        """
        Initialize an Account object.
        
        :param discord_user_id: The Discord user ID associated with this account
        :param discord_guild_id: The Discord guild ID associated with this account
        :param username: The Yamibo username
        :param cookies: Dictionary of cookies used for authentication
        :param timestamp: Unix timestamp of when the account was created/updated
        :param good: Boolean indicating if the account is valid
        """
        self.discord_user_id = discord_user_id
        self.discord_guild_id = discord_guild_id
        self.username = username
        self.cookies = cookies or {}
        self.timestamp = timestamp
        self.good = good
        self.autosign = autosign
    
    @classmethod
    def from_dict(cls, data):
        """
        Create an Account object from a dictionary.
        
        :param data: Dictionary containing account data
        :return: Account object
        """
        return cls(
            discord_user_id=data.get("discordUserId"),
            discord_guild_id=data.get("discordGuildId"),
            username=data.get("name", ""),
            cookies=data.get("cookies", {}),
            timestamp=data.get("timestamp", 0),
            good=data.get("good", False),
            autosign=data.get("autosign", False),
        )
    
    def to_dict(self):
        """
        Convert the Account object to a dictionary.
        
        :return: Dictionary representation of the account
        """
        return {
            "discordUserId": self.discord_user_id,
            "discordGuildId": self.discord_guild_id,
            "name": self.username,
            "cookies": self.cookies,
            "timestamp": self.timestamp,
            "good": self.good,
            "autosign": self.autosign
        }

class DataBase:
    def __init__(self):
        db_folder = os.path.dirname(os.path.abspath(__file__))
        database_folder = os.path.join(db_folder, "..", "database")
        os.makedirs(database_folder, exist_ok=True)
        self.accounts_db = os.path.join(database_folder, "accounts.db")
        self.notifychannels_db = os.path.join(database_folder, "notifychannels_db.db")

    async def create_table(self):
        async with aiosqlite.connect(self.accounts_db) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    discordUserId INTEGER,
                    discordGuildId INTEGER,
                    username TEXT NOT NULL UNIQUE,
                    cookies TEXT,
                    timestamp INTEGER,
                    good INTEGER,
                    autosign INTEGER
                )
            """)
            await db.commit()
        async with aiosqlite.connect(self.notifychannels_db) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS notifychannels (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    discordGuildId INTEGER NOT NULL UNIQUE,
                    discordChannelId INTEGER NOT NULL UNIQUE
                )
            """)
            await db.commit()

    async def save_account(self, account: Account):
        cookies_json = json.dumps(account.cookies)
        good_int = 1 if account.good else 0
        autosign_int = 1 if account.autosign else 0
        async with aiosqlite.connect(self.accounts_db) as db:
            await db.execute("""
                INSERT OR REPLACE INTO accounts (discordUserId, discordGuildId, username, cookies, timestamp, good, autosign)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                account.discord_user_id,
                account.discord_guild_id,
                account.username,
                cookies_json,
                account.timestamp,
                good_int,
                autosign_int
            ))
            await db.commit()

    async def read_account_by_username(self, username: str) -> Account:
        async with aiosqlite.connect(self.accounts_db) as db:
            async with db.execute("SELECT * FROM accounts WHERE username = ?", (username,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    account_data = {
                        "discordUserId": row[1],
                        "discordGuildId": row[2],
                        "name": row[3],
                        "cookies": json.loads(row[4]),
                        "timestamp": row[5],
                        "good": bool(row[6]),
                        "autosign": bool(row[7])
                    }
                    return Account.from_dict(account_data)
                return None

    async def read_account_by_id(self, discordUserId: int) -> Account | None:
        async with aiosqlite.connect(self.accounts_db) as db:
            async with db.execute("SELECT * FROM accounts WHERE discordUserId = ?", (discordUserId,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    account_data = {
                        "discordUserId": row[1],
                        "discordGuildId": row[2],
                        "name": row[3],
                        "cookies": json.loads(row[4]),
                        "timestamp": row[5],
                        "good": bool(row[6]),
                        "autosign": bool(row[7])
                    }
                    return Account.from_dict(account_data)
                return None

    async def get_all_accounts(self) -> list[Account]:
        """
        Retrieves all account records asynchronously.
        Returns:
            A list of dictionaries, each representing an account.
        """
        accounts: list[Account] = []
        async with aiosqlite.connect(self.accounts_db) as db:
            async with db.execute("SELECT * FROM accounts") as cursor:
                async for row in cursor:
                    account_data = {
                        "discordUserId": row[1],
                        "discordGuildId": row[2],
                        "name": row[3],
                        "cookies": json.loads(row[4]),
                        "timestamp": row[5],
                        "good": bool(row[6]),
                        "autosign": bool(row[7])
                    }
                    accounts.append(Account.from_dict(account_data)) 
        return accounts
    
    async def get_autosign_accounts(self) -> list[Account]:
        """
        Retrieves all account records where autosign is true.
        Returns:
            A list of Account objects with autosign enabled.
        """
        accounts: list[Account] = []
        async with aiosqlite.connect(self.accounts_db) as db:
            async with db.execute("SELECT * FROM accounts WHERE autosign = 1") as cursor:
                async for row in cursor:
                    account_data = {
                        "discordUserId": row[1],
                        "discordGuildId": row[2],
                        "name": row[3],
                        "cookies": json.loads(row[4]),
                        "timestamp": row[5],
                        "good": bool(row[6]),
                        "autosign": bool(row[7])
                    }
                    accounts.append(Account.from_dict(account_data)) 
        return accounts
    
    async def save_notify_channels(self, channel: dict):
        async with aiosqlite.connect(self.notifychannels_db) as db:
            await db.execute("""
                INSERT OR REPLACE INTO notifychannels (discordGuildId, discordChannelId)
                VALUES (?, ?)
            """, (
                channel["discordGuildId"],
                channel["discordChannelId"],
            ))
            await db.commit()
    
    async def read_channel_by_id(self, discordGuildId: int) -> dict:
        async with aiosqlite.connect(self.accounts_db) as db:
            async with db.execute("SELECT * FROM notifychannels WHERE discordGuildId = ?", (discordGuildId,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return {
                        "discordGuildId": row[1],
                        "discordChannelId": row[2],
                    }
                return {}