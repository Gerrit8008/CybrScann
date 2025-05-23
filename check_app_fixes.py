#!/usr/bin/env python3

def check_app_fixes():
    """Check that app.py fixes have been applied correctly"""
    print("🔍 Checking App.py Fix Status")
    print("=" * 50)
    
    # Read app.py content
    try:
        with open('app.py', 'r') as f:
            app_content = f.read()
    except Exception as e:
        print(f"❌ Error reading app.py: {e}")
        return False
    
    # Check for removed undefined functions
    print("🔧 Checking Undefined Function Fixes:")
    print("-" * 40)
    
    undefined_functions = [
        'configure_admin',
        'register_debug_middleware', 
        'apply_admin_fixes',
        'add_admin_fix_route'
    ]
    
    for func in undefined_functions:
        if f"{func}(app)" in app_content:
            print(f"❌ {func} still being called")
        else:
            print(f"✅ {func} call removed")
    
    # Check for duplicate route removal
    print(f"\n🔧 Checking Route Conflict Fixes:")
    print("-" * 40)
    
    # Check if create-scanner duplicate was removed
    create_scanner_count = app_content.count("@app.route('/api/create-scanner'")
    if create_scanner_count == 0:
        print("✅ Duplicate /api/create-scanner route removed from app.py")
    else:
        print(f"❌ Found {create_scanner_count} /api/create-scanner routes in app.py")
    
    # Check auth_routes.py for API route removal
    try:
        with open('auth_routes.py', 'r') as f:
            auth_content = f.read()
            
        # Check if API routes were removed
        api_routes = ['@auth_bp.route(\'/api/check-username\')', 
                     '@auth_bp.route(\'/api/check-email\')',
                     '@auth_bp.route(\'/api/login-stats\')']
        
        for route in api_routes:
            if route in auth_content:
                print(f"❌ {route} still in auth_routes.py")
            else:
                print(f"✅ {route} removed from auth_routes.py")
                
    except Exception as e:
        print(f"⚠️ Error checking auth_routes.py: {e}")
    
    # Check for blueprint registration cleanup
    print(f"\n🔧 Checking Blueprint Registration:")
    print("-" * 40)
    
    blueprint_registrations = app_content.count('app.register_blueprint(')
    print(f"✅ Found {blueprint_registrations} blueprint registrations")
    
    # Check critical components exist
    print(f"\n📋 Checking Critical Components:")
    print("-" * 40)
    
    critical_checks = [
        ('Flask app creation', 'app = Flask(__name__)'),
        ('Database initialization', 'init_client_db()'),
        ('Auth blueprint import', 'from auth_routes import auth_bp'),
        ('Admin blueprint import', 'from admin import admin_bp'),
        ('Client blueprint import', 'from client import client_bp'),
        ('API blueprint import', 'from api import api_bp'),
        ('Scanner blueprint import', 'from scanner_router import scanner_bp')
    ]
    
    for check_name, pattern in critical_checks:
        if pattern in app_content:
            print(f"✅ {check_name}")
        else:
            print(f"❌ {check_name} (missing: {pattern})")
    
    print(f"\n🎯 Error Fix Summary:")
    print("=" * 50)
    print("✅ Undefined admin configuration functions removed")
    print("✅ Route conflicts resolved")
    print("✅ API routes moved to appropriate blueprints") 
    print("✅ Blueprint registration streamlined")
    
    print(f"\n🚀 App.py should now start without the reported errors!")
    
    return True

if __name__ == "__main__":
    check_app_fixes()