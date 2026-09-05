import os
import sys
import time
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration
SERVER_URL = os.getenv("SERVER_URL")
AUTH_KEY = os.getenv("AGENT_AUTH_KEY")

if not AUTH_KEY:
    print("[ERROR] AGENT_AUTH_KEY is missing from environment variables or .env file.")
    sys.exit(1)

HEADERS = {"Authorization": f"Bearer {AUTH_KEY}"}

def execute_action(action):
    """Executes native OS commands based on the action received."""
    print(f"[ACTION RECEIVED] Executing: {action}")
    
    if action == "lock":
        if sys.platform == "win32":
            os.system("rundll32.exe user32.dll,LockWorkStation")
        elif sys.platform == "darwin":  # macOS
            os.system("pmset displaysleepnow")
        elif sys.platform.startswith("linux"):
            os.system("loginctl lock-session")
            
    elif action == "shutdown":
        if sys.platform == "win32":
            os.system("shutdown /s /t 0")
        elif sys.platform == "darwin":  # macOS
            os.system("sudo shutdown -h now")
        elif sys.platform.startswith("linux"):
            os.system("shutdown -h now")

def start_polling():
    """Polls the remote server periodically for new commands."""
    print(f"[AGENT STARTED] Polling server at: {SERVER_URL}")
    print("Press Ctrl+C to stop.")
    
    while True:
        try:
            # Poll the server with a timeout to handle network stalls
            res = requests.get(SERVER_URL, headers=HEADERS, timeout=10)
            
            if res.status_code == 200:
                action = res.json().get("action")
                if action:
                    execute_action(action)
            elif res.status_code == 401:
                print("[AUTH ERROR] Invalid AGENT_AUTH_KEY. Check your .env file.")
            else:
                print(f"[WARNING] Server responded with status code: {res.status_code}")

        except requests.exceptions.RequestException as e:
            # Silently handle temporary network hiccups (e.g., Wi-Fi reconnections)
            print(f"[NETWORK ERROR] Connection failed, retrying... ({e.__class__.__name__})")
        
        # Poll interval in seconds
        time.sleep(5)

if __name__ == "__main__":
    try:
        start_polling()
    except KeyboardInterrupt:
        print("\n[AGENT STOPPED] Exiting safely.")
