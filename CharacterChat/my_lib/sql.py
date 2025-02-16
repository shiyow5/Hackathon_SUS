import sqlite3
import json

def create_table():
    conn = sqlite3.connect("datas/chat_history/memory.db")
    cursor = conn.cursor()

    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS messages (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   name TEXT UNIQUE,
                   conversation TEXT)
                   """)
    conn.commit()
    conn.close()

def save_messages(name, messages):
    conn = sqlite3.connect("datas/chat_history/memory.db")
    cursor = conn.cursor()

    json_data = json.dumps(messages)

    cursor.execute("""
                    INSERT INTO messages (name, conversation) 
                    VALUES (?, ?) 
                    ON CONFLICT(name) DO UPDATE SET conversation = excluded.conversation
                    """, (name, json_data))
    conn.commit()
    conn.close()

def get_messages(name):
    conn = sqlite3.connect("datas/chat_history/memory.db")
    cursor = conn.cursor()

    cursor.execute("SELECT conversation FROM messages WHERE name = ?", (name,))
    row = cursor.fetchone()

    conn.close()

    return json.loads(row[0]) if row else []

create_table()