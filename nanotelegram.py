from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext
from telegram.helpers import escape_markdown
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from a .env file

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
PORT = int(os.getenv('PORT', 5000))

app = Flask(__name__)
bot = Bot(token=TOKEN)

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text('Welcome! Send /search to find properties.')

async def search(update: Update, context: CallbackContext):
    # Replace with actual search logic
    results = [
        {'title': '2 Bedroom Apartment', 'location': 'Malingo', 'price': '$500', 'image': 'http://example.com/image1.jpg'},
        {'title': '3 Bedroom House', 'location': 'Buea', 'price': '$750', 'image': 'http://example.com/image2.jpg'}
    ]
    
    # Generate reply markup for carousel
    reply_markup = []
    for result in results:
        reply_markup.append([{
            'text': f"View {escape_markdown(result['title'])}",
            'callback_data': f'view_{result["title"]}'
        }])
    
    for result in results:
        await update.message.reply_photo(
            photo=result['image'],
            caption=f"{escape_markdown(result['title'])}\nLocation: {escape_markdown(result['location'])}\nPrice: {escape_markdown(result['price'])}",
            reply_markup={'inline_keyboard': reply_markup}
        )

async def button(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    option = query.data.split('_')[1]
    # Handle the callback here
    await query.edit_message_text(text=f"Selected option: {option}")

async def main():
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('search', search))
    application.add_handler(CallbackQueryHandler(button))
    
    await application.initialize()
    await application.start()
    await application.updater.start_polling()

@app.route('/{}'.format(TOKEN), methods=['POST'])
def webhook():
    json_str = request.get_data(as_text=True)
    update = Update.de_json(json_str, bot)
    application.process_update(update)
    return 'ok', 200

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
    app.run(host='0.0.0.0', port=PORT)
