import face_recognition
import numpy as np
from pymongo import MongoClient
import os
from datetime import datetime

# MongoDB connection
client = MongoClient(os.getenv("MONGODB_URI", "mongodb://localhost:27017"))
db = client["attendance_db"]

def encode_face(face_image: bytes, user_id: str) -> bool:
    """
    Encode a face and store it in the database
    """
    try:
        # Load the image
        image = face_recognition.load_image_file(face_image)
        face_encodings = face_recognition.face_encodings(image)
        
        if not face_encodings:
            return False
        
        # Convert numpy array to list for MongoDB storage
        encoding_list = face_encodings[0].tolist()
        
        # Store in database
        db.face_encodings.update_one(
            {"user_id": user_id},
            {"$set": {"encoding": encoding_list, "updated_at": datetime.now()}},
            upsert=True
        )
        return True
    except Exception as e:
        print(f"Error encoding face: {e}")
        return False

def verify_face(face_data: bytes, user_id: str = None) -> bool:
    """
    Verify a face against stored encodings
    If user_id is provided, only check that user's encoding
    Otherwise, find the matching user from all encodings
    """
    try:
        # Load the uploaded image
        image = face_recognition.load_image_file(face_data)
        face_encodings = face_recognition.face_encodings(image)
        
        if not face_encodings:
            return False
        
        current_encoding = face_encodings[0]
        
        # If user_id provided, compare against that specific user
        if user_id:
            stored_data = db.face_encodings.find_one({"user_id": user_id})
            if not stored_data:
                return False
                
            stored_encoding = np.array(stored_data["encoding"])
            matches = face_recognition.compare_faces([stored_encoding], current_encoding, tolerance=0.6)
            return matches[0]
        
        # Otherwise, compare against all stored encodings
        stored_data = db.face_encodings.find()
        for data in stored_data:
            stored_encoding = np.array(data["encoding"])
            matches = face_recognition.compare_faces([stored_encoding], current_encoding, tolerance=0.6)
            if matches[0]:
                return True
                
        return False
    except Exception as e:
        print(f"Error verifying face: {e}")
        return False

def mark_attendance(user_id: str, face_data: bytes = None, course_id: str = None) -> dict:
    """
    Mark attendance for a user
    Optional face verification if face_data is provided
    """
    # Verify face if provided
    if face_data and not verify_face(face_data, user_id):
        return {"success": False, "message": "Face verification failed"}
    
    # Mark attendance
    attendance_record = {
        "user_id": user_id,
        "timestamp": datetime.now(),
        "verified_by_face": bool(face_data),
        "course_id": course_id
    }
    
    result = db.attendance.insert_one(attendance_record)
    if result.inserted_id:
        return {"success": True, "message": "Attendance marked successfully"}
    
    return {"success": False, "message": "Failed to mark attendance"}
