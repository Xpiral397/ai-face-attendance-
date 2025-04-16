#!/bin/bash

# Activate virtual environment if exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Install required packages
echo "Installing dependencies..."
pip install -r requirements.txt

# Apply migrations
echo "Applying migrations..."
python manage.py migrate

# Run the server with Daphne (ASGI server for WebSockets)
echo "Starting server with WebSocket support..."
daphne -b 127.0.0.1 -p 8000 aifaceattendance.asgi:application 