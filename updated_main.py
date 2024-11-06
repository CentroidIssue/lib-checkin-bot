
from typing import Final, List
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import telegram
import requests
import re
from datetime import datetime

ma = ''
TOKEN: Final = 'your_token_here'  # Replace with your token
BOT_USERNAME: Final = '@thuvien123bot'
bot = telegram.Bot(TOKEN)
chat_id = ''

# List to store pending codes
pending_codes: List[str] = []

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('hello')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Xin code')

# URL for check-in
url = 'https://libcalendar.ntu.edu.sg/r/checkin'

# Function to perform check-in with a code
async def checkin(code: str):
    payload = {
        "code": code,  
    }
    headers = {
        'Referer': 'https://libcalendar.ntu.edu.sg/r/checkin',
    }
    response = requests.post(url, data=payload, headers=headers)
    print(response.text)

# Function to extract booking time
def extract_booking_time(message):
    match = re.search(r'until (\d{1,2}:\d{2}\w{2} [A-Za-z]+, [A-Za-z]+ \d{1,2}, \d{4})', message)
    if match:
        time_str = match.group(1)
        print(time_str)
        booking_time = datetime.strptime(time_str, "%I:%M%p %A, %B %d, %Y")
        return booking_time
    return None

# Handler for messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = update.message.text
    if code not in pending_codes:
        pending_codes.append(code)
        await update.message.reply_text(f"Code {code} added to the pending list.")
    else:
        await update.message.reply_text(f"Code {code} is already in the pending list.")

# New function to list pending codes
async def pending_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if pending_codes:
        await update.message.reply_text("Pending codes:" + "".join(pending_codes))
    else:
        await update.message.reply_text("No pending codes.")

# Main function to set up the bot
def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("pending", pending_command))
    application.add_handler(MessageHandler(filters.TEXT, handle_message))

    application.run_polling()

if __name__ == '__main__':
    main()
