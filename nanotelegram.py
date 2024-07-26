from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Get the WhatsApp API URL and access token from environment variables
WHATSAPP_API_URL = os.getenv('WHATSAPP_API_URL')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')

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
    return [
        {'id': '1', 'title': 'Luxury Villa', 'contact': 'https://example.com/contact/1', 'view': 'https://example.com/view/1', 'pay': 'https://example.com/pay/1'},
        {'id': '2', 'title': 'Modern Apartment', 'contact': 'https://example.com/contact/2', 'view': 'https://example.com/view/2', 'pay': 'https://example.com/pay/2'},
    ]

def send_carousel_message(to, results):
    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}',
        'Content-Type': 'application/json',
    }

    elements = []
    for result in results:
        elements.append({
            'title': result['title'],
            'buttons': [
                {
                    'type': 'postback',
                    'title': 'Contact',
                    'payload': result['contact'],
                },
                {
                    'type': 'postback',
                    'title': 'View',
                    'payload': result['view'],
                },
                {
                    'type': 'postback',
                    'title': 'Pay',
                    'payload': result['pay'],
                },
            ],
        })

    payload = {
        'messaging_product': 'whatsapp',
        'to': to,
        'type': 'template',
        'template': {
            'name': 'carousel',
            'language': {
                'code': 'en_US'
            },
            'components': [
                {
                    'type': 'body',
                    'elements': elements
                }
            ]
        }
    }

    response = requests.post(WHATSAPP_API_URL, headers=headers, json=payload)
    print(response.json())  # Print the response for debugging

def send_text_message(to, text):
    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}',
        'Content-Type': 'application/json',
    }

    payload = {
        'messaging_product': 'whatsapp',
        'to': to,
        'type': 'text',
        'text': {
            'body': text
        }
    }

    response = requests.post(WHATSAPP_API_URL, headers=headers, json=payload)
    print(response.json())  # Print the response for debugging

if __name__ == '__main__':
    app.run(debug=True)
