import os
import asyncio
import threading
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Load variables from .env file
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
AUTHORIZED_USER_ID = int(os.getenv("AUTHORIZED_USER_ID", "0"))
AGENT_AUTH_KEY = os.getenv("AGENT_AUTH_KEY")

pending_command = None

# --- Telegram Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != AUTHORIZED_USER_ID:
        return
    await update.message.reply_text("👋 Controller Online.\n/lock - Lock PC\n/shutdown - Turn off PC\n/status - Queue state")

async def lock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global pending_command
    if update.effective_user.id != AUTHORIZED_USER_ID:
        return
    pending_command = "lock"
    await update.message.reply_text("🔒 Command queued: LOCK")

async def shutdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global pending_command
    if update.effective_user.id != AUTHORIZED_USER_ID:
        return
    pending_command = "shutdown"
    await update.message.reply_text("⚠️ Command queued: SHUTDOWN")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != AUTHORIZED_USER_ID:
        return
    await update.message.reply_text(f"Pending action: {pending_command or 'None'}")

# --- Fixed Thread Logic ---
def run_telegram():
    # Explicitly create and set a new event loop for this background thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("lock", lock))
    app.add_handler(CommandHandler("shutdown", shutdown))
    app.add_handler(CommandHandler("status", status))
    
    # Run polling on the newly created event loop
    app.run_polling(stop_signals=None)

# --- Flask Server ---
flask_app = Flask(__name__)

@flask_app.route('/poll', methods=['GET'])
def poll_command():
    global pending_command
    token = request.headers.get("Authorization")
    if token != f"Bearer {AGENT_AUTH_KEY}":
        return jsonify({"error": "Unauthorized"}), 401
    
    cmd = pending_command
    pending_command = None  # Clear once fetched
    return jsonify({"action": cmd})

# Start Telegram bot thread
threading.Thread(target=run_telegram, daemon=True).start()

if __name__ == "__main__":
    flask_app.run(host='0.0.0.0', port=int(os.getenv("PORT", 5000)))
