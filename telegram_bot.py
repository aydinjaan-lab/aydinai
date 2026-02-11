import os
import requests
import asyncio
from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters

TELEGRAM_API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

status_message_id = None
status_chat_id = None

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

async def keep_alive_task(app):
    global status_message_id, status_chat_id

    while True:
        if status_message_id and status_chat_id:
            try:
                await app.bot.edit_message_text(
                    chat_id=status_chat_id,
                    message_id=status_message_id,
                    text="🟢 AI is active\nLast refresh: every 5 minutes"
                )
            except:
                pass
        await asyncio.sleep(300)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global status_message_id, status_chat_id

    user_text = update.message.text
    reply = query_mistral(user_text)

    sent = await update.message.reply_text(reply)

    # Save last message info for editing
    status_message_id = sent.message_id
    status_chat_id = update.effective_chat.id

def main():
    app = Application.builder().token(TELEGRAM_API_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.create_task(keep_alive_task(app))

    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()