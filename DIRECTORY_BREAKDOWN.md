# Directory Structure Breakdown

## Frontend Components

### `/components/auth`
- **LoginForm.tsx**: 
  - Dual-factor authentication UI
  - Email/password fields
  - Face capture interface with webcam integration
  - Responsive design for mobile/desktop
- **FaceCapture.tsx**: 
  - Camera access and face detection
  - Real-time feedback on face positioning
  - Anti-spoofing checks (liveness detection)
  - Error handling for camera permissions

### `/components/dashboard`
- **AdminDashboard.tsx**: 
  - Academic structure management
  - Multi-panel layout with navigation sidebar
  - System statistics and monitoring panels
  - User management interface
  - Schedule conflict visualization
  
- **StudentDashboard.tsx**:
  - Personalized timetable with live ticker
  - Attendance statistics and history
  - Course materials access
  - Upcoming class notifications
  - Face verification for attendance
  
- **LecturerDashboard.tsx**:
  - Teaching schedule overview
  - Class attendance management
  - Course materials upload interface
  - Student performance tracking
  - Real-time class status updates

### `/components/schedule`
- **Timeline.tsx**:
  - Animated timeline showing real-time class schedules
  - Color-coded events (online/physical)
  - Current time indicator with smooth animation
  - Interactive elements for class details
  
- **ConflictDetection.tsx**:
  - Visual indicators for schedule conflicts
  - Tooltips showing conflict details
  - Resolution suggestions
  - Real-time validation

### `/components/attendance`
- **FaceVerification.tsx**:
  - Face capture for attendance verification
  - Match status visualization
  - Success/fail animations
  - Retry mechanisms
  
- **AttendanceReports.tsx**:
  - Tabular and chart visualizations
  - Filtering capabilities
  - Export functionality
  - Performance metrics

## Backend Services

### `/api/auth`
- **auth.controller.ts**:
  - JWT token generation and validation
  - Face verification endpoint
  - Password authentication
  - Session management
  
- **face.service.ts**:
  - Face detection and recognition
  - Encoding storage and comparison
  - Anti-spoofing validation
  - Performance optimization

### `/api/academic`
- **faculty.controller.ts**:
  - CRUD operations for faculties
  - Relationship management with departments
  
- **department.controller.ts**:
  - CRUD operations for departments
  - Course assignments
  - Level management
  
- **course.controller.ts**:
  - Course management
  - Credit hour assignment
  - Lecturer qualification matching

### `/api/schedule`
- **scheduler.controller.ts**:
  - Time slot allocation
  - Conflict detection algorithms
  - Schedule generation
  - Optimization routines
  
- **conflict.service.ts**:
  - Validation rules for scheduling
  - Conflict resolution strategies
  - Real-time checking

### `/api/attendance`
- **attendance.controller.ts**:
  - Attendance marking endpoints
  - Record management
  - Report generation
  - Statistics calculation

## Utility Libraries

### `/lib/face`
- **detector.ts**:
  - Face detection using OpenCV/dlib
  - Optimization for browser environments
  - Webcam integration utilities
  
- **recognition.ts**:
  - Face recognition algorithms
  - Encoding management
  - Comparison utilities

### `/lib/validation`
- **scheduleValidation.ts**:
  - Rules for schedule conflict prevention
  - Time slot validation
  - Resource availability checking

## Database Models

### `/models`
- **User.ts**:
  - Student, lecturer, admin schemas
  - Role-based permissions
  - Face encoding storage
  
- **Academic.ts**:
  - Faculty, department, level schemas
  - Relationships and constraints
  
- **Schedule.ts**:
  - Time slot definitions
  - Assignment relationships
  - Conflict validation rules
  
- **Attendance.ts**:
  - Attendance records
  - Reporting structures
  - Analytics data points

## Page Implementation Details

### `/pages/login.tsx`
- Role-based login UI
- Dual-factor authentication flow
- Error handling and feedback
- Responsive design

### `/pages/admin/dashboard.tsx`
- System-wide statistics
- Navigation to management tools
- Real-time alerts and notifications
- User activity monitoring

### `/pages/admin/faculty.tsx`
- Faculty listing with search/filter
- Creation/editing interface
- Department assignment
- Performance metrics

### `/pages/admin/schedule.tsx`
- Schedule generation interface
- Conflict visualization
- Drag-and-drop time slot assignment
- Optimization tools

### `/pages/student/dashboard.tsx`
- Personalized timetable
- Attendance statistics
- Course material access
- Face verification interface

### `/pages/lecturer/dashboard.tsx`
- Teaching schedule
- Class management tools
- Attendance tracking
- Student performance analytics 