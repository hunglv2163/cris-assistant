import os
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def check_updates():
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    print(f"Checking updates from: {url}")
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if not data.get("ok"):
            print("Error:", data)
            return

        updates = data.get("result", [])
        print(f"Found {len(updates)} updates.")
        
        for u in updates:
            print("-" * 20)
            print(u)
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    check_updates()
