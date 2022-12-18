import sqlite3


class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()

    def user_exists(self, UserId):
        self.cursor.execute(f"SELECT * FROM users WHERE UserId = {UserId}").fetchmany(1)
        with self.connection:
            result = self.cursor.execute(f"SELECT * FROM users WHERE UserId = {UserId}").fetchmany(1)
            return bool(len(result))

    def add_user(self, UserId):
        with self.connection:
            return self.cursor.execute(f"INSERT INTO users (UserId) VALUES ({UserId})")

    def set_active(self, UserId, active):
        with self.connection:
            return self.cursor.execute(f"UPDATE users SET Active = '{active}' WHERE UserId = {UserId}")

    def get_user(self):
        with self.connection:
            return self.cursor.execute("SELECT UserId FROM users").fetchall()

    def set_city(self, city, UserId):
        with self.connection:
            return self.cursor.execute(f"UPDATE users SET City = '{city}' WHERE UserId = {UserId}")
