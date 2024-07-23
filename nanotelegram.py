from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext
from telegram.helpers import escape_markdown
import os
from dotenv import load_dotenv
import logging
import asyncio

# Load environment variables from a .env file
load_dotenv()

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
PORT = int(os.getenv('PORT', 5000))

app = Flask(__name__)

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Dummy property data
properties = [
    {'title': '2 Bedroom Apartment', 'location': 'Malingo', 'price': '$500', 'image': 'http://example.com/image1.jpg'},
    {'title': '3 Bedroom House', 'location': 'Buea', 'price': '$750', 'image': 'http://example.com/image2.jpg'},
    {'title': 'Studio Apartment', 'location': 'Molyko', 'price': '$300', 'image': 'http://example.com/image3.jpg'}
]

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text('Welcome! Send /search to find properties.')

async def search(update: Update, context: CallbackContext):
    buttons = []
    for i, prop in enumerate(properties):
        buttons.append([InlineKeyboardButton(
            text=f"View {prop['title']}",
            callback_data=f"view_{i}"
        )])

    reply_markup = InlineKeyboardMarkup(buttons)
    await update.message.reply_text("Select a property to view:", reply_markup=reply_markup)

async def button(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    index = int(query.data.split('_')[1])
    prop = properties[index]
    caption = f"{escape_markdown(prop['title'])}\nLocation: {escape_markdown(prop['location'])}\nPrice: {escape_markdown(prop['price'])}"
    await query.message.reply_photo(photo=prop['image'], caption=caption)

async def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('search', search))
    application.add_handler(CallbackQueryHandler(button))

    # Start the application
    await application.initialize()
    await application.start()
    await application.updater.start_polling()

    return application

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    asyncio.run(application.process_update(update))
    return 'ok', 200

if __name__ == '__main__':
    application = asyncio.run(main())
    app.run(host='0.0.0.0', port=PORT)
