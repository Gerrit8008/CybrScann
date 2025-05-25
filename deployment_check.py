#!/usr/bin/env python3
"""
Deployment readiness check for CybrScan
"""

import os
import ast
import json

def check_syntax_all():
    """Check syntax of all Python files"""
    python_files = [
        'app.py',
        'client_db.py', 
        'scanner_deployment.py',
        'scan.py',
        'auth.py',
        'database_utils.py'
    ]
    
    print("🔍 Checking Python syntax...")
    syntax_ok = True
    
    for filename in python_files:
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    ast.parse(f.read())
                print(f"  ✅ {filename}")
            except SyntaxError as e:
                print(f"  ❌ {filename}: Line {e.lineno} - {e.msg}")
                syntax_ok = False
            except Exception as e:
                print(f"  ⚠️ {filename}: {e}")
        else:
            print(f"  ⚠️ {filename}: File not found")
    
    return syntax_ok

def check_requirements():
    """Check requirements.txt exists"""
    print("\n📦 Checking requirements...")
    if os.path.exists('requirements.txt'):
        with open('requirements.txt', 'r') as f:
            reqs = f.read()
            essential_packages = ['flask', 'gunicorn']
            
            for package in essential_packages:
                if package in reqs.lower():
                    print(f"  ✅ {package}")
                else:
                    print(f"  ❌ {package} missing")
            return True
    else:
        print("  ❌ requirements.txt not found")
        return False

def check_entry_point():
    """Check app entry point"""
    print("\n🚀 Checking entry point...")
    try:
        with open('app.py', 'r') as f:
            content = f.read()
            
        if 'app = Flask(__name__)' in content:
            print("  ✅ Flask app instance found")
        else:
            print("  ❌ Flask app instance not found")
            return False
            
        if 'if __name__ == ' in content:
            print("  ✅ Main entry point found")
        else:
            print("  ❌ Main entry point not found")
            return False
            
        # Check for duplicate main blocks
        main_count = content.count('if __name__ == ')
        if main_count == 1:
            print("  ✅ Single main entry point")
        else:
            print(f"  ⚠️ Multiple main entry points found: {main_count}")
            
        return True
        
    except Exception as e:
        print(f"  ❌ Error checking entry point: {e}")
        return False

def check_database_files():
    """Check database files"""
    print("\n🗄️ Checking database files...")
    db_files = ['client_scanner.db', 'cybrscan.db', 'leads.db']
    
    for db_file in db_files:
        if os.path.exists(db_file):
            print(f"  ✅ {db_file} exists")
        else:
            print(f"  ⚠️ {db_file} will be created on first run")

def check_templates():
    """Check critical templates"""
    print("\n📄 Checking templates...")
    critical_templates = [
        'templates/scan.html',
        'templates/results.html', 
        'templates/client/scanner-create.html'
    ]
    
    templates_ok = True
    for template in critical_templates:
        if os.path.exists(template):
            print(f"  ✅ {template}")
        else:
            print(f"  ❌ {template} missing")
            templates_ok = False
    
    return templates_ok

def check_static_files():
    """Check static files"""
    print("\n📁 Checking static files...")
    static_dirs = ['static/css', 'static/js', 'static/images']
    
    for static_dir in static_dirs:
        if os.path.exists(static_dir):
            print(f"  ✅ {static_dir}")
        else:
            print(f"  ⚠️ {static_dir} missing")
            os.makedirs(static_dir, exist_ok=True)
            print(f"  📁 Created {static_dir}")

def main():
    """Run all deployment checks"""
    print("🚀 CybrScan Deployment Readiness Check")
    print("=" * 50)
    
    checks = [
        ("Syntax Check", check_syntax_all),
        ("Requirements Check", check_requirements),
        ("Entry Point Check", check_entry_point),
        ("Templates Check", check_templates)
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        try:
            result = check_func()
            if not result:
                all_passed = False
        except Exception as e:
            print(f"❌ {check_name} failed: {e}")
            all_passed = False
    
    # Always run these
    check_database_files()
    check_static_files()
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 DEPLOYMENT READY!")
        print("✅ All critical checks passed")
        print("🚀 Ready for deployment to Render")
    else:
        print("❌ DEPLOYMENT ISSUES FOUND")
        print("🔧 Please fix the issues above before deploying")
    
    return all_passed

if __name__ == "__main__":
    main()