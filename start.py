#!/usr/bin/env python3
"""
Salescoach Startup Script
This script helps you get started with Salescoach quickly by checking dependencies
and guiding you through the setup process.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.8 or higher"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_env_file():
    """Check if .env file exists and has OpenAI API key"""
    env_file = Path('.env')
    
    if not env_file.exists():
        print("❌ .env file not found")
        # Create a template .env file
        try:
            with open('.env', 'w') as f:
                f.write('OPENAI_API_KEY=your_openai_api_key_here\n')
            print("✅ Created .env template file")
        except Exception as e:
            print(f"❌ Could not create .env file: {e}")
            return False
    
    # Check if API key is set
    with open('.env', 'r') as f:
        content = f.read()
        if 'OPENAI_API_KEY=your_openai_api_key_here' in content or 'OPENAI_API_KEY=' not in content:
            print("❌ OpenAI API key not configured")
            print("📝 Please update your .env file with a valid OpenAI API key:")
            print("   Edit .env and replace 'your_openai_api_key_here' with your actual API key")
            return False
    
    print("✅ .env file configured")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    try:
        import flask
        import openai
        import dotenv
        print("✅ All dependencies installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e.name}")
        print("📦 Installing dependencies...")
        
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            print("💡 Try running: pip install -r requirements.txt")
            return False

def create_uploads_dir():
    """Create uploads directory if it doesn't exist"""
    uploads_dir = Path('uploads')
    if not uploads_dir.exists():
        uploads_dir.mkdir()
        print("✅ Created uploads directory")
    else:
        print("✅ Uploads directory exists")

def main():
    """Main startup function"""
    print("🚀 Salescoach Startup Checker")
    print("=" * 40)
    
    # Check all requirements
    checks = [
        check_python_version(),
        check_dependencies(),
        check_env_file(),
    ]
    
    create_uploads_dir()
    
    print("\n" + "=" * 40)
    
    if all(checks):
        print("✅ All checks passed! Starting Salescoach...")
        print("\n🌐 Opening Salescoach at http://localhost:5000")
        print("📖 Press Ctrl+C to stop the server")
        print("=" * 40)
        
        # Import and run the Flask app
        try:
            from app import app
            app.run(debug=True, host='0.0.0.0', port=5000)
        except KeyboardInterrupt:
            print("\n👋 Salescoach stopped. Thanks for using it!")
        except Exception as e:
            print(f"❌ Error starting application: {e}")
    else:
        print("❌ Some checks failed. Please fix the issues above and try again.")
        print("\n💡 Quick setup guide:")
        print("   1. Install Python 3.8+")
        print("   2. Run: pip install -r requirements.txt")
        print("   3. Edit .env file with your OpenAI API key")
        print("   4. Run: python start.py")

if __name__ == "__main__":
    main() 