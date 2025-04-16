import os
import sys
import django

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aifaceattendance.settings")
    django.setup()  # Set up Django before importing any models
    
    sys.argv = ["daphne", "-b", "127.0.0.1", "-p", "8000", "aifaceattendance.asgi:application"]
    
    try:
        from daphne.cli import CommandLineInterface
        CommandLineInterface.entrypoint()
    except ImportError as e:
        print(f"Error importing Daphne: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error running Daphne server: {e}")
        sys.exit(1) 