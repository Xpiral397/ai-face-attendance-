from fastapi import APIRouter, HTTPException, Depends, status, Body, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from pymongo import MongoClient
from bson import ObjectId
import os
from datetime import datetime, timedelta
from pydantic import BaseModel, EmailStr
from typing import Optional

from models.user import UserRole, User, UserCreate, UserInDB
from utils.jwt_utils import create_access_token, decode_token
from services.face_service import verify_face, encode_face

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# MongoDB connection
client = MongoClient(os.getenv("MONGODB_URI", "mongodb://localhost:27017"))
db = client["attendance_db"]

class Token(BaseModel):
    access_token: str
    token_type: str
    role: UserRole

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class FaceLoginRequest(BaseModel):
    email: EmailStr
    face_image: bytes

def get_user(email: str):
    user_data = db.users.find_one({"email": email})
    if user_data:
        return user_data
    return None

def authenticate_user(email: str, password: str):
    user = get_user(email)
    if not user:
        return False
    if not pwd_context.verify(password, user["hashed_password"]):
        return False
    return user

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = decode_token(token)
        email = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = get_user(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

@router.post("/register", response_model=User)
async def register_user(user_data: UserCreate = Body(...)):
    # Check if user already exists
    if get_user(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Hash the password
    hashed_password = pwd_context.hash(user_data.password)
    
    # Create user document
    user_dict = user_data.dict()
    user_dict.pop("password")
    user_dict["hashed_password"] = hashed_password
    user_dict["created_at"] = datetime.now()
    user_dict["updated_at"] = datetime.now()
    
    # Insert into database
    result = db.users.insert_one(user_dict)
    user_dict["id"] = str(result.inserted_id)
    
    return user_dict

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user["email"]})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user["role"]
    }

@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest):
    user = authenticate_user(login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    access_token = create_access_token(data={"sub": user["email"]})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user["role"]
    }

@router.post("/face-login", response_model=Token)
async def face_login(request: FaceLoginRequest):
    # Find user by email
    user = get_user(request.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Verify face
    if not verify_face(request.face_image, str(user["_id"])):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Face verification failed"
        )
    
    # Generate token
    access_token = create_access_token(data={"sub": user["email"]})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user["role"]
    }

@router.post("/register-face")
async def register_face(face_image: bytes = Body(...), current_user = Depends(get_current_user)):
    # Only students register face
    if current_user["role"] != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can register face"
        )
    
    # Encode and store face
    success = encode_face(face_image, str(current_user["_id"]))
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to encode face. Please try again with a clearer image."
        )
    
    return {"message": "Face registered successfully"}
