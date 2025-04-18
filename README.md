# AI Face Attendance System

A face recognition-based attendance system built with Django, channels, and WebSockets.

## Setup

1. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Apply migrations:
   ```
   python manage.py migrate
   ```

## Running the System

### Option 1: Using Django's development server (HTTP only)
```
python manage.py runserver
```
This will start the basic Django server at http://127.0.0.1:8000/ 
but WebSockets won't work correctly.

### Option 2: Using Daphne (HTTP + WebSockets, recommended)
```
run_daphne_server.bat
```
This will start the Daphne ASGI server with full WebSocket support at http://127.0.0.1:8000/

## Troubleshooting 404 Errors

If you encounter 404 errors:

1. Make sure you're using the Daphne server (Option 2 above)
2. Access the application at http://127.0.0.1:8000/
3. Check the console for WebSocket connection errors
4. If the WebSocket connection fails, the app will automatically try an alternate connection
5. Make sure your ALLOWED_HOSTS in settings.py includes 'localhost' and '127.0.0.1'

## Routes

- Main application: http://127.0.0.1:8000/
- Face login: http://127.0.0.1:8000/face-login/
- Admin: http://127.0.0.1:8000/admin/
- API docs: http://127.0.0.1:8000/api/docs/
- WebSocket endpoint: ws://127.0.0.1:8000/ws/auth/face/
