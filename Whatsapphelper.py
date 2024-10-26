import requests
import os
import mimetypes
from urllib.parse import urlparse
from urllib.request import urlopen
from requests.structures import CaseInsensitiveDict

class WhatsAppHelper:
    def __init__(self, phone_number_id, access_token):
        self.phone_number_id = phone_number_id
        self.access_token = access_token
        self.base_url = f"https://graph.facebook.com/v20.0/{self.phone_number_id}"
        self.headers = CaseInsensitiveDict()
        self.headers["Authorization"] = f"Bearer {self.access_token}"
        self.headers["Content-Type"] = "application/json"

    def upload_media(self, file_url):
        # Get file information from URL
        file_name = os.path.basename(urlparse(file_url).path)
        with urlopen(file_url) as response:
            file_size = int(response.info().get('Content-Length', 0))
            mime_type = response.info().get('Content-Type')
        
        print(f"File Name: {file_name}")
        print(f"File Size: {file_size} bytes")
        print(f"MIME Type: {mime_type}")
        
        # Check file size limit
        size_limit = 16 * 1024 * 1024  # 16MB for most media types
        if mime_type.startswith('image/'):
            size_limit = 5 * 1024 * 1024  # 5MB for images
        elif mime_type == 'application/pdf':
            size_limit = 100 * 1024 * 1024  # 100MB for documents
        
        if file_size > size_limit:
            raise Exception(f"File size exceeds the limit of {size_limit / (1024 * 1024)}MB for this media type")
        # Upload media
        upload_url = f"{self.base_url}/media"
        
        with urlopen(file_url) as media_file:
            files = {
                'file': (file_name, media_file.read(), mime_type),
            }
            data = {
                'messaging_product': 'whatsapp',
                'type': mime_type.split('/')[0],  # e.g., 'image', 'video', 'audio', etc.
            }
            
            print("Params sent:")
            print(f"URL: {upload_url}")
            print(f"Headers: {self.headers}")
            print(f"Data: {data}")
            print(f"Files: {files}")
            
            print("\nExpected params:")
            print("- messaging_product (required): Should be 'whatsapp'")
            print("- type (required): Should be 'image', 'video', 'audio', etc.")
            print("- file (required): The media file to be uploaded")
            
            # Change from data=data to json=data
            upload_response = requests.post(upload_url, headers=self.headers, json=data, files=files)
            
            print(f"\nResponse status code: {upload_response.status_code}")
            print(f"Response content: {upload_response.text}")
            
            if upload_response.status_code != 200:
                raise Exception(f"Error uploading media: {upload_response.text}")
            
            upload_result = upload_response.json()
            
            print(f"\nParsed response: {upload_result}")
            
            if 'error' in upload_result:
                raise Exception(f"Error uploading media: {upload_result['error']['message']}")
        
        # Check if upload was successful
        if 'id' not in upload_result:
            raise Exception("Upload failed: No media ID received")
        
        return upload_result['id']

    def send_carousel(self, to_phone_number, carousel_cards):
        url = f"{self.base_url}/messages"

        data = {
            "messaging_product": "whatsapp",
            "to": to_phone_number,
            "type": "template",
            "template": {
                "name": "product_search_carousel_v4",
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
