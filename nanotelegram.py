from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from Whatsapphelper import WhatsAppHelper

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Get the WhatsApp API credentials from environment variables
PHONE_NUMBER_ID = os.getenv('PHONE_NUMBER_ID')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
VERIFY_TOKEN = os.getenv('VERIFY_TOKEN')

# Initialize WhatsAppHelper
whatsapp_helper = WhatsAppHelper(PHONE_NUMBER_ID, ACCESS_TOKEN)

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    # Handle webhook verification
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    if token == VERIFY_TOKEN:
        return challenge
    else:
        return 'Invalid verify token', 403

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print(data)  # Print incoming data for debugging

    if 'entry' in data:
        for entry in data['entry']:
            for messaging_event in entry.get('changes', []):
                value = messaging_event.get('value', {})
                messages = value.get('messages', [])
                for message in messages:
                    from_number = message['from']
                    text = message.get('text', {}).get('body', '')

                    # Send carousel for any incoming message
                    results = perform_product_search(text)
                    send_carousel_message(from_number, results)

    return jsonify({'status': 'success'})

def perform_product_search(query):
    # This function now returns dummy product data for any query
    return [
        {
            "name": "Smartphone X",
            "description": "Latest model, 5G",
            "price": "$999",
            "rating": "4.5 stars",
            "store": "TechZone",
            "product_code": "SMRT001"
        },
        {
            "name": "Laptop Pro",
            "description": "Powerful & lightweight",
            "price": "$1499",
            "rating": "4.7 stars",
            "store": "ComputerWorld",
            "product_code": "LPTP002"
        },
        {
            "name": "Wireless Earbuds",
            "description": "Noise-cancelling",
            "price": "$199",
            "rating": "4.3 stars",
            "store": "AudioHub",
            "product_code": "WLEB003"
        }
    ]

def send_carousel_message(to, results):
    try:
        status_code, response = whatsapp_helper.send_carousel(to, results)
        print(f"Carousel sent. Status code: {status_code}")
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error sending carousel: {str(e)}")

def send_text_message(to, text):
    # You may want to implement this method in WhatsAppHelper class
    # For now, we'll use a simple print statement
    print(f"Sending text message to {to}: {text}")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
