import os
import requests
from flask import Flask, request

# ===== ENV VARIABLES =====
TELEGRAM_API_TOKEN = os.environ.get("TELEGRAM_API_TOKEN")
MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY")

# ===== INIT =====
app = Flask(__name__)

# ===== MEMORY STORE =====
user_memory = {}

# ===== SEND TELEGRAM MESSAGE (SYNC SAFE) =====
def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_API_TOKEN}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=data)

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