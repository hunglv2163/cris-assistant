import sqlite3
from datetime import datetime, timedelta

DB_NAME = "bot_data.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            chat_id INTEGER,
            chat_title TEXT,
            content TEXT,
            timestamp DATETIME
        )
    ''')
    conn.commit()
    conn.close()

def save_message(user_id, username, chat_id, chat_title, content, timestamp=None):
    if timestamp is None:
        timestamp = datetime.now()
        
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT INTO messages (user_id, username, chat_id, chat_title, content, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, username, chat_id, chat_title, content, timestamp))
    conn.commit()
    conn.close()

def get_messages_today(chat_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Get start of today (local time)
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    c.execute('''
        SELECT username, content, timestamp 
        FROM messages 
        WHERE chat_id = ? AND timestamp >= ?
        ORDER BY timestamp ASC
    ''', (chat_id, today_start))
    
    rows = c.fetchall()
    conn.close()
    return rows
