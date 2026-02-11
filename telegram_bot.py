import os
import requests
from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    ContextTypes,
    filters,
)

TELEGRAM_API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

last_chat_id = None
last_message_id = None


# ===== MISTRAL API =====
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
        return "AI error."


# ===== MESSAGE HANDLER =====
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_chat_id, last_message_id

    user_text = update.message.text
    reply = query_mistral(user_text)

    sent = await update.message.reply_text(reply)

    # Save message for editing later
    last_chat_id = update.effective_chat.id
    last_message_id = sent.message_id


# ===== KEEP ALIVE JOB =====
async def keep_alive(context: ContextTypes.DEFAULT_TYPE):
    global last_chat_id, last_message_id

    if last_chat_id and last_message_id:
        try:
            await context.bot.edit_message_text(
                chat_id=last_chat_id,
                message_id=last_message_id,
                text="🟢 AI Active\nUpdated every 5 minutes"
            )
        except:
            pass


# ===== MAIN =====
def main():
    app = Application.builder().token(TELEGRAM_API_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Schedule job every 5 minutes (300 seconds)
    app.job_queue.run_repeating(keep_alive, interval=300, first=300)

    print("Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()