from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
import os
import uvicorn

# Import routers
from api.auth.auth_controller import router as auth_router
from api.academic.academic_controller import router as academic_router
from api.schedule.schedule_controller import router as schedule_router
from api.attendance.attendance_controller import router as attendance_router

# Create FastAPI app
app = FastAPI(
    title="AI Face Attendance System",
    description="An AI-powered academic management system with facial recognition",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect to MongoDB
mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
client = MongoClient(mongo_uri)
db = client['attendance_db']

# Make database available to all routers
def get_db():
    return db

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(academic_router, prefix="/academic", tags=["Academic Management"])
app.include_router(schedule_router, prefix="/schedule", tags=["Schedule Management"])
app.include_router(attendance_router, prefix="/attendance", tags=["Attendance Management"])

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the AI Face Attendance System API",
        "documentation": "/docs"
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
