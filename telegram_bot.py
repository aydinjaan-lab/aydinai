import os
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters

# === ENV VARIABLES ===
TELEGRAM_API_TOKEN = os.getenv("8561743954:AAFD1u3JHW58iAKEJENQE2DR8MMlfotnoSs")
MISTRAL_API_KEY = os.getenv("MewX6VX5JOJWQsopXkE6mr2PSgfMQTV3")

# === MISTRAL API CALL ===
def query_mistral(prompt):
    url = "https://api.mistral.ai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "mistral-small",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return "Error contacting Mistral API."

# === TELEGRAM HANDLER ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    reply = query_mistral(user_text)
    await update.message.reply_text(reply)

# === MAIN ===
def main():
    app = Application.builder().token(TELEGRAM_API_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()