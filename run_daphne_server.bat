@echo off
echo AI Face Attendance WebSocket Server

:: Activate virtual environment if exists
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

:: Set Django settings
set DJANGO_SETTINGS_MODULE=aifaceattendance.settings

:: Run Daphne ASGI server
echo Starting Daphne ASGI server...
python -m daphne -b 127.0.0.1 -p 8000 aifaceattendance.asgi:application

pause 