import cv2
import base64
import json
import requests
import time
import getpass

def capture_image_from_webcam():
    """Capture an image from the webcam and return it"""
    # Initialize the webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return None
    
    # Allow the camera to warm up
    time.sleep(1)
    
    print("Capturing image in:")
    for i in range(3, 0, -1):
        print(f"{i}...")
        time.sleep(1)
    
    # Capture frame
    ret, frame = cap.read()
    
    # Release the camera
    cap.release()
    
    if not ret:
        print("Error: Could not capture image")
        return None
    
    print("Image captured successfully!")
    
    # Display the captured image (optional)
    cv2.imshow('Captured Image', frame)
    cv2.waitKey(1000)  # Display for 1 second
    cv2.destroyAllWindows()
    
    return frame

def convert_image_to_base64(image):
    """Convert an OpenCV image to base64 string"""
    # Convert image to JPEG format
    _, buffer = cv2.imencode('.jpg', image)
    
    # Convert to base64
    base64_image = base64.b64encode(buffer).decode('utf-8')
    
    return base64_image

def login_with_face_and_password(email, base64_image, password=None):
    """Send the face image and password to the server for authentication"""
    url = 'http://127.0.0.1:8000/api/auth/face_login/'
    
    # Prepare payload
    payload = {
        'face_image': base64_image
    }
    
    # Add email as a hint if provided
    if email:
        payload['email'] = email
        
    # Add password if provided for 2-factor authentication
    if password:
        payload['password'] = password
    
    # Make API request
    try:
        response = requests.post(url, json=payload)
        response_data = response.json()
        
        if response.status_code == 200:
            print("Authentication successful!")
            return response_data
        else:
            print(f"Authentication failed: {response_data.get('detail', 'Unknown error')}")
            return None
    except Exception as e:
        print(f"Error during authentication: {str(e)}")
        return None

def get_user_profile(access_token):
    """Get the user profile using the access token"""
    url = 'http://127.0.0.1:8000/api/auth/profile/'
    
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    try:
        response = requests.get(url, headers=headers)
        return response.json()
    except Exception as e:
        print(f"Error fetching profile: {str(e)}")
        return None

def main():
    print("\n== AI Face Attendance System - Enhanced Authentication ==")
    print("=======================================================")
    
    # Step 1: Optionally get the email
    print("\nStep 1: Email (Optional)")
    print("------------------------")
    print("Enter your email or leave blank to use face identification only:")
    email = input("Email: ").strip() or None
    
    if email:
        print(f"Using email hint: {email}")
    else:
        print("No email provided. The system will identify you by your face.")
    
    # Step 2: Capture face image
    print("\nStep 2: Face Capture")
    print("-------------------")
    print("Capturing your face for recognition...")
    
    # Capture image from webcam
    image = capture_image_from_webcam()
    
    if image is None:
        print("Failed to capture image. Exiting.")
        return
    
    # Convert image to base64
    base64_image = convert_image_to_base64(image)
    
    # Step 3: Get password (optional for development, should be required in production)
    print("\nStep 3: Password Verification")
    print("----------------------------")
    print("Enter your password for 2-factor authentication:")
    password = getpass.getpass("Password: ")
    
    if not password:
        print("Warning: No password provided. In production, this would be required.")
    
    # Step 4: Authenticate with face and password
    print("\nStep 4: Authentication")
    print("---------------------")
    print("Sending authentication data to server...")
    
    auth_data = login_with_face_and_password(email, base64_image, password)
    
    if auth_data:
        # Display access token (truncated for security)
        token = auth_data.get('access', '')
        if token:
            token_preview = f"{token[:20]}...{token[-20:]}"
            print(f"\nAccess Token: {token_preview}")
        
        # Get and display user profile
        print("\nFetching user profile...")
        profile = get_user_profile(auth_data.get('access', ''))
        
        if profile:
            print("\n== User Profile ==")
            print(f"Username: {profile.get('username')}")
            print(f"Email: {profile.get('email')}")
            print(f"Full Name: {profile.get('full_name', 'N/A')}")
            print(f"Role: {profile.get('role', 'N/A')}")
            print("\nAuthentication complete! You are now logged in.")
        else:
            print("Failed to fetch user profile.")
    
if __name__ == "__main__":
    main() 