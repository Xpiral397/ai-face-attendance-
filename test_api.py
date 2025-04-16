import requests
import base64
import os
import json

# Set the API url
BASE_URL = 'http://127.0.0.1:8000/api'

def register_user():
    """Register a new user"""
    url = f"{BASE_URL}/auth/register/"
    data = {
        "username": "testuser",
        "password": "testpass123",
        "email": "testuser@example.com",
        "full_name": "Test User",
        "role": "student"
    }
    response = requests.post(url, json=data)
    if response.status_code == 201:
        print("User registered successfully")
        return response.json()
    else:
        print(f"Failed to register user: {response.text}")
        return None

def login_user():
    """Login with username and password"""
    url = f"{BASE_URL}/auth/login/"
    data = {
        "username": "testuser",
        "password": "testpass123"
    }
    response = requests.post(url, json=data)
    if response.status_code == 200:
        print("User logged in successfully")
        return response.json()
    else:
        print(f"Failed to login: {response.text}")
        return None

def register_face(token, image_path):
    """Register a face for the user"""
    url = f"{BASE_URL}/auth/register-face/"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # Read and encode the image
    with open(image_path, 'rb') as image_file:
        image_data = base64.b64encode(image_file.read()).decode('utf-8')
    
    data = {
        "face_image": image_data
    }
    
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        print("Face registered successfully")
        return True
    else:
        print(f"Failed to register face: {response.text}")
        return False

def face_login(email, image_path):
    """Login with face recognition"""
    url = f"{BASE_URL}/auth/face-login/"
    
    # Read and encode the image
    with open(image_path, 'rb') as image_file:
        image_data = base64.b64encode(image_file.read()).decode('utf-8')
    
    data = {
        "email": email,
        "face_image": image_data
    }
    
    response = requests.post(url, json=data)
    if response.status_code == 200:
        print("Face login successful")
        return response.json()
    else:
        print(f"Face login failed: {response.text}")
        return None

def save_test_image(image_path):
    """Save the test image to a file"""
    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(image_path), exist_ok=True)
    
    # Create a sample image if needed
    if not os.path.exists(image_path):
        try:
            from PIL import Image
            import io
            # Create a dummy image
            img = Image.new('RGB', (100, 100), color='red')
            img.save(image_path)
            print(f"Created test image at {image_path}")
        except Exception as e:
            print(f"Failed to create test image: {e}")

def main():
    # Define the test image path
    test_image_path = 'media/test_images/test_face.jpg'
    
    # Save the test image
    save_test_image(test_image_path)
    
    # Register a new user
    register_data = register_user()
    if not register_data:
        return
    
    # Login with username/password
    login_data = login_user()
    if not login_data:
        return
    
    # Get the access token
    token = login_data['access']
    
    # Register the face
    face_registered = register_face(token, test_image_path)
    if not face_registered:
        return
    
    # Login with face
    face_login_data = face_login("testuser@example.com", test_image_path)
    if face_login_data:
        print("All tests passed!")

if __name__ == "__main__":
    main() 