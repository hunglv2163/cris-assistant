from database import get_messages_today
from datetime import datetime

chat_id = -1003617346575
print(f"Testing get_messages_today for chat_id: {chat_id}")
print(f"Current time: {datetime.now()}")

messages = get_messages_today(chat_id)
print(f"Found {len(messages)} messages:")
for msg in messages:
    print(msg)
