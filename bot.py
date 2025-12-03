# Import necessary libraries
import logging
import requests
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# --- Configuration ---

# 1. REPLACE THIS with your actual Bot Token from Telegram's BotFather.
# You MUST get a token to run the bot.
BOT_TOKEN = "YOUR_BOT_TOKEN_"

# 2. The base URL for the number API endpoint.
NUMBER_API_BASE_URL = "https://numapi.anshapi.workers.dev/?num="

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Command Handlers ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcoming message when the /start command is issued."""
    logger.info("Received /start command.")
    welcome_message = (
        "Hello! I am the Number Fact Bot. 🤖\n\n"
        "Send me any number (e.g., `42` or `1729`) and I will tell you a fun fact about it!\n"
        "Try sending: `50`"
    )
    await update.message.reply_text(welcome_message)

async def number_fact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles incoming messages, extracts a number, fetches a fact, and replies."""
    user_input = update.message.text.strip()
    logger.info(f"Received message: '{user_input}'")

    # Attempt to extract a number from the user's text
    try:
        # Check if the input is a valid number (integer or float, we'll strip non-digits for simplicity)
        number_str = user_input
        # Remove commas and spaces just in case the user included them
        number_str = number_str.replace(',', '').replace(' ', '')

        # Validate if the string is numeric (allowing for positive integers/floats)
        if not number_str.isdigit():
             # Check if it's a negative number or float, handle more complex cases if needed
            try:
                # If it can be cast to float, it's a valid number input
                float(number_str)
            except ValueError:
                # Not a simple number, so we ask the user to input a number
                await update.message.reply_text(
                    "That doesn't look like a valid number. Please send me a simple number (e.g., `5`, `100`, or `3.14`)."
                )
                return

        # At this point, number_str is a clean number string.
        fact_url = f"{NUMBER_API_BASE_URL}{number_str}"

        # Fetch data from the external API
        response = requests.get(fact_url)

        if response.status_code == 200:
            # The API returns the fact as plain text in the response body
            fact_text = response.text

            # Send the fact back to the user
            await update.message.reply_text(f"🔢 Fact about {user_input}: \n\n{fact_text}")
        else:
            logger.error(f"API call failed with status code: {response.status_code}")
            await update.message.reply_text(
                "Oops! I couldn't fetch a fact for that number right now. The external API seems to be unavailable or returned an error."
            )

    except requests.exceptions.RequestException as e:
        logger.error(f"Network error during API call: {e}")
        await update.message.reply_text(
            "I ran into a network issue while trying to get your fact. Please try again later."
        )
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        await update.message.reply_text(
            "An unexpected error occurred. Please check the logs for details."
        )

# --- Main function to set up and run the bot ---

def main():
    """Starts the bot."""
    if BOT_TOKEN == "YOUR_BOT_TOKEN":
        print("\n--- WARNING ---\nPlease replace 'YOUR_BOT_TOKEN' in the script with your actual Telegram Bot Token obtained from BotFather before running.\n---------------")
        return

    # Create the Application and pass it your bot's token.
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Register handlers
    # Command handler for /start
    application.add_handler(CommandHandler("start", start_command))

    # Message handler for any text message that is not a command.
    # We use filters.TEXT & (~filters.COMMAND) to ensure it only handles regular text.
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), number_fact_handler))

    # Start the Bot
    print("Bot is running... Press Ctrl-C to stop.")
    application.run_polling()

if __name__ == '__main__':
    main()
