import sqlite3
import os

DB_NAME = "jarvis.db"

class MemoryOps:
    def __init__(self):
        self.init_db()

    def init_db(self):
        try:
            with sqlite3.connect(DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS memories (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        info TEXT NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                conn.commit()
                print("   [Memory] Database Connected (SQLite).")
        except Exception as e:
            print(f"   [Memory] Init Error: {e}")

    @staticmethod
    def save_memory(fact):
        try:
            with sqlite3.connect(DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO memories (info) VALUES (?)", (fact,))
                conn.commit()
            return f"Saved to memory: {fact}"
        except Exception as e:
            return f"Save Error: {e}"

    @staticmethod
    def read_memory():
        try:
            with sqlite3.connect(DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT info FROM memories ORDER BY id DESC LIMIT 5")
                rows = cursor.fetchall()
            if not rows: return "Memory is empty."
            return "Memories:\n" + "\n".join([r[0] for r in rows])
        except Exception as e:
            return f"Read Error: {e}"

mem = MemoryOps()