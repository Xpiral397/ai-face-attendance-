import requests
import base64
import os
import json
from PIL import Image
import io
import time

# Set the API url
BASE_URL = 'http://127.0.0.1:8000/api'

def register_user(username, password, email, full_name, role="student"):
    """Register a new user"""
    url = f"{BASE_URL}/auth/register"
    data = {
        "email": email,
        "password": password,
        "full_name": full_name,
        "role": role
    }
    response = requests.post(url, json=data)
    print(f"Register response status: {response.status_code}")
    if response.status_code == 201:
        print("User registered successfully")
        return response.json()
    else:
        print(f"Failed to register user: {response.text}")
        return None

def login_user(email, password):
    """Login with email and password"""
    url = f"{BASE_URL}/auth/token"
    data = {
        "email": email,
        "password": password
    }
    response = requests.post(url, json=data)
    print(f"Login response status: {response.status_code}")
    if response.status_code == 200:
        print("User logged in successfully")
        return response.json()
    else:
        print(f"Failed to login: {response.text}")
        return None

def register_face(token, image_path):
    """Register a face for the user"""
    url = f"{BASE_URL}/auth/register-face"
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
    print(f"Face registration response status: {response.status_code}")
    if response.status_code == 200:
        print("Face registered successfully")
        return True
    else:
        print(f"Failed to register face: {response.text}")
        return False

def face_login(email, image_path):
    """Login with face recognition"""
    url = f"{BASE_URL}/auth/face-login"
    
    # Read and encode the image
    with open(image_path, 'rb') as image_file:
        image_data = base64.b64encode(image_file.read()).decode('utf-8')
    
    data = {
        "email": email,
        "face_image": image_data
    }
    
    response = requests.post(url, json=data)
    print(f"Face login response status: {response.status_code}")
    if response.status_code == 200:
        print("Face login successful")
        return response.json()
    else:
        print(f"Face login failed: {response.text}")
        return None

def create_sample_image(image_path):
    """Create a sample image for testing"""
    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(image_path), exist_ok=True)
    
    # Create a sample image
    img = Image.new('RGB', (200, 200), color=(255, 255, 255))
    # Draw a face-like pattern (very simplified)
    draw = Image.new('RGB', (200, 200))
    # Simple face outline
    for x in range(50, 150):
        for y in range(50, 150):
            if ((x-100)**2 + (y-100)**2) < 2500:
                draw.putpixel((x, y), (255, 200, 200))
    # Add eyes
    for x in range(70, 85):
        for y in range(80, 95):
            draw.putpixel((x, y), (0, 0, 0))
    for x in range(115, 130):
        for y in range(80, 95):
            draw.putpixel((x, y), (0, 0, 0))
    # Add mouth
    for x in range(75, 125):
        for y in range(120, 130):
            if ((x-100)**2 + (y-125)**2) < 625:
                draw.putpixel((x, y), (255, 0, 0))
    
    img.paste(draw, (0, 0))
    img.save(image_path)
    print(f"Created sample face image at {image_path}")

def main():
    # User information
    username = "testuser123"
    password = "password123"
    email = "testuser123@example.com"
    full_name = "Test User"
    
    # Define the test image path
    test_image_path = 'media/test_face.jpg'
    os.makedirs('media', exist_ok=True)
    
    # Create a sample face image
    create_sample_image(test_image_path)
    print(f"Sample image created at: {test_image_path}")
    
    # Step 1: Register a new user
    register_data = register_user(username, password, email, full_name)
    if not register_data:
        print("Registration failed. Trying to login in case user already exists.")
    
    # Step 2: Login with email/password
    login_data = login_user(email, password)
    if not login_data:
        print("Login failed. Cannot proceed.")
        return
    
    # Get the access token
    token = login_data['access_token']
    print(f"Access token obtained: {token[:10]}...")
    
    # Step 3: Register the face
    face_registered = register_face(token, test_image_path)
    if not face_registered:
        print("Face registration failed. But trying face login anyway in case already registered.")
    
    # Step 4: Login with face
    face_login_data = face_login(email, test_image_path)
    if face_login_data:
        face_token = face_login_data.get('access_token')
        print(f"Face login successful! Access token: {face_token[:10]}...")
        print("\nYou can now use this token for frontend authentication:")
        print(f"Bearer {face_token}")
        
        # This is what you would send to the frontend
        auth_header = f"Bearer {face_token}"
        print("\nIn your frontend code, use this header for authenticated requests:")
        print('headers: { "Authorization": "' + auth_header + '" }')
    else:
        print("Face login failed.")

if __name__ == "__main__":
    main() 