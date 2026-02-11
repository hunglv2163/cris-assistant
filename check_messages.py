import sqlite3
from datetime import datetime

conn = sqlite3.connect("bot_data.db")
c = conn.cursor()

print("--- Checking messages saved in the last hour ---")
c.execute("SELECT id, username, content, timestamp FROM messages ORDER BY id DESC LIMIT 10")
rows = c.fetchall()
for r in rows:
    print(r)

print("\n--- Checking for specific content 'oke' ---")
c.execute("SELECT id, username, content, timestamp FROM messages WHERE content LIKE '%oke%'")
rows = c.fetchall()
for r in rows:
    print(r)

conn.close()
