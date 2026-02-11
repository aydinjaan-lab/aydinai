import os
import requests
from flask import Flask, request
from telegram import Update
from telegram import Bot

# ==============================
# ENV VARIABLES (SET IN RENDER)
# ==============================
TELEGRAM_API_TOKEN = os.environ.get("TELEGRAM_API_TOKEN")
MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY")

# ==============================
# INIT
# ==============================
app = Flask(__name__)
bot = Bot(token=TELEGRAM_API_TOKEN)

# ==============================
# SIMPLE MEMORY (per user)
# ==============================
user_memory = {}

# ==============================
# MISTRAL REQUEST
# ==============================
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

    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print("Mistral error:", e)
        return "AI error. Please try again."

# ==============================
# WEBHOOK
# ==============================
@app.route(f"/{TELEGRAM_API_TOKEN}", methods=["POST"])
def webhook():
    try:
        update = Update.de_json(request.get_json(force=True), bot)

        if update.message and update.message.text:
            user_id = update.message.from_user.id
            user_text = update.message.text

            if user_id not in user_memory:
                user_memory[user_id] = [
                    {"role": "system", "content": "You are a helpful AI assistant with memory."}
                ]

            user_memory[user_id].append({"role": "user", "content": user_text})

            # keep last 20 messages only
            user_memory[user_id] = user_memory[user_id][-20:]

            ai_reply = ask_mistral(user_memory[user_id])

            user_memory[user_id].append({"role": "assistant", "content": ai_reply})

            # IMPORTANT: use requests instead of async send_message
            send_url = f"https://api.telegram.org/bot{TELEGRAM_API_TOKEN}/sendMessage"
            requests.post(send_url, json={
                "chat_id": update.message.chat.id,
                "text": ai_reply
            })

        return "OK"

    except Exception as e:
        print("Webhook error:", e)
        return "Error", 500

# ==============================
# HEALTH CHECK
# ==============================
@app.route("/")
def home():
    return "Bot is running."

# ==============================
# START
# ==============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)