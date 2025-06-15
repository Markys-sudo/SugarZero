import sqlite3
from datetime import date

DB_PATH = "database/bot.db"

def add_diary_entry(user_id: int, text: str):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS food_diary (user_id INT, text TEXT, day TEXT)")
        c.execute("INSERT INTO food_diary (user_id, text, day) VALUES (?, ?, ?)", (user_id, text, date.today().isoformat()))
        conn.commit()

def get_diary_entries(user_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS food_diary (user_id INT, text TEXT, day TEXT)")
        c.execute("SELECT text FROM food_diary WHERE user_id = ? AND day = ?", (user_id, date.today().isoformat()))
        return [row[0] for row in c.fetchall()]

def clear_diary(user_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("DELETE FROM food_diary WHERE user_id = ? AND day = ?", (user_id, date.today().isoformat()))
        conn.commit()
