import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# ========= ENV VARIABLES =========
TELEGRAM_API_TOKEN = os.environ.get("TELEGRAM_API_TOKEN")
MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY")

# ========= MEMORY STORAGE =========
# Stores conversation per user_id
user_memory = {}

# ========= MISTRAL CALL =========
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
        return "AI error: " + response.text


# ========= MESSAGE HANDLER =========
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_text = update.message.text

    # Initialize memory for new users
    if user_id not in user_memory:
        user_memory[user_id] = [
            {"role": "system", "content": "You are a helpful AI assistant with memory."}
        ]

    # Add user message
    user_memory[user_id].append({"role": "user", "content": user_text})

    # Limit memory to last 20 messages
    if len(user_memory[user_id]) > 20:
        user_memory[user_id] = user_memory[user_id][-20:]

    # Get AI response
    ai_reply = ask_mistral(user_memory[user_id])

    # Add AI response to memory
    user_memory[user_id].append({"role": "assistant", "content": ai_reply})

    await update.message.reply_text(ai_reply)


# ========= MAIN =========
def main():
    app = ApplicationBuilder().token(TELEGRAM_API_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot running with memory...")

    app.run_polling()


if __name__ == "__main__":
    main()