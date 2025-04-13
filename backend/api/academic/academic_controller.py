from fastapi import APIRouter, HTTPException, Depends, status, Body, Path, Query
from pymongo import MongoClient
from bson import ObjectId
import os
from datetime import datetime
from typing import List, Optional
from pydantic import EmailStr

from models.user import UserRole, Faculty, Department, Course
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

# Faculty endpoints
@router.post("/faculty", status_code=status.HTTP_201_CREATED)
async def create_faculty(
    faculty_data: Faculty,
    current_user = Depends(admin_only)
):
    """
    Create a new faculty
    """
    # Check if faculty already exists
    existing = db.faculties.find_one({"name": faculty_data.name})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Faculty with this name already exists"
        )
    
    # Create faculty
    faculty_dict = faculty_data.dict()
    faculty_dict["created_at"] = datetime.now()
    faculty_dict["updated_at"] = datetime.now()
    
    result = db.faculties.insert_one(faculty_dict)
    faculty_dict["id"] = str(result.inserted_id)
    
    return faculty_dict

@router.get("/faculty")
async def get_faculties():
    """
    Get all faculties
    """
    faculties = list(db.faculties.find())
    for faculty in faculties:
        faculty["id"] = str(faculty["_id"])
        del faculty["_id"]
    
    return faculties

@router.get("/faculty/{faculty_id}")
async def get_faculty(faculty_id: str = Path(...)):
    """
    Get a faculty by ID
    """
    faculty = db.faculties.find_one({"_id": ObjectId(faculty_id)})
    if not faculty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Faculty not found"
        )
    
    faculty["id"] = str(faculty["_id"])
    del faculty["_id"]
    
    return faculty

@router.put("/faculty/{faculty_id}")
async def update_faculty(
    faculty_data: Faculty,
    faculty_id: str = Path(...),
    current_user = Depends(admin_only)
):
    """
    Update a faculty
    """
    faculty = db.faculties.find_one({"_id": ObjectId(faculty_id)})
    if not faculty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Faculty not found"
        )
    
    # Update faculty
    faculty_dict = faculty_data.dict()
    faculty_dict["updated_at"] = datetime.now()
    
    db.faculties.update_one(
        {"_id": ObjectId(faculty_id)},
        {"$set": faculty_dict}
    )
    
    faculty_dict["id"] = faculty_id
    
    return faculty_dict

@router.delete("/faculty/{faculty_id}")
async def delete_faculty(
    faculty_id: str = Path(...),
    current_user = Depends(admin_only)
):
    """
    Delete a faculty
    """
    faculty = db.faculties.find_one({"_id": ObjectId(faculty_id)})
    if not faculty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Faculty not found"
        )
    
    # Check if faculty has departments
    departments = db.departments.find_one({"faculty_id": faculty_id})
    if departments:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete faculty with departments"
        )
    
    db.faculties.delete_one({"_id": ObjectId(faculty_id)})
    
    return {"message": "Faculty deleted successfully"}

# Department endpoints
@router.post("/department", status_code=status.HTTP_201_CREATED)
async def create_department(
    department_data: Department,
    current_user = Depends(admin_only)
):
    """
    Create a new department
    """
    # Check if faculty exists
    faculty = db.faculties.find_one({"_id": ObjectId(department_data.faculty_id)})
    if not faculty:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Faculty not found"
        )
    
    # Check if department already exists
    existing = db.departments.find_one({
        "name": department_data.name,
        "faculty_id": department_data.faculty_id
    })
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Department with this name already exists in this faculty"
        )
    
    # Create department
    department_dict = department_data.dict()
    department_dict["created_at"] = datetime.now()
    department_dict["updated_at"] = datetime.now()
    
    result = db.departments.insert_one(department_dict)
    department_dict["id"] = str(result.inserted_id)
    
    return department_dict

@router.get("/department")
async def get_departments(
    faculty_id: Optional[str] = None
):
    """
    Get all departments
    Optionally filtered by faculty_id
    """
    # Build query
    query = {}
    if faculty_id:
        query["faculty_id"] = faculty_id
    
    departments = list(db.departments.find(query))
    for department in departments:
        department["id"] = str(department["_id"])
        del department["_id"]
    
    return departments

@router.get("/department/{department_id}")
async def get_department(department_id: str = Path(...)):
    """
    Get a department by ID
    """
    department = db.departments.find_one({"_id": ObjectId(department_id)})
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    
    department["id"] = str(department["_id"])
    del department["_id"]
    
    return department

@router.put("/department/{department_id}")
async def update_department(
    department_data: Department,
    department_id: str = Path(...),
    current_user = Depends(admin_only)
):
    """
    Update a department
    """
    department = db.departments.find_one({"_id": ObjectId(department_id)})
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    
    # Update department
    department_dict = department_data.dict()
    department_dict["updated_at"] = datetime.now()
    
    db.departments.update_one(
        {"_id": ObjectId(department_id)},
        {"$set": department_dict}
    )
    
    department_dict["id"] = department_id
    
    return department_dict

@router.delete("/department/{department_id}")
async def delete_department(
    department_id: str = Path(...),
    current_user = Depends(admin_only)
):
    """
    Delete a department
    """
    department = db.departments.find_one({"_id": ObjectId(department_id)})
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    
    # Check if department has courses
    courses = db.courses.find_one({"department_id": department_id})
    if courses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete department with courses"
        )
    
    db.departments.delete_one({"_id": ObjectId(department_id)})
    
    return {"message": "Department deleted successfully"}

# Course endpoints
@router.post("/course", status_code=status.HTTP_201_CREATED)
async def create_course(
    course_data: Course,
    current_user = Depends(admin_only)
):
    """
    Create a new course
    """
    # Check if department exists
    department = db.departments.find_one({"_id": ObjectId(course_data.department_id)})
    if not department:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Department not found"
        )
    
    # Check if course already exists
    existing = db.courses.find_one({
        "code": course_data.code,
        "department_id": course_data.department_id
    })
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course with this code already exists in this department"
        )
    
    # Create course
    course_dict = course_data.dict()
    course_dict["created_at"] = datetime.now()
    course_dict["updated_at"] = datetime.now()
    
    result = db.courses.insert_one(course_dict)
    course_dict["id"] = str(result.inserted_id)
    
    return course_dict

@router.get("/course")
async def get_courses(
    department_id: Optional[str] = None,
    level: Optional[int] = None
):
    """
    Get all courses
    Optionally filtered by department_id and level
    """
    # Build query
    query = {}
    if department_id:
        query["department_id"] = department_id
    if level:
        query["levels"] = level
    
    courses = list(db.courses.find(query))
    for course in courses:
        course["id"] = str(course["_id"])
        del course["_id"]
    
    return courses

@router.get("/course/{course_id}")
async def get_course(course_id: str = Path(...)):
    """
    Get a course by ID
    """
    course = db.courses.find_one({"_id": ObjectId(course_id)})
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    course["id"] = str(course["_id"])
    del course["_id"]
    
    return course

@router.put("/course/{course_id}")
async def update_course(
    course_data: Course,
    course_id: str = Path(...),
    current_user = Depends(admin_only)
):
    """
    Update a course
    """
    course = db.courses.find_one({"_id": ObjectId(course_id)})
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Update course
    course_dict = course_data.dict()
    course_dict["updated_at"] = datetime.now()
    
    db.courses.update_one(
        {"_id": ObjectId(course_id)},
        {"$set": course_dict}
    )
    
    course_dict["id"] = course_id
    
    return course_dict

@router.delete("/course/{course_id}")
async def delete_course(
    course_id: str = Path(...),
    current_user = Depends(admin_only)
):
    """
    Delete a course
    """
    course = db.courses.find_one({"_id": ObjectId(course_id)})
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Check if course is assigned to schedules
    schedules = db.schedules.find_one({"course_id": course_id})
    if schedules:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete course assigned to schedules"
        )
    
    db.courses.delete_one({"_id": ObjectId(course_id)})
    
    return {"message": "Course deleted successfully"} 