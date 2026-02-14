import os
import requests
from flask import Flask, request
from telegram import Update

# ==============================
# ENV VARIABLES (SET IN RENDER)
# ==============================
TELEGRAM_API_TOKEN = os.environ.get("TELEGRAM_API_TOKEN")
MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY")

# ==============================
# INIT
# ==============================
app = Flask(__name__)

# ==============================
# MEMORY STORE (per user)
# ==============================
user_memory = {}

# ==============================
# SYSTEM ROLE (SAFE MULTILINE)
# ==============================
SYSTEM_ROLE = """You are a helpful AI assistant.

Rules:
- Every reply must be around 50 words.
- Always be helpful and clear.
- Use friendly emojis naturally.
- Do not exceed 60 words.
- Keep responses concise but informative.
- Maintain conversation memory.
"""

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
        update = Update.de_json(request.get_json(force=True), None)

        if update.message and update.message.text:
            user_id = update.message.from_user.id
            user_text = update.message.text

            # Initialize memory
            if user_id not in user_memory:
                user_memory[user_id] = [
                    {"role": "system", "content": SYSTEM_ROLE}
                ]

            # Add user message
            user_memory[user_id].append({"role": "user", "content": user_text})

            # Keep only last 20 messages
            user_memory[user_id] = user_memory[user_id][-20:]

            # Ask AI
            ai_reply = ask_mistral(user_memory[user_id])

            # Store assistant reply
            user_memory[user_id].append({"role": "assistant", "content": ai_reply})

            # Send message using Telegram HTTP API (sync safe)
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
# START (Local Only)
# ==============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)