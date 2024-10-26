import requests
import os
import mimetypes
from urllib.parse import urlparse
from urllib.request import urlopen

def upload_media_to_whatsapp(file_url, phone_number_id, access_token):
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
    upload_url = f"https://graph.facebook.com/v19.0/{phone_number_id}/media"
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    
    with urlopen(file_url) as media_file:
        files = {
            'file': (file_name, media_file.read(), mime_type),
        }
        data = {
            'messaging_product': 'whatsapp',
            'type': mime_type.split('/')[0],  # e.g., 'image', 'video', 'audio', etc.
        }
        
        upload_response = requests.post(upload_url, headers=headers, data=data, files=files)
        
        # if upload_response.status_code != 200:
        #     raise Exception(f"Error uploading media: {upload_response.text}")
        
        upload_result = upload_response.json()
        
        if 'error' in upload_result:
            raise Exception(f"Error uploading media: {upload_result['error']['message']}")
    
    # Check if upload was successful
    if 'id' not in upload_result:
        raise Exception("Upload failed: No media ID received")
    
    media_id = upload_result['id']
    
    return media_id
