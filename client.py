import os
import sys
import time
import requests
from dotenv import load_dotenv

load_dotenv()

# Use HTTPS Render URL
SERVER_URL = os.getenv("SERVER_URL", "https://your-app-name.onrender.com/poll")
AUTH_KEY = os.getenv("AGENT_AUTH_KEY")
HEADERS = {"Authorization": f"Bearer {AUTH_KEY}"}

def execute_action(action):
    if action == "lock":
        if sys.platform == "win32":
            os.system("rundll32.exe user32.dll,LockWorkStation")
        elif sys.platform == "darwin":
            os.system("pmset displaysleepnow")
        elif sys.platform.startswith("linux"):
            os.system("loginctl lock-session")
            
    elif action == "shutdown":
        if sys.platform == "win32":
            os.system("shutdown /s /t 0")
        else:
            os.system("shutdown -h now")

def start_polling():
    while True:
        try:
            res = requests.get(SERVER_URL, headers=HEADERS, timeout=10)
            if res.status_code == 200:
                action = res.json().get("action")
                if action:
                    execute_action(action)
        except Exception:
            pass
        
        time.sleep(5)

if __name__ == "__main__":
    start_polling()
