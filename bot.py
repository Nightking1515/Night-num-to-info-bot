# Import necessary libraries
import logging
import requests
import json
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# --- CONFIGURATION ---
# 1. Replace 'YOUR_BOT_TOKEN' with your actual Bot Token
BOT_TOKEN = "YOUR_BOT_TOKEN"

# 2. API Endpoints
MOBILE_API_BASE_URL = "YOUR_NUMBER_API_KEY"
AADHAAR_API_BASE_URL = "YOUR_ADHAR_NUM_API_KEY"
RC_API_BASE_URL = "YOUR_VHICLE_INFO_API_KEY"

# 3. Footer Details (Two Channels)
BOT_SIGNATURE = "made by @Nightking1515"
CHANNEL_1_TEXT = "@nightools"
CHANNEL_1_URL = "https://t.me/nightools"
CHANNEL_2_TEXT = "@LEADER_JIII"
CHANNEL_2_URL = "https://t.me/LEADER_JIII"

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- FORMATTING HELPER FUNCTIONS ---

def format_mobile_result(record: dict, number: str) -> str:
    """Formats the mobile number data."""
    current_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    # Extract data points
    name = record.get('name', 'N/A')
    father = record.get('father_name', 'N/A')
    mobile = record.get('mobile', number)
    address = record.get('address', 'N/A')
    network = record.get('circle', 'N/A')
    aadhar_id = record.get('id_number', 'N/A')

    # Construct the custom formatted message
    record_message = (
        f"🔎 ✅ <b>DIGITAL FOOTPRINT FOUND</b> {current_time}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"<b>RECORD #01</b>\n"
        f"👤 ├ Name: {name}\n"
        f"👨‍👧 ├ Father: {father}\n"
        f"📱 ├ Mobile: {mobile}\n"
        f"🏠 ├ Address: {address}\n"
        f"🗼 ├ Network: {network}\n"
        f"🆔 └ Aadhar ID: {aadhar_id}\n"
        f"──────────────────────────"
    )
    return record_message

def format_aadhaar_result(record: dict, aadhaar_number: str) -> str:
    """Formats the Aadhaar data."""
    current_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    # Extract data points
    uid = record.get('uid', aadhaar_number)
    name = record.get('name', 'N/A')
    dob = record.get('dob', 'N/A')
    state = record.get('state', 'N/A')
    gender = record.get('gender', 'N/A')
    address = record.get('address', 'N/A')

    # Construct the custom formatted message
    record_message = (
        f"🔒 📄 <b>AADHAAR INFO FOUND</b> {current_time}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"<b>AADHAAR RECORD</b>\n"
        f"🆔 ├ UID (Partial): {uid[-4:]}\n"
        f"👤 ├ Name: {name}\n"
        f"🎂 ├ DOB: {dob}\n"
        f"🚻 ├ Gender: {gender}\n"
        f"🗺️ ├ State: {state}\n"
        f"🏠 └ Address: {address}\n"
        f"──────────────────────────"
    )
    return record_message

def format_rc_result(record: dict, rc_number: str) -> str:
    """Formats the RC (Vehicle) data using the specific keys found in the API response (e.g., Nexus2)."""
    current_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    # Use exact keys found in the API response to ensure correct data mapping
    owner_name = record.get('Owner Name', 'N/A')
    vehicle_model = record.get('Model Name', 'N/A')
    fuel_type = record.get('Fuel Type', 'N/A')
    # Using 'Insurance Expiry' as the status since the API provides this key
    insurance_status = record.get('Insurance Expiry', 'N/A')
    # FitnessStatus might be missing in this specific response
    fitness_status = record.get('FitnessStatus', 'N/A')
    rto_location = record.get('Registered RTO', 'N/A')

    # Construct the custom formatted message
    record_message = (
        f"🚗 📜 <b>VEHICLE RC INFO FOUND</b>\n"
        f"{current_time}\n"
        f"<b>RC RECORD</b>\n"
        f"🔢 ├ Reg No: {rc_number.upper()}\n"
        f"👤 ├ Owner: {owner_name}\n"
        f"🚘 ├ Model: {vehicle_model}\n"
        f"⛽ ├ Fuel Type: {fuel_type}\n"
        f"🛡️ ├ Insurance Expiry: {insurance_status}\n"
        f"✅ ├ Fitness Status: {fitness_status}\n"
        f"📍 └ RTO Location: {rto_location}\n"
    )
    return record_message

def get_footer() -> str:
    """Generates the footer containing the two channel links."""
    return (
        f"\n"
        f"<b>{BOT_SIGNATURE}</b>\n"
        f"Channels to Join for Full Use:\n"
        f"👇 <a href='{CHANNEL_1_URL}'>{CHANNEL_1_TEXT}</a>\n"
        f"👇 <a href='{CHANNEL_2_URL}'>{CHANNEL_2_TEXT}</a>"
    )

# --- COMMAND HANDLERS ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays available commands on /start."""
    logger.info("Received /start command. Showing instructions.")

    welcome_message = (
        "🤖 <b>Welcome to the Information Bot!</b>\n\n"
        "Here are the commands you can use to fetch information:\n\n"

        "📱 <b>1. Mobile Number Lookup:</b>\n"
        "   Command: <code>/num &lt;10-digit-number&gt;</code>\n"
        "   Example: <code>/num 1234567890</code>\n\n"

        "📄 <b>2. Aadhaar Lookup:</b>\n"
        "   Command: <code>/adhr &lt;12-digit-aadhaar&gt;</code>\n"
        "   Example: <code>/adhr 123456789012</code>\n\n"

        "🚗 <b>3. Vehicle RC Lookup:</b>\n"
        "   Command: <code>/rc &lt;vehicle-registration-number&gt;</code>\n"
        "   Example: <code>/rc HR01AB0001</code>\n\n"

        "Use one of the commands above to get started!"
    )
    await update.message.reply_html(welcome_message)

async def handle_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE, api_url: str, number_input: str, formatter_func) -> None:
    """Generic function to handle API calls, transaction messages, and result display."""

    # Send 'Finding' message
    finding_message = await update.message.reply_text("🔍 Searching for data... Please wait.")
    finding_message_id = finding_message.message_id
    chat_id = update.effective_chat.id

    try:
        # 1. Fetch data from the external API
        response = requests.get(f"{api_url}{number_input}")

        if response.status_code == 200:

            # 2. Parse JSON
            data = json.loads(response.text)

            results = []

            if formatter_func == format_rc_result:
                # RC API Fixed Handling: Searching for 'Nexus2' inside 'result'
                rc_record = None

                if isinstance(data, dict) and 'result' in data and isinstance(data['result'], dict):
                    # RC API data is structured as {'result': {'Nexus1': {...}, 'Nexus2': {...}}}
                    if 'Nexus2' in data['result'] and isinstance(data['result']['Nexus2'], dict):
                        rc_record = data['result']['Nexus2']
                    # Fallback to Nexus1 if Nexus2 is not available
                    elif 'Nexus1' in data['result'] and isinstance(data['result']['Nexus1'], dict):
                         rc_record = data['result']['Nexus1']

                # Final check: if a valid record was extracted (checking for owner name key)
                if rc_record and (rc_record.get('Owner Name') or rc_record.get('owner_name')):
                    results = [rc_record]
                else:
                    # Log the full JSON response if data is unsuccessful or empty
                    logger.warning(f"RC API returned unsuccessful or empty data for {number_input}. Full JSON received: {json.dumps(data, indent=2)}")

            else:
                # General handling for /num and /adhr APIs: data is within the 'result' key list
                results = data.get('result', [])
                if not isinstance(results, list):
                    results = []


            if results and any(isinstance(r, dict) and len(r) > 0 for r in results):

                # Format valid records
                valid_results = [r for r in results if isinstance(r, dict) and len(r) > 0]
                final_messages = [formatter_func(record, number_input) for record in valid_results]

                # Add Footer
                if formatter_func == format_rc_result:
                    # For RC, join message and footer with a line break
                    full_output = final_messages[0] + "\n" + get_footer()
                else:
                    # For others, join records with double line breaks and add footer
                    full_output = "\n\n".join(final_messages) + get_footer()


                # Delete 'Finding' message and send the result
                await context.bot.delete_message(chat_id=chat_id, message_id=finding_message_id)
                await update.message.reply_html(full_output)

            else:
                # No results found
                await context.bot.delete_message(chat_id=chat_id, message_id=finding_message_id)
                await update.message.reply_text(
                    f"🤷‍♂️ Search completed, but no digital footprint found for input: <code>{number_input}</code>",
                    parse_mode='HTML'
                )

        else:
            # API call failed with a non-200 status code
            logger.error(f"API call failed with status code: {response.status_code} for URL: {api_url}{number_input}")
            await context.bot.delete_message(chat_id=chat_id, message_id=finding_message_id)
            await update.message.reply_text(
                "🚨 Alas! I could not fetch information right now. The external API may be unavailable or returned a non-success status code."
            )

    except requests.exceptions.RequestException as e:
        logger.error(f"Network error during API call: {e}")
        await context.bot.delete_message(chat_id=chat_id, message_id=finding_message_id)
        await update.message.reply_text(
            "🚨 A network issue occurred while fetching the footprint. Please try again later."
        )
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        await context.bot.delete_message(chat_id=chat_id, message_id=finding_message_id)
        await update.message.reply_text(
            "🛑 An unexpected error occurred. Check the logs for details."
        )


async def num_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the /num command for mobile lookup."""
    if not context.args:
        await update.message.reply_text("Please provide a mobile number after /num. Example: /num 7801848687")
        return

    number_input = context.args[0].strip()

    # Validation
    if not number_input.isdigit() or len(number_input) < 7:
        await update.message.reply_text(f"❌ '{number_input}' does not look like a valid number.")
        return

    await handle_lookup(update, context, MOBILE_API_BASE_URL, number_input, format_mobile_result)


async def adhr_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the /adhr command for Aadhaar lookup."""
    if not context.args:
        await update.message.reply_text("Please provide an Aadhaar number after /adhr. Example: /adhr 123456789012")
        return

    aadhaar_input = context.args[0].strip()

    # Validation
    if not aadhaar_input.isdigit():
        await update.message.reply_text(f"❌ '{aadhaar_input}' contains invalid characters. Please enter digits only.")
        return

    await handle_lookup(update, context, AADHAAR_API_BASE_URL, aadhaar_input, format_aadhaar_result)


async def rc_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the /rc command for Vehicle RC lookup."""
    if not context.args:
        await update.message.reply_text("Please provide a vehicle registration number after /rc. Example: /rc HR01AB0001")
        return

    rc_input = context.args[0].strip()

    # Validation
    if not rc_input:
        await update.message.reply_text(f"❌ Please provide a non-empty vehicle registration number.")
        return

    await handle_lookup(update, context, RC_API_BASE_URL, rc_input, format_rc_result)


# --- MAIN FUNCTION ---

def main():
    """Starts the bot."""
    if BOT_TOKEN == "YOUR_BOT_TOKEN":
        print("\n--- WARNING ---\nPlease replace 'YOUR_BOT_TOKEN' with your Telegram Bot Token in the script before running.\n---------------")
        return

    # Build the application
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("num", num_command_handler))
    application.add_handler(CommandHandler("adhr", adhr_command_handler))
    application.add_handler(CommandHandler("rc", rc_command_handler))

    # Handler for unknown messages (non-command text is not ignored, but given a response)
    async def unknown_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.message.text.startswith('/'):
            await update.message.reply_text("Unknown command. Use /start to see available commands.")
        else:
            await update.message.reply_text("I only respond to commands. Use /start to see available commands.")

    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), unknown_message))


    # Start the bot
    print("Bot is running... Press Ctrl-C to stop.")
    application.run_polling()

if __name__ == '__main__':
    main()
