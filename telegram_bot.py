import os
import requests
from flask import Flask, request
from telegram import Bot, Update

# ===== ENV VARIABLES =====
TELEGRAM_API_TOKEN = os.environ.get("TELEGRAM_API_TOKEN")
MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY")

# ===== INIT =====
app = Flask(__name__)
bot = Bot(token=TELEGRAM_API_TOKEN)

# ===== MEMORY STORE =====
user_memory = {}

# ===== MISTRAL FUNCTION =====
def ask_mistral(messages):
    url = "https://api.mistral.ai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "mistral-small-latest",
        "messages": messages
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return "AI error."

# ===== WEBHOOK ROUTE =====
@app.route(f"/{TELEGRAM_API_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)

    if update.message and update.message.text:
        user_id = update.message.from_user.id
        user_text = update.message.text

        if user_id not in user_memory:
            user_memory[user_id] = [
                {"role": "system", "content": "You are a helpful AI assistant with memory."}
            ]

        user_memory[user_id].append({"role": "user", "content": user_text})

        if len(user_memory[user_id]) > 20:
            user_memory[user_id] = user_memory[user_id][-20:]

        ai_reply = ask_mistral(user_memory[user_id])

        user_memory[user_id].append({"role": "assistant", "content": ai_reply})

        bot.send_message(chat_id=update.message.chat.id, text=ai_reply)

    return "OK"

# ===== ROOT CHECK =====
@app.route("/")
def home():
    return "Bot is running."

# ===== START =====
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)