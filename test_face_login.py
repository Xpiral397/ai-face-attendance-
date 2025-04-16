import base64
import json
import requests

try:
    # Read the image file and encode it in base64
    with open('test_face.jpg', 'rb') as f:
        img_data = base64.b64encode(f.read()).decode('utf-8')
    
    # Create the payload for the face login API
    payload = {
        'email': 'test@example.com',
        'face_image': img_data
    }
    
    # Make the API request
    response = requests.post('http://127.0.0.1:8000/api/auth/face_login/', json=payload)
    
    # Print the response
    print("Status Code:", response.status_code)
    print("Response:")
    print(json.dumps(response.json(), indent=2))
    
except Exception as e:
    print(f"Error: {e}") 