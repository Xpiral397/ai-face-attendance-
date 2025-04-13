from fastapi import APIRouter, HTTPException, Depends, status, Body, Path, Query
from pymongo import MongoClient
from bson import ObjectId
import os
from datetime import datetime, time
from typing import List, Optional

from models.user import UserRole, TimeSlot, Schedule
from api.auth.auth_controller import get_current_user

router = APIRouter()

# MongoDB connection
client = MongoClient(os.getenv("MONGODB_URI", "mongodb://localhost:27017"))
db = client["attendance_db"]

# Helper function to check if user is admin
def admin_only(current_user = Depends(get_current_user)):
    if current_user["role"] != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can perform this action"
        )
    return current_user

# Helper function to convert time string to datetime.time object
def parse_time(time_str: str) -> time:
    return datetime.strptime(time_str, "%H:%M").time()

# Function to check schedule conflicts
def check_conflicts(schedule_data: dict, ignore_id: str = None) -> List[dict]:
    conflicts = []
    
    # Parse time strings to datetime.time objects for comparison
    start_time = parse_time(schedule_data["time_slot"]["start_time"])
    end_time = parse_time(schedule_data["time_slot"]["end_time"])
    
    # Potentially conflicting schedules query
    query = {
        "time_slot.day": schedule_data["time_slot"]["day"]
    }
    
    if ignore_id:
        query["_id"] = {"$ne": ObjectId(ignore_id)}
    
    # Find potential conflicts
    potential_conflicts = db.schedules.find(query)
    
    for conflict in potential_conflicts:
        conflict_start = parse_time(conflict["time_slot"]["start_time"])
        conflict_end = parse_time(conflict["time_slot"]["end_time"])
        
        # Check if times overlap
        if (start_time <= conflict_end and end_time >= conflict_start):
            # Check specific conflicts
            
            # Lecturer conflict
            if conflict["lecturer_id"] == schedule_data["lecturer_id"]:
                conflicts.append({
                    "type": "LECTURER",
                    "message": "Lecturer is already scheduled at this time",
                    "conflicting_schedule": conflict
                })
            
            # Room conflict (for physical classes)
            if (schedule_data["time_slot"]["type"] == "Physical" and 
                conflict["time_slot"]["type"] == "Physical" and
                schedule_data.get("room") and conflict.get("room") and
                schedule_data["room"] == conflict["room"]):
                conflicts.append({
                    "type": "ROOM",
                    "message": "Room is already scheduled at this time",
                    "conflicting_schedule": conflict
                })
            
            # Level conflict (same department, same level)
            if (conflict["department_id"] == schedule_data["department_id"] and
                conflict["level"] == schedule_data["level"]):
                conflicts.append({
                    "type": "LEVEL",
                    "message": "Students in this level already have a class at this time",
                    "conflicting_schedule": conflict
                })
    
    return conflicts

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_schedule(
    schedule_data: Schedule,
    current_user = Depends(admin_only)
):
    """
    Create a new schedule
    Checks for conflicts before creation
    """
    # Check if course exists
    course = db.courses.find_one({"_id": ObjectId(schedule_data.course_id)})
    if not course:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course not found"
        )
    
    # Check if lecturer exists
    lecturer = db.users.find_one({
        "_id": ObjectId(schedule_data.lecturer_id),
        "role": UserRole.LECTURER
    })
    if not lecturer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lecturer not found"
        )
    
    # Check if department exists
    department = db.departments.find_one({"_id": ObjectId(schedule_data.department_id)})
    if not department:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Department not found"
        )
    
    # Check conflicts
    schedule_dict = schedule_data.dict()
    conflicts = check_conflicts(schedule_dict)
    
    if conflicts:
        return {
            "success": False,
            "conflicts": conflicts
        }
    
    # Create schedule
    schedule_dict["created_at"] = datetime.now()
    schedule_dict["updated_at"] = datetime.now()
    
    result = db.schedules.insert_one(schedule_dict)
    schedule_dict["id"] = str(result.inserted_id)
    
    return {
        "success": True,
        "schedule": schedule_dict
    }

@router.get("/")
async def get_schedules(
    department_id: Optional[str] = None,
    level: Optional[int] = None,
    lecturer_id: Optional[str] = None,
    course_id: Optional[str] = None,
    day: Optional[str] = None
):
    """
    Get all schedules
    Optionally filtered by department_id, level, lecturer_id, course_id, and day
    """
    # Build query
    query = {}
    if department_id:
        query["department_id"] = department_id
    if level:
        query["level"] = level
    if lecturer_id:
        query["lecturer_id"] = lecturer_id
    if course_id:
        query["course_id"] = course_id
    if day:
        query["time_slot.day"] = day
    
    schedules = list(db.schedules.find(query))
    for schedule in schedules:
        schedule["id"] = str(schedule["_id"])
        del schedule["_id"]
    
    return schedules

@router.get("/{schedule_id}")
async def get_schedule(schedule_id: str = Path(...)):
    """
    Get a schedule by ID
    """
    schedule = db.schedules.find_one({"_id": ObjectId(schedule_id)})
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )
    
    schedule["id"] = str(schedule["_id"])
    del schedule["_id"]
    
    return schedule

@router.put("/{schedule_id}")
async def update_schedule(
    schedule_data: Schedule,
    schedule_id: str = Path(...),
    current_user = Depends(admin_only)
):
    """
    Update a schedule
    Checks for conflicts before update
    """
    schedule = db.schedules.find_one({"_id": ObjectId(schedule_id)})
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )
    
    # Check conflicts
    schedule_dict = schedule_data.dict()
    conflicts = check_conflicts(schedule_dict, schedule_id)
    
    if conflicts:
        return {
            "success": False,
            "conflicts": conflicts
        }
    
    # Update schedule
    schedule_dict["updated_at"] = datetime.now()
    
    db.schedules.update_one(
        {"_id": ObjectId(schedule_id)},
        {"$set": schedule_dict}
    )
    
    schedule_dict["id"] = schedule_id
    
    return {
        "success": True,
        "schedule": schedule_dict
    }

@router.delete("/{schedule_id}")
async def delete_schedule(
    schedule_id: str = Path(...),
    current_user = Depends(admin_only)
):
    """
    Delete a schedule
    """
    schedule = db.schedules.find_one({"_id": ObjectId(schedule_id)})
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )
    
    db.schedules.delete_one({"_id": ObjectId(schedule_id)})
    
    return {"message": "Schedule deleted successfully"}

@router.post("/check-conflicts")
async def check_schedule_conflicts(
    schedule_data: Schedule,
    schedule_id: Optional[str] = None,
    current_user = Depends(admin_only)
):
    """
    Check for schedule conflicts without saving
    """
    conflicts = check_conflicts(schedule_data.dict(), schedule_id)
    
    return {
        "has_conflicts": bool(conflicts),
        "conflicts": conflicts
    }

@router.get("/timetable/student")
async def get_student_timetable(
    day: Optional[str] = None,
    current_user = Depends(get_current_user)
):
    """
    Get timetable for a student
    """
    # Check if user is a student
    if current_user["role"] != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can access student timetable"
        )
    
    # Get student profile
    student_profile = db.student_profiles.find_one({"user_id": str(current_user["_id"])})
    if not student_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found"
        )
    
    # Build query
    query = {
        "department_id": student_profile["department_id"],
        "level": student_profile["level"]
    }
    if day:
        query["time_slot.day"] = day
    
    # Get schedules
    schedules = list(db.schedules.find(query))
    
    # Enhance schedules with course and lecturer info
    for schedule in schedules:
        schedule["id"] = str(schedule["_id"])
        del schedule["_id"]
        
        # Add course info
        course = db.courses.find_one({"_id": ObjectId(schedule["course_id"])})
        if course:
            schedule["course"] = {
                "id": str(course["_id"]),
                "code": course["code"],
                "name": course["name"]
            }
        
        # Add lecturer info
        lecturer = db.users.find_one({"_id": ObjectId(schedule["lecturer_id"])})
        if lecturer:
            schedule["lecturer"] = {
                "id": str(lecturer["_id"]),
                "name": lecturer["full_name"]
            }
    
    return schedules

@router.get("/timetable/lecturer")
async def get_lecturer_timetable(
    day: Optional[str] = None,
    current_user = Depends(get_current_user)
):
    """
    Get timetable for a lecturer
    """
    # Check if user is a lecturer
    if current_user["role"] != UserRole.LECTURER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only lecturers can access lecturer timetable"
        )
    
    # Build query
    query = {
        "lecturer_id": str(current_user["_id"])
    }
    if day:
        query["time_slot.day"] = day
    
    # Get schedules
    schedules = list(db.schedules.find(query))
    
    # Enhance schedules with course and department info
    for schedule in schedules:
        schedule["id"] = str(schedule["_id"])
        del schedule["_id"]
        
        # Add course info
        course = db.courses.find_one({"_id": ObjectId(schedule["course_id"])})
        if course:
            schedule["course"] = {
                "id": str(course["_id"]),
                "code": course["code"],
                "name": course["name"]
            }
        
        # Add department info
        department = db.departments.find_one({"_id": ObjectId(schedule["department_id"])})
        if department:
            schedule["department"] = {
                "id": str(department["_id"]),
                "name": department["name"]
            }
    
    return schedules 