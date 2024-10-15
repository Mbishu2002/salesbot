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

                    if text.lower().startswith('/search'):
                        query = text[8:].strip()
                        if query:
                            results = perform_property_search(query)
                            send_carousel_message(from_number, results)
                        else:
                            send_text_message(from_number, "Please provide a search query after /search.")
    return jsonify({'status': 'success'})

def perform_property_search(query):
    # This is a placeholder. In a real application, you would query your database or API.
    return [
        {
            "name": "Luxury Apt",
            "description": "3BR view",
            "price": "$500k",
            "down_payment": "$25k",
            "location": "Downtown",
            "video_url": "https://example.com/luxury_apt_video.mp4"
        },
        {
            "name": "Cozy Studio",
            "description": "Quiet area",
            "price": "$150k",
            "down_payment": "$7.5k",
            "location": "Suburbs",
            "video_url": "https://example.com/cozy_studio_video.mp4"
        },
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
