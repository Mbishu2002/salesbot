from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from Whatsapphelper import WhatsAppHelper
import requests
import random
from upload import upload_media_to_whatsapp

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
    if 'entry' in data:
        for entry in data['entry']:
            for messaging_event in entry.get('changes', []):
                value = messaging_event.get('value', {})
                messages = value.get('messages', [])
                for message in messages:
                    from_number = message['from']
                    text = message.get('text', {}).get('body', '')

                    # Perform product search and send message
                    results = perform_product_search(text)
                    if results:
                        send_carousel_message(from_number, results)
                    else:
                        send_text_message(from_number, "Sorry, your search yielded no results.")
                    break  # Process only the first message

    return jsonify({'status': 'success'})

def perform_product_search(query):
    # Make API call to search for products
    url = f"https://elegant-crow-curiously.ngrok-free.app/api/v1/products/search/?q={query}"
    response = requests.get(url)
    if response.status_code == 200:
        products = response.json()
        results = []
        for product in products:
            # Upload the featured image and get the image ID using upload.py
            image_id = upload_media_to_whatsapp(
                product['featured_image'] if product['featured_image'] is not None and product['featured_image'] != '' else "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTX_17wXohqBtGqb62QZXQ2M1iAvNy1kvO4yA&s",
                PHONE_NUMBER_ID,
                ACCESS_TOKEN
            )
            formatted_product = format_product_for_carousel(product)
            formatted_product['image_id'] = image_id
            results.append(formatted_product)
        return results
    else:
        print(f"Error searching products: {response.status_code}")
        return []

def format_product_for_carousel(product):
    return {
        "name": product['name'],
        "description": product['description'][:50] + "..." if len(product['description']) > 50 else product['description'],
        "price": f"${product['price']}",
        "rating": f"{random.uniform(3.5, 5.0):.1f}",
        "store": product['shop']['name'],
        "product_code": product['id']
    }

def send_carousel_message(to, results):
    try:
        if len(results) < 10:
            # Send each product as an individual message
            for product in results:
                send_individual_product_message(to, product)
        else:
            # Compile the first 10 products into a single list of cards
            carousel_cards = []
            for index, product in enumerate(results[:10]):
                card = {
                    "card_index": index,
                    "components": [
                        {
                            "type": "header",
                            "parameters": [
                                {
                                    "type": "image",
                                    "image": {
                                        "id": product['image_id']
                                    }
                                }
                            ]
                        },
                        {
                            "type": "body",
                            "parameters": [
                                {"type": "text", "text": product['name']},
                                {"type": "text", "text": product['description']},
                                {"type": "text", "text": product['price']},
                                {"type": "text", "text": product['rating']},
                                {"type": "text", "text": product['store']}
                            ]
                        },
                        {
                            "type": "button",
                            "sub_type": "url",
                            "index": "0",
                            "parameters": [
                                {
                                    "type": "text",
                                    "text": product['product_code']
                                }
                            ]
                        }
                    ]
                }
                carousel_cards.append(card)

            # Send the compiled carousel
            status_code, response = whatsapp_helper.send_carousel(to, carousel_cards)
            print(f"Carousel sent. Status code: {status_code}")
            print(f"Response: {response}")
    except Exception as e:
        print(f"Error sending carousel: {str(e)}")

def send_individual_product_message(to, product):
    # This function sends an individual product message using a different template
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "template",
        "template": {
            "name": "product_card",
            "language": {
                "code": "en"
            },
            "components": [
                {
                    "type": "header",
                    "parameters": [
                        {
                            "type": "image",
                            "image": {
                                "id": product['image_id']  
                            }
                        }
                    ]
                },
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": product['name']},
                        {"type": "text", "text": product['description']},
                        {"type": "text", "text": product['price']},
                        {"type": "text", "text": product['rating']},
                        {"type": "text", "text": product['store']}
                    ]
                },
                {
                    "type": "button",
                    "sub_type": "url",
                    "index": "0",
                    "parameters": [
                        {
                            "type": "text",
                            "text": f"https://nanoweb.pages.dev/product/{product['product_code']}"
                        }
                    ]
                }
            ]
        }
    }

    # Send the individual product message
    response = requests.post(f"{whatsapp_helper.base_url}/messages", headers=whatsapp_helper.headers, json=data)
    print(f"Individual product message sent. Status code: {response.status_code}")
    print(f"Response: {response.text}")

def send_text_message(to, text):
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    response = requests.post(f"{whatsapp_helper.base_url}/messages", headers=whatsapp_helper.headers, json=data)
    print(f"Text message sent. Status code: {response.status_code}")
    print(f"Response: {response.text}")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
