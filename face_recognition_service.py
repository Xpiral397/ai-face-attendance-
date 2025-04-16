"""
Advanced Face Recognition Service

This is a more advanced implementation of the face recognition service
that shows how it would work in a production environment.

Requirements:
- face_recognition (https://github.com/ageitgey/face_recognition)
- numpy
- pillow

Note: This requires dlib which needs CMake to install.
"""

import os
import base64
import numpy as np
from io import BytesIO
from PIL import Image
import face_recognition
import logging
import json
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FaceRecognitionService:
    def __init__(self, face_db_dir='face_database', tolerance=0.6):
        """
        Initialize the face recognition service
        
        Args:
            face_db_dir: Directory to store face encodings
            tolerance: Tolerance for face comparison (lower = stricter)
        """
        self.face_db_dir = face_db_dir
        self.tolerance = tolerance
        self.known_face_encodings = {}
        self.known_face_names = {}
        
        # Create face database directory if it doesn't exist
        os.makedirs(face_db_dir, exist_ok=True)
        
        # Load existing face encodings
        self._load_face_database()
    
    def _load_face_database(self):
        """Load face encodings from the database directory"""
        try:
            encoding_files = [f for f in os.listdir(self.face_db_dir) 
                              if f.endswith('.json')]
            
            for file_name in encoding_files:
                user_id = file_name.split('.')[0]
                file_path = os.path.join(self.face_db_dir, file_name)
                
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    if 'encodings' in data and 'name' in data:
                        # Convert string encodings back to numpy arrays
                        encodings = [np.array(enc) for enc in data['encodings']]
                        self.known_face_encodings[user_id] = encodings
                        self.known_face_names[user_id] = data['name']
            
            logger.info(f"Loaded {len(self.known_face_encodings)} face profiles from database")
        except Exception as e:
            logger.error(f"Error loading face database: {e}")
    
    def _save_face_encoding(self, user_id, name, encodings):
        """Save face encodings to disk"""
        try:
            # Convert numpy arrays to lists for JSON serialization
            encodings_list = [encoding.tolist() for encoding in encodings]
            
            data = {
                'name': name,
                'encodings': encodings_list,
                'updated_at': datetime.now().isoformat()
            }
            
            file_path = os.path.join(self.face_db_dir, f"{user_id}.json")
            
            with open(file_path, 'w') as f:
                json.dump(data, f)
            
            logger.info(f"Saved face encoding for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error saving face encoding: {e}")
            return False
    
    def register_face(self, image_data, user_id, name):
        """
        Register a face for a user
        
        Args:
            image_data: Base64 encoded image or bytes
            user_id: Unique identifier for the user
            name: User's name
            
        Returns:
            success: Boolean indicating success
            message: Status message
            face_count: Number of faces detected
        """
        try:
            # Convert base64 to image if needed
            if isinstance(image_data, str):
                image_data = base64.b64decode(image_data)
            
            # Convert bytes to image
            image = Image.open(BytesIO(image_data))
            
            # Convert to RGB (in case of RGBA)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Convert to numpy array for face_recognition
            image_np = np.array(image)
            
            # Find faces in the image
            face_locations = face_recognition.face_locations(image_np)
            
            if not face_locations:
                return {
                    'success': False,
                    'message': 'No faces detected in the image',
                    'face_count': 0
                }
            
            if len(face_locations) > 1:
                return {
                    'success': False,
                    'message': f'Multiple faces detected ({len(face_locations)}). Please use an image with only one face.',
                    'face_count': len(face_locations)
                }
            
            # Compute face encodings
            face_encodings = face_recognition.face_encodings(image_np, face_locations)
            
            # Save the encoding
            self.known_face_encodings[user_id] = face_encodings
            self.known_face_names[user_id] = name
            
            # Save to disk
            save_result = self._save_face_encoding(user_id, name, face_encodings)
            
            return {
                'success': save_result,
                'message': 'Face registered successfully' if save_result else 'Error saving face data',
                'face_count': len(face_locations)
            }
            
        except Exception as e:
            logger.error(f"Error registering face: {e}")
            return {
                'success': False,
                'message': f'Error: {str(e)}',
                'face_count': 0
            }
    
    def verify_face(self, image_data, user_id=None):
        """
        Verify a face against a specific user or all users
        
        Args:
            image_data: Base64 encoded image or bytes
            user_id: Optional user ID to check against
            
        Returns:
            success: Boolean indicating success
            user_id: ID of the matched user (if any)
            confidence: Confidence score (lower is better)
        """
        try:
            # Convert base64 to image if needed
            if isinstance(image_data, str):
                image_data = base64.b64decode(image_data)
            
            # Convert bytes to image
            image = Image.open(BytesIO(image_data))
            
            # Convert to RGB (in case of RGBA)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Convert to numpy array for face_recognition
            image_np = np.array(image)
            
            # Find faces in the image
            face_locations = face_recognition.face_locations(image_np)
            
            if not face_locations:
                return {
                    'success': False,
                    'message': 'No faces detected in the image',
                    'user_id': None,
                    'confidence': None
                }
            
            if len(face_locations) > 1:
                return {
                    'success': False,
                    'message': f'Multiple faces detected ({len(face_locations)}). Please use an image with only one face.',
                    'user_id': None,
                    'confidence': None
                }
            
            # Compute face encoding for the input image
            face_encoding = face_recognition.face_encodings(image_np, face_locations)[0]
            
            # If user_id is provided, only compare with that user
            if user_id:
                if user_id not in self.known_face_encodings:
                    return {
                        'success': False,
                        'message': f'User {user_id} not found in database',
                        'user_id': None,
                        'confidence': None
                    }
                
                # Compare with the known encodings for this user
                matches = face_recognition.compare_faces(
                    self.known_face_encodings[user_id], 
                    face_encoding,
                    tolerance=self.tolerance
                )
                
                # Calculate the face distance (lower = more similar)
                face_distances = face_recognition.face_distance(
                    self.known_face_encodings[user_id], 
                    face_encoding
                )
                
                if any(matches):
                    best_match_index = np.argmin(face_distances)
                    confidence = float(face_distances[best_match_index])
                    
                    return {
                        'success': True,
                        'message': f'Face matched with user {user_id}',
                        'user_id': user_id,
                        'name': self.known_face_names.get(user_id),
                        'confidence': confidence
                    }
                else:
                    return {
                        'success': False,
                        'message': 'Face verification failed',
                        'user_id': None,
                        'confidence': float(min(face_distances)) if len(face_distances) > 0 else None
                    }
            
            # If no user_id is provided, compare with all known faces
            else:
                best_match = None
                best_confidence = 1.0  # Lower is better
                
                for uid, encodings in self.known_face_encodings.items():
                    # Compare with the known encodings for this user
                    matches = face_recognition.compare_faces(
                        encodings, 
                        face_encoding,
                        tolerance=self.tolerance
                    )
                    
                    # Calculate the face distance (lower = more similar)
                    face_distances = face_recognition.face_distance(
                        encodings, 
                        face_encoding
                    )
                    
                    if any(matches):
                        best_match_index = np.argmin(face_distances)
                        confidence = float(face_distances[best_match_index])
                        
                        if confidence < best_confidence:
                            best_confidence = confidence
                            best_match = uid
                
                if best_match:
                    return {
                        'success': True,
                        'message': f'Face matched with user {best_match}',
                        'user_id': best_match,
                        'name': self.known_face_names.get(best_match),
                        'confidence': best_confidence
                    }
                else:
                    return {
                        'success': False,
                        'message': 'No matching face found in database',
                        'user_id': None,
                        'confidence': None
                    }
                    
        except Exception as e:
            logger.error(f"Error verifying face: {e}")
            return {
                'success': False,
                'message': f'Error: {str(e)}',
                'user_id': None,
                'confidence': None
            }

# Usage example
if __name__ == "__main__":
    # Create the service
    face_service = FaceRecognitionService()
    
    # Example for registering a face
    def register_face_example():
        print("EXAMPLE: Registering a face")
        print("==========================")
        
        # Load test image
        with open('test_face.jpg', 'rb') as f:
            image_data = f.read()
        
        # Register the face
        result = face_service.register_face(
            image_data=image_data,
            user_id='test_user_123',
            name='Test User'
        )
        
        print(f"Success: {result['success']}")
        print(f"Message: {result['message']}")
        print(f"Face count: {result['face_count']}")
        print()
    
    # Example for verifying a face
    def verify_face_example():
        print("EXAMPLE: Verifying a face")
        print("========================")
        
        # Load test image
        with open('test_face.jpg', 'rb') as f:
            image_data = f.read()
        
        # Verify the face against a specific user
        result = face_service.verify_face(
            image_data=image_data,
            user_id='test_user_123'
        )
        
        print(f"Success: {result['success']}")
        print(f"Message: {result['message']}")
        print(f"User ID: {result['user_id']}")
        print(f"Name: {result.get('name')}")
        print(f"Confidence: {result['confidence']}")
        print()
        
        # Verify the face against all users
        result = face_service.verify_face(
            image_data=image_data
        )
        
        print("Searching against all users:")
        print(f"Success: {result['success']}")
        print(f"Message: {result['message']}")
        print(f"User ID: {result['user_id']}")
        print(f"Name: {result.get('name')}")
        print(f"Confidence: {result['confidence']}")
    
    # Run the examples
    register_face_example()
    verify_face_example() 