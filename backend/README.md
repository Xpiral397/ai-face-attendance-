# AI Face Attendance System Backend

This is the backend for the AI Face Attendance System, an AI-powered academic management system with facial recognition for attendance.

## Features

- Facial recognition for authentication and attendance tracking
- Academic structure management (faculties, departments, levels, courses)
- Schedule management with conflict detection
- Attendance tracking and reporting
- Role-based access control (students, lecturers, admins)

## Tech Stack

- **Framework**: FastAPI
- **Database**: MongoDB
- **Face Recognition**: OpenCV and face-recognition library
- **Authentication**: JWT tokens

## Setup

### Prerequisites

- Python 3.8+
- MongoDB
- Virtual environment (recommended)

### Installation

1. Clone the repository
2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   ```
   MONGODB_URI=your_mongodb_connection_string
   JWT_SECRET_KEY=your_secret_key
   ```

### Running the Server

```
uvicorn main:app --reload
```

The API will be available at http://localhost:8000. The API documentation can be accessed at http://localhost:8000/docs.

## API Documentation

### Authentication

- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login with email and password
- `POST /auth/face-login` - Login with face and email
- `POST /auth/register-face` - Register a face for a user

### Academic Management

- `POST /academic/faculty` - Create a faculty
- `GET /academic/faculty` - Get all faculties
- `GET /academic/faculty/{faculty_id}` - Get a faculty by ID
- `PUT /academic/faculty/{faculty_id}` - Update a faculty
- `DELETE /academic/faculty/{faculty_id}` - Delete a faculty

- `POST /academic/department` - Create a department
- `GET /academic/department` - Get all departments
- `GET /academic/department/{department_id}` - Get a department by ID
- `PUT /academic/department/{department_id}` - Update a department
- `DELETE /academic/department/{department_id}` - Delete a department

- `POST /academic/course` - Create a course
- `GET /academic/course` - Get all courses
- `GET /academic/course/{course_id}` - Get a course by ID
- `PUT /academic/course/{course_id}` - Update a course
- `DELETE /academic/course/{course_id}` - Delete a course

### Schedule Management

- `POST /schedule` - Create a schedule
- `GET /schedule` - Get all schedules
- `GET /schedule/{schedule_id}` - Get a schedule by ID
- `PUT /schedule/{schedule_id}` - Update a schedule
- `DELETE /schedule/{schedule_id}` - Delete a schedule
- `POST /schedule/check-conflicts` - Check for schedule conflicts
- `GET /schedule/timetable/student` - Get student timetable
- `GET /schedule/timetable/lecturer` - Get lecturer timetable

### Attendance Management

- `POST /attendance/mark` - Mark attendance
- `GET /attendance/history` - Get attendance history
- `GET /attendance/stats` - Get attendance statistics
- `GET /attendance/report` - Get attendance report

## Models

### User

- Email, password, role (student, lecturer, admin)
- Face encodings for students
- Profile information

### Academic Structure

- Faculties
- Departments (linked to faculties)
- Courses (linked to departments)

### Schedule

- Course, lecturer, department, level
- Time slot (day, start time, end time)
- Room (for physical classes)
- Online link (for online classes)

### Attendance

- User ID, course ID
- Timestamp
- Verification method (face, password)

## Security

- JWT token authentication
- Role-based access control
- Password hashing with bcrypt
- Face verification with face-recognition library 