"""
Enhanced face recognition service with user matching and authentication
"""
import os
import base64
from io import BytesIO
from PIL import Image
import logging
import uuid
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

logger = logging.getLogger(__name__)

def save_face_image(image_data, user_id):
    """
    Save a face image for a user
    """
    try:
        # Create user directory if it doesn't exist
        user_dir = os.path.join(settings.MEDIA_ROOT, 'faces', str(user_id))
        os.makedirs(user_dir, exist_ok=True)
        
        # Generate a unique filename
        filename = f"{uuid.uuid4()}.jpg"
        file_path = os.path.join(user_dir, filename)
        
        # Save the image
        if isinstance(image_data, bytes):
            with open(file_path, 'wb') as f:
                f.write(image_data)
        else:
            # Assume it's a Django uploaded file
            path = default_storage.save(file_path, ContentFile(image_data.read()))
            
        logger.info(f"Saved face image for user {user_id}: {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"Failed to save face image: {e}")
        return None

def identify_user_by_face(image_data):
    """
    Identify a user by face image
    
    In a real implementation, this would:
    1. Get the face encoding from the image
    2. Compare with all registered users' face encodings
    3. Return the user_id of the best match

    For this simplified version, we'll simulate face matching by checking 
    if the user's face data exists in our database
    """
    try:
        # Convert base64 to bytes if it's a string
        if isinstance(image_data, str):
            try:
                image_data = base64.b64decode(image_data)
            except Exception as e:
                logger.error(f"Error decoding base64 image: {e}")
                return None

        # In a real implementation, we would:
        # 1. Detect face in the image
        # 2. Get the face encoding
        # 3. Compare with stored encodings for all users
        # 4. Return the best match
        
        # For testing, save the image to a test directory
        test_dir = os.path.join(settings.MEDIA_ROOT, 'test_images')
        os.makedirs(test_dir, exist_ok=True)
        filename = f"login_attempt_{uuid.uuid4()}.jpg"
        file_path = os.path.join(test_dir, filename)
        
        # Save the image for logging/debugging
        with open(file_path, 'wb') as f:
            f.write(image_data)
        
        logger.info(f"Saved login attempt image: {file_path}")
        
        # For demonstration purposes, check if this is the first image
        # If it is the first image, we'll consider it a match with the test user's email
        # In a real implementation, we would do actual face recognition here
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Return the first user found (for testing only)
        # In a real implementation, we would return the best face match
        user = User.objects.filter(active=True).first()
        
        if user:
            logger.info(f"Identified user: {user.email}")
            return user.email
        else:
            logger.warning("No active users found in the database")
            return None
            
    except Exception as e:
        logger.error(f"Error in identify_user_by_face: {e}")
        return None

def verify_face(image_data, user_id=None):
    """
    Verify if the face in the image matches the given user
    
    In a real implementation, this would use face_recognition to compare face embeddings
    """
    try:
        # Convert base64 to bytes if it's a string
        if isinstance(image_data, str):
            try:
                image_data = base64.b64decode(image_data)
            except Exception as e:
                logger.error(f"Error decoding base64 image: {e}")
                return False

        # For testing purposes, always return True
        # In a real implementation, we would compare the face with the user's stored face data
        
        # Save the image for logging/debugging
        if image_data:
            test_dir = os.path.join(settings.MEDIA_ROOT, 'verification_attempts')
            os.makedirs(test_dir, exist_ok=True)
            filename = f"verify_{user_id}_{uuid.uuid4()}.jpg"
            file_path = os.path.join(test_dir, filename)
            
            with open(file_path, 'wb') as f:
                f.write(image_data)
            logger.info(f"Saved verification image for user {user_id}: {file_path}")
        
        # Always return True for testing
        # In production, this would be the result of actual face comparison
        return True
    except Exception as e:
        logger.error(f"Face verification error: {e}")
        return False

def extract_face_encoding(image_data):
    """
    Extract face encoding from image
    """
    # This would use face_recognition to detect faces and extract encodings
    # For now, we'll return a dummy encoding
    return [0.0] * 128  # face_recognition returns 128-dimensional encodings 

def register_face(image_data, user_id):
    """
    Register a face for a user

    Args:
        image_data: Base64 encoded image
        user_id: User's ID
        
    Returns:
        bool: Success status
    """
    try:
        # Convert base64 to bytes if it's a string
        if isinstance(image_data, str):
            try:
                image_data = base64.b64decode(image_data)
            except Exception as e:
                logger.error(f"Error decoding base64 image: {e}")
                return False
        
        # In a real implementation:
        # 1. Detect face in the image
        # 2. Extract face encoding
        # 3. Store the face encoding for this user
        
        # For now, just save the image
        image_path = save_face_image(image_data, user_id)
        
        if image_path:
            logger.info(f"Face registered for user {user_id}")
            return True
        else:
            logger.error(f"Failed to save face image for user {user_id}")
            return False
    except Exception as e:
        logger.error(f"Error registering face: {e}")
        return False 