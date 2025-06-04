#!/usr/bin/env python3
"""Setup script to install required dependencies"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - Success")
            return True
        else:
            print(f"❌ {description} - Failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} - Error: {e}")
        return False

def check_python():
    """Check Python installation"""
    print("🐍 Checking Python...")
    version = sys.version_info
    print(f"   Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 8:
        print("✅ Python version is compatible")
        return True
    else:
        print("❌ Python 3.8+ required")
        return False

def install_dependencies():
    """Install required dependencies"""
    print("\n🔧 INSTALLING DEPENDENCIES")
    print("=" * 40)
    
    # Check if we can use pip
    pip_commands = ['pip3', 'pip', 'python3 -m pip', 'python -m pip']
    working_pip = None
    
    for pip_cmd in pip_commands:
        if run_command(f"{pip_cmd} --version", f"Testing {pip_cmd}"):
            working_pip = pip_cmd
            break
    
    if not working_pip:
        print("❌ No working pip found. Trying alternative installation methods...")
        
        # Try apt-get for Ubuntu/Debian
        if run_command("which apt-get", "Checking for apt-get"):
            print("📦 Using apt-get to install packages...")
            commands = [
                "apt-get update",
                "apt-get install -y python3-pip",
                "apt-get install -y python3-flask",
                "apt-get install -y python3-flask-cors"
            ]
            
            for cmd in commands:
                if not run_command(f"sudo {cmd}", f"Running {cmd}"):
                    print(f"⚠️ Failed to run {cmd}, trying without sudo...")
                    run_command(cmd, f"Running {cmd} without sudo")
        
        # Try yum for CentOS/RHEL
        elif run_command("which yum", "Checking for yum"):
            print("📦 Using yum to install packages...")
            commands = [
                "yum update -y",
                "yum install -y python3-pip",
                "yum install -y python3-flask"
            ]
            
            for cmd in commands:
                run_command(f"sudo {cmd}", f"Running {cmd}")
        
        else:
            print("❌ No package manager found. Manual installation required.")
            return False
    
    else:
        print(f"✅ Using {working_pip} for installation")
        
        # Install required packages
        packages = [
            "flask",
            "flask-cors",
            "requests",
            "werkzeug"
        ]
        
        for package in packages:
            run_command(f"{working_pip} install {package}", f"Installing {package}")
    
    return True

def test_installation():
    """Test if installation was successful"""
    print("\n🧪 TESTING INSTALLATION")
    print("=" * 30)
    
    test_imports = [
        ("flask", "Flask"),
        ("flask_cors", "Flask-CORS"),
        ("werkzeug.utils", "Werkzeug"),
        ("sqlite3", "SQLite3"),
        ("requests", "Requests")
    ]
    
    all_good = True
    for module, name in test_imports:
        try:
            __import__(module)
            print(f"✅ {name} - Available")
        except ImportError:
            print(f"❌ {name} - Missing")
            all_good = False
    
    return all_good

def test_app_startup():
    """Test if the app can start properly"""
    print("\n🚀 TESTING APP STARTUP")
    print("=" * 25)
    
    try:
        # Test importing the main modules
        sys.path.append('/home/ggrun/CybrScan_1')
        
        print("   Testing client blueprint import...")
        from client import client_bp
        print("✅ Client blueprint imported successfully")
        
        print("   Testing auth routes import...")
        from auth_routes import auth_bp
        print("✅ Auth routes imported successfully")
        
        print("   Testing admin import...")
        from admin import admin_bp
        print("✅ Admin blueprint imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ App startup test failed: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def main():
    """Main setup function"""
    print("🔧 CYBRSCAN DEPENDENCY SETUP")
    print("=" * 35)
    
    # Check Python
    if not check_python():
        print("❌ Python version incompatible. Please upgrade to Python 3.8+")
        return False
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Dependency installation failed")
        return False
    
    # Test installation
    if not test_installation():
        print("❌ Some dependencies are still missing")
        print("\n🔧 MANUAL INSTALLATION REQUIRED:")
        print("   pip3 install flask flask-cors requests werkzeug")
        print("   OR")
        print("   sudo apt-get install python3-flask python3-pip")
        return False
    
    # Test app startup
    if not test_app_startup():
        print("❌ App startup test failed")
        return False
    
    print("\n🎉 SETUP COMPLETE!")
    print("✅ All dependencies installed successfully")
    print("✅ App modules can be imported")
    print("\n🚀 Next steps:")
    print("   1. python3 app.py  (start the application)")
    print("   2. Go to: http://localhost:5000")
    print("   3. Login and test the client dashboard")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)