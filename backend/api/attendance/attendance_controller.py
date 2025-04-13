from fastapi import APIRouter, HTTPException, Depends, status, Body, Query
from pymongo import MongoClient
from bson import ObjectId
import os
from datetime import datetime, timedelta
from typing import List, Optional

from models.user import UserRole, User
from services.face_service import verify_face, mark_attendance
from api.auth.auth_controller import get_current_user

router = APIRouter()

# MongoDB connection
client = MongoClient(os.getenv("MONGODB_URI", "mongodb://localhost:27017"))
db = client["attendance_db"]

@router.post("/mark")
async def mark_student_attendance(
    course_id: str,
    face_data: Optional[bytes] = Body(None),
    current_user = Depends(get_current_user)
):
    """
    Mark attendance for a student
    Optional face verification if face_data is provided
    """
    # Check if user is a student
    if current_user["role"] != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can mark attendance"
        )
    
    # Check if student is enrolled in the course
    student_profile = db.student_profiles.find_one({"user_id": str(current_user["_id"])})
    if not student_profile or course_id not in student_profile.get("courses", []):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student not enrolled in this course"
        )
    
    # Mark attendance
    result = mark_attendance(str(current_user["_id"]), face_data, course_id)
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    
    return result

@router.get("/history")
async def get_attendance_history(
    course_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user = Depends(get_current_user)
):
    """
    Get attendance history for a user
    Filtered by course_id and date range if provided
    """
    # Build query
    query = {"user_id": str(current_user["_id"])}
    if course_id:
        query["course_id"] = course_id
    
    # Add date range filter if provided
    if start_date or end_date:
        query["timestamp"] = {}
        if start_date:
            query["timestamp"]["$gte"] = datetime.fromisoformat(start_date)
        if end_date:
            query["timestamp"]["$lte"] = datetime.fromisoformat(end_date)
    
    # Get attendance records
    records = list(db.attendance.find(query).sort("timestamp", -1))
    for record in records:
        record["_id"] = str(record["_id"])
    
    return records

@router.get("/stats")
async def get_attendance_stats(
    course_id: Optional[str] = None,
    current_user = Depends(get_current_user)
):
    """
    Get attendance statistics
    """
    # Build query
    query = {"user_id": str(current_user["_id"])}
    if course_id:
        query["course_id"] = course_id
    
    # Get total attendance count
    total_count = db.attendance.count_documents(query)
    
    # Get face verified count
    face_verified_query = query.copy()
    face_verified_query["verified_by_face"] = True
    face_verified_count = db.attendance.count_documents(face_verified_query)
    
    # Get last 30 days attendance
    thirty_days_ago = datetime.now() - timedelta(days=30)
    recent_query = query.copy()
    recent_query["timestamp"] = {"$gte": thirty_days_ago}
    recent_count = db.attendance.count_documents(recent_query)
    
    return {
        "total_attendance": total_count,
        "face_verified_attendance": face_verified_count,
        "last_30_days_attendance": recent_count,
        "face_verification_percentage": (face_verified_count / total_count * 100) if total_count > 0 else 0
    }

@router.get("/report")
async def get_attendance_report(
    department_id: Optional[str] = None,
    course_id: Optional[str] = None,
    level: Optional[int] = None,
    current_user = Depends(get_current_user)
):
    """
    Get attendance report (for lecturers and admins)
    """
    # Check if user is lecturer or admin
    if current_user["role"] not in [UserRole.LECTURER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only lecturers and admins can access attendance reports"
        )
    
    # Build pipeline for aggregation
    pipeline = []
    
    # Match stage
    match_stage = {}
    if course_id:
        match_stage["course_id"] = course_id
    
    # If lecturer, only show their courses
    if current_user["role"] == UserRole.LECTURER:
        lecturer_courses = db.courses.find({"lecturer_id": str(current_user["_id"])})
        course_ids = [str(course["_id"]) for course in lecturer_courses]
        match_stage["course_id"] = {"$in": course_ids}
    
    if match_stage:
        pipeline.append({"$match": match_stage})
    
    # Group by student and course
    pipeline.append({
        "$group": {
            "_id": {
                "user_id": "$user_id",
                "course_id": "$course_id"
            },
            "attendance_count": {"$sum": 1},
            "face_verified_count": {
                "$sum": {"$cond": [{"$eq": ["$verified_by_face", True]}, 1, 0]}
            },
            "last_attendance": {"$max": "$timestamp"}
        }
    })
    
    # Lookup student info
    pipeline.append({
        "$lookup": {
            "from": "users",
            "localField": "_id.user_id",
            "foreignField": "_id",
            "as": "user"
        }
    })
    
    # Lookup course info
    pipeline.append({
        "$lookup": {
            "from": "courses",
            "localField": "_id.course_id",
            "foreignField": "_id",
            "as": "course"
        }
    })
    
    # Filter by department and level if provided
    if department_id or level:
        lookup_match = {}
        if department_id:
            lookup_match["student_profiles.department_id"] = department_id
        if level:
            lookup_match["student_profiles.level"] = level
        
        pipeline.append({
            "$lookup": {
                "from": "student_profiles",
                "localField": "_id.user_id",
                "foreignField": "user_id",
                "as": "student_profiles"
            }
        })
        
        pipeline.append({
            "$match": lookup_match
        })
    
    # Project the final result
    pipeline.append({
        "$project": {
            "_id": 0,
            "user_id": "$_id.user_id",
            "course_id": "$_id.course_id",
            "student_name": {"$arrayElemAt": ["$user.full_name", 0]},
            "course_name": {"$arrayElemAt": ["$course.name", 0]},
            "attendance_count": 1,
            "face_verified_count": 1,
            "face_verification_percentage": {
                "$multiply": [
                    {"$divide": ["$face_verified_count", "$attendance_count"]},
                    100
                ]
            },
            "last_attendance": 1
        }
    })
    
    # Execute aggregation
    report = list(db.attendance.aggregate(pipeline))
    
    return report 