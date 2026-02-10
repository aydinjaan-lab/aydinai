import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CallbackContext

# Replace with your actual Telegram Bot API Token and Mistral API Key
TELEGRAM_API_TOKEN = '8561743954:AAFD1u3JHW58iAKEJENQE2DR8MMlfotnoSs'  # Your Telegram bot token
MISTRAL_API_KEY = 'MewX6VX5JOJWQsopXkE6mr2PSgfMQTV3'  # Your Mistral API key

# Mistral Model API URL (generic endpoint for Mistral)
MISTRAL_API_URL = "https://api.mistral.ai/v1/generate"  # Replace with Mistral's API endpoint if different

# Function to query the Mistral API
def query_mistral_model(prompt):
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Define the payload to send to Mistral
    data = {
        "input": prompt  # Send the user query as input to Mistral
    }

    # Send POST request to Mistral API
    response = requests.post(MISTRAL_API_URL, headers=headers, json=data)
    
    if response.status_code == 200:
        # Parse the response from Mistral
        ai_response = response.json().get('generated_text', 'Sorry, I couldn\'t generate a response.')
        return ai_response
    else:
        return "There was an error connecting to Mistral. Please try again later."

# Function to handle incoming messages from the user
async def handle_message(update: Update, context: CallbackContext):
    user_message = update.message.text  # Get the message from the user
    
    # Query Mistral API with the user's message
    ai_response = query_mistral_model(user_message)
    
    # Send the response back to the user
    await update.message.reply_text(ai_response)

# Function to start the Telegram bot
def start_bot():
    # Create the Application instance (Updated for v20+)
    application = Application.builder().token(TELEGRAM_API_TOKEN).build()

    # Add message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start polling the bot
    application.run_polling()

if __name__ == '__main__':
    start_bot()  # Run the bot