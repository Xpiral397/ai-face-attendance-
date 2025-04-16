@echo off
echo AI Face Attendance WebSocket Server

:: Activate virtual environment if exists
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

:: Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

:: Apply migrations
echo Applying migrations...
python manage.py migrate

:: Run server with WebSocket support
echo Starting server with WebSocket support...
daphne -b 127.0.0.1 -p 8000 aifaceattendance.asgi:application

pause 