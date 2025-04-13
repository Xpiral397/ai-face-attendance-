from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    STUDENT = "student"
    LECTURER = "lecturer"
    ADMIN = "admin"

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class UserCreate(UserBase):
    password: str
    
class UserInDB(UserBase):
    id: str
    hashed_password: str
    
class User(UserBase):
    id: str
    
class StudentProfile(BaseModel):
    user_id: str
    department_id: str
    level: int
    matric_number: str
    courses: List[str] = []
    
class LecturerProfile(BaseModel):
    user_id: str
    departments: List[str] = []
    levels: List[int] = []
    subjects: List[str] = []
    
class FaceEncoding(BaseModel):
    user_id: str
    encoding: List[float]
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
class AttendanceRecord(BaseModel):
    user_id: str
    course_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    verified_by_face: bool = False
    
class Department(BaseModel):
    id: str
    name: str
    faculty_id: str
    levels: List[int] = []
    
class Faculty(BaseModel):
    id: str
    name: str
    
class Course(BaseModel):
    id: str
    code: str
    name: str
    department_id: str
    levels: List[int] = []
    credit_hours: int = 3
    
class TimeSlot(BaseModel):
    day: str
    start_time: str
    end_time: str
    type: str  # "Physical" or "Online"
    
class Schedule(BaseModel):
    id: str
    lecturer_id: str
    course_id: str
    department_id: str
    level: int
    time_slot: TimeSlot
    room: Optional[str] = None
    online_link: Optional[str] = None 