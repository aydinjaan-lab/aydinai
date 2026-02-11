import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# ==============================
# YOUR KEYS
# ==============================

TELEGRAM_API_TOKEN = "8561743954:AAFD1u3JHW58iAKEJENQE2DR8MMlfotnoSs"
MISTRAL_API_KEY = "MewX6VX5JOJWQsopXkE6mr2PSgfMQTV3"

RENDER_URL = "https://aydinai.onrender.com"

# ==============================
# MEMORY STORAGE (Simple)
# ==============================

user_memory = {}

# ==============================
# TELEGRAM HANDLER
# ==============================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    # Store conversation
    if user_id not in user_memory:
        user_memory[user_id] = []

    user_memory[user_id].append(text)

    # Simple memory-based reply
    if len(user_memory[user_id]) > 5:
        reply = f"You said before: {user_memory[user_id][-2]}"
    else:
        reply = f"You said: {text}"

    await update.message.reply_text(reply)

# ==============================
# FLASK APP
# ==============================

app = Flask(__name__)
telegram_app = ApplicationBuilder().token(TELEGRAM_API_TOKEN).build()
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

@app.post(f"/{TELEGRAM_API_TOKEN}")
async def webhook():
    data = request.get_json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return "OK"

@app.get("/")
def home():
    return "Bot is running"

# ==============================
# STARTUP
# ==============================

async def setup():
    await telegram_app.initialize()
    await telegram_app.bot.set_webhook(f"{RENDER_URL}/{TELEGRAM_API_TOKEN}")

asyncio.run(setup())

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)