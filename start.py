#!/usr/bin/env python3
"""
Startup script for the Travel Itinerary Generator
This script checks for dependencies, sets up the environment, and starts the application.
"""

import os
import sys
import subprocess
import importlib.util
from pathlib import Path

def check_package_installed(package_name):
    """Check if a Python package is installed."""
    return importlib.util.find_spec(package_name) is not None

def setup_environment():
    """Set up the project environment."""
    print("Checking environment setup...")
    
    # Check for required packages
    required_packages = [
        "fastapi", "uvicorn", "pydantic", "dotenv", 
        "jinja2", "aiohttp", "pydantic_ai"
    ]
    
    missing_packages = []
    for package in required_packages:
        if not check_package_installed(package):
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Missing required packages: {', '.join(missing_packages)}")
        print("Installing missing packages...")
        
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("Packages installed successfully.")
        except subprocess.CalledProcessError:
            print("Error installing packages. Please run: pip install -r requirements.txt")
            return False
    
    # Check for project structure
    project_dirs = ["templates", "static", "cache"]
    missing_dirs = []
    
    for directory in project_dirs:
        if not os.path.exists(directory):
            missing_dirs.append(directory)
    
    if missing_dirs:
        print(f"Missing required directories: {', '.join(missing_dirs)}")
        print("Setting up project structure...")
        
        try:
            if os.path.exists("project_structure.py"):
                subprocess.check_call([sys.executable, "project_structure.py"])
            else:
                for directory in missing_dirs:
                    os.makedirs(directory, exist_ok=True)
                
                if "templates" in missing_dirs and os.path.exists("index.html"):
                    os.makedirs("templates", exist_ok=True)
                    with open("index.html", "r") as source:
                        with open("templates/index.html", "w") as target:
                            target.write(source.read())
        except Exception as e:
            print(f"Error setting up project structure: {e}")
            return False
    
    # Check for .env file
    if not os.path.exists(".env"):
        if os.path.exists(".env.example"):
            print("Creating .env file from .env.example...")
            with open(".env.example", "r") as source:
                with open(".env", "w") as target:
                    target.write(source.read())
            print("Created .env file. Please edit it to add your API keys.")
        else:
            print("Warning: No .env file found. Creating a basic one...")
            with open(".env", "w") as env_file:
                env_file.write("# Add your API keys here\nGROQ_API_KEY=your_groq_api_key_here\n")
            print("Created basic .env file. Please add your GROQ_API_KEY.")
    
    return True

def start_application():
    """Start the FastAPI application."""
    print("\nStarting Travel Itinerary Generator...")
    
    try:
        subprocess.check_call([sys.executable, "main.py"])
    except KeyboardInterrupt:
        print("\nApplication stopped.")
    except Exception as e:
        print(f"\nError starting application: {e}")
        print("Try running 'uvicorn main:app --reload' manually.")

if __name__ == "__main__":
    print("=" * 60)
    print("Travel Itinerary Generator Setup")
    print("=" * 60)
    
    if setup_environment():
        start_application()
    else:
        print("\nEnvironment setup failed. Please resolve the issues and try again.")
        sys.exit(1)