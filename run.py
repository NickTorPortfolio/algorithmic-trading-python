import os
import sys
import subprocess

def install_requirements():
    """Install the required packages from requirements.txt."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    except subprocess.CalledProcessError as e:
        print(f"Failed to install packages: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Automatically install required packages
    install_requirements()

    # Import the app creation function
    from app import create_app

    # Create the Flask app
    app = create_app()

    # Run the app
    app.run(debug=True)
