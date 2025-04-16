"""
Start the WebSocket server with Daphne for ASGI support
"""
import os
import sys
import subprocess

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aifaceattendance.settings')

def main():
    # Command to run Daphne with the ASGI application
    command = [
        sys.executable,
        "-m",
        "daphne",
        "-b",
        "127.0.0.1",
        "-p",
        "8000",
        "aifaceattendance.asgi:application"
    ]
    
    print("Starting WebSocket server with Daphne...")
    print("Access the application at: http://127.0.0.1:8000/")
    print("WebSocket endpoint at: ws://127.0.0.1:8000/ws/auth/face/")
    print("Press Ctrl+C to stop the server")
    
    # Run the Daphne server
    try:
        subprocess.run(command)
    except KeyboardInterrupt:
        print("\nShutting down server...")
    
if __name__ == "__main__":
    main() 