import os
import sys
import subprocess

def main():
    # Set the Django settings module environment variable
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Dongelek.settings")
    
    # Construct the command to run daphne
    cmd = [
        sys.executable, 
        "-m", 
        "daphne",
        "-p", 
        "8000", 
        "Dongelek.asgi:application"
    ]
    
    print("Starting Daphne server...")
    print(f"Command: {' '.join(cmd)}")
    
    # Run daphne as a subprocess
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\nDaphne server stopped")
    except subprocess.CalledProcessError as e:
        print(f"Error running Daphne: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
