import os
import asyncio
import requests
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters

TELEGRAM_API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

RENDER_URL = "https://aydinai.onrender.com"

app = Flask(__name__)
telegram_app = Application.builder().token(TELEGRAM_API_TOKEN).build()

# ===== MEMORY STORAGE (per user) =====
user_memory = {}

MAX_HISTORY = 10  # Keep last 10 exchanges


def query_mistral(messages):
    url = "https://api.mistral.ai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "mistral-small",
        "messages": messages
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]

    return "AI error."


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_text = update.message.text

    # Create memory if new user
    if user_id not in user_memory:
        user_memory[user_id] = [
            {"role": "system", "content": "You are a helpful AI assistant."}
        ]

    # Add user message
    user_memory[user_id].append({"role": "user", "content": user_text})

    # Trim memory
    if len(user_memory[user_id]) > MAX_HISTORY * 2:
        user_memory[user_id] = user_memory[user_id][-MAX_HISTORY*2:]

    # Get AI reply
    reply = query_mistral(user_memory[user_id])

    # Save assistant reply
    user_memory[user_id].append({"role": "assistant", "content": reply})

    await update.message.reply_text(reply)


telegram_app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
)


@app.route(f"/{TELEGRAM_API_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    asyncio.run(telegram_app.process_update(update))
    return "OK", 200


@app.route("/")
def home():
    return "Bot is running."


if __name__ == "__main__":
    async def setup():
        await telegram_app.initialize()
        await telegram_app.bot.set_webhook(
            url=f"{RENDER_URL}/{TELEGRAM_API_TOKEN}"
        )

    asyncio.run(setup())

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)