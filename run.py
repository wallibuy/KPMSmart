#!/usr/bin/env python3
"""
KPMS TRUST - Quick Start Launcher
Simple launcher script for the complete working system
"""

import subprocess
import sys
import os

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required!")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} detected")

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ All packages installed successfully!")
    except subprocess.CalledProcessError:
        print("❌ Failed to install packages. Please run: pip install -r requirements.txt")
        sys.exit(1)

def run_application():
    """Start the Flask application"""
    print("🚀 Starting KPMS TRUST application...")
    print("📍 Open your browser to: http://localhost:5000")
    print("👤 Login credentials:")
    print("   Admin: admin / adminpass")
    print("   Stores: store01-31 / 123")
    print("\nPress Ctrl+C to stop the server\n")
    
    try:
        # Import and run the app
        from app import app
        app.run(host='0.0.0.0', port=5000, debug=False)
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure all requirements are installed.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Application stopped.")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🏪 KPMS TRUST - Complete Working System")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Install requirements
    install_requirements()
    
    # Run the application
    run_application()