@echo off
echo AI Face Attendance System

:: Activate virtual environment if exists
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

:: Start the Django development server
echo Starting Django development server...
python manage.py runserver

pause 