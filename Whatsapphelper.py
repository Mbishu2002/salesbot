import requests
import os
import mimetypes
from requests.structures import CaseInsensitiveDict

class WhatsAppHelper:
    def __init__(self, phone_number_id, access_token):
        self.phone_number_id = phone_number_id
        self.access_token = access_token
        self.base_url = f"https://graph.facebook.com/v21.0/{self.phone_number_id}"
        self.headers = CaseInsensitiveDict()
        self.headers["Authorization"] = f"Bearer {self.access_token}"
        self.headers["Content-Type"] = "application/json"

    def upload_media(self, file_url):
        # Download the file from the URL
        response = requests.get(file_url)
        if response.status_code != 200:
            raise Exception(f"Failed to download file from URL: {file_url}")
        
        # Get file information
        file_name = os.path.basename(file_url)
        content_type = response.headers.get('content-type')
        file_content = response.content
        
        # Upload media
        upload_url = f"{self.base_url}/media"
        files = {
            'file': (file_name, file_content, content_type),
        }
        data = {
            'messaging_product': 'whatsapp',
            'type': content_type.split('/')[0],  # e.g., 'image', 'video', 'audio', etc.
        }
        
        upload_response = requests.post(upload_url, headers=self.headers, data=data, files=files)
        
        if upload_response.status_code != 200:
            raise Exception(f"Error uploading media: {upload_response.text}")
        
        upload_result = upload_response.json()
        
        if 'error' in upload_result:
            raise Exception(f"Error uploading media: {upload_result['error']['message']}")
        
        if 'id' not in upload_result:
            raise Exception("Upload failed: No media ID received")
        
        return upload_result['id']

    def send_carousel(self, to_phone_number, properties):
        url = f"{self.base_url}/messages"

        carousel_cards = []
        for index, prop in enumerate(properties):
            media_id = self.upload_media(prop['video_url'])
            card = {
                "card_index": index,
                "components": [
                    {
                        "type": "header",
                        "parameters": [
                            {
                                "type": "video",
                                "video": {
                                    "id": media_id
                                }
                            }
                        ]
                    },
                    {
                        "type": "body",
                        "parameters": [
                            {"type": "text", "text": prop['name']},
                            {"type": "text", "text": prop['description']},
                            {"type": "text", "text": prop['price']},
                            {"type": "text", "text": prop['down_payment']},
                            {"type": "text", "text": prop['location']}
                        ]
                    },
                    {
                        "type": "button",
                        "sub_type": "url",
                        "index": "0",
                        "parameters": [
                            {
                                "type": "text",
                                "text": str(index + 1)
                            }
                        ]
                    }
                ]
            }
            carousel_cards.append(card)

        data = {
            "messaging_product": "whatsapp",
            "to": to_phone_number,
            "type": "template",
            "template": {
                "name": "property_search_carousel_v4",
                "language": {
                    "code": "en_US"
                },
                "components": [
                    {
                        "type": "carousel",
                        "cards": carousel_cards
                    }
                ]
            }
        }

        resp = requests.post(url, headers=self.headers, json=data)
        return resp.status_code, resp.json()