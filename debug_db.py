import sqlite3
from datetime import datetime

conn = sqlite3.connect("bot_data.db")
c = conn.cursor()
c.execute("SELECT * FROM messages")
rows = c.fetchall()
print(f"Total rows: {len(rows)}")
for r in rows:
    print(r)

print("-" * 20)
print(f"Server Local Time: {datetime.now()}")
print(f"Server UTC Time: {datetime.utcnow()}")
conn.close()
