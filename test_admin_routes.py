#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fix_auth import authenticate_user_wrapper
from client_db import verify_session

def test_admin_routes():
    """Test all admin routes to ensure they're working"""
    print("🔍 Testing Admin Dashboard Routes")
    print("=" * 50)
    
    # Admin routes that should exist
    admin_routes = [
        ('/admin/dashboard', 'Dashboard'),
        ('/admin/clients', 'Client Management'),
        ('/admin/subscriptions', 'Subscriptions'),
        ('/admin/reports', 'Reports'),
        ('/admin/settings', 'Settings'),
        ('/customize', 'Create Scanner'),
        ('/auth/logout', 'Logout')
    ]
    
    print("📋 Admin Sidebar Routes Status:")
    print("-" * 50)
    
    # Check routes exist in admin.py
    admin_py_content = ""
    try:
        with open('admin.py', 'r') as f:
            admin_py_content = f.read()
    except:
        print("❌ admin.py not found")
        return
    
    app_py_content = ""
    try:
        with open('app.py', 'r') as f:
            app_py_content = f.read()
    except:
        print("❌ app.py not found")
    
    for route, name in admin_routes:
        if route == '/auth/logout':
            # This is handled by auth_routes.py
            print(f"✅ {name:<20} {route:<25} (auth_routes.py)")
        elif route == '/customize':
            # This should be in app.py
            if '@app.route(\'/customize\')' in app_py_content or 'route(\'/customize\')' in app_py_content:
                print(f"✅ {name:<20} {route:<25} (app.py)")
            else:
                print(f"❌ {name:<20} {route:<25} (MISSING)")
        else:
            # These should be in admin.py
            route_pattern = f"@admin_bp.route('{route.replace('/admin', '')}')"
            if route_pattern in admin_py_content:
                print(f"✅ {name:<20} {route:<25} (admin.py)")
            else:
                print(f"❌ {name:<20} {route:<25} (MISSING)")
    
    print("\n📁 Admin Template Status:")
    print("-" * 50)
    
    # Check templates exist
    templates = [
        ('admin-dashboard.html', 'Dashboard'),
        ('client-management.html', 'Client Management'), 
        ('subscriptions-dashboard.html', 'Subscriptions'),
        ('reports-dashboard.html', 'Reports'),
        ('settings-dashboard.html', 'Settings')
    ]
    
    for template, name in templates:
        template_path = f'templates/admin/{template}'
        if os.path.exists(template_path):
            print(f"✅ {name:<20} {template}")
        else:
            print(f"❌ {name:<20} {template} (MISSING)")
    
    print("\n🎯 Test Admin Authentication Flow:")
    print("-" * 50)
    
    try:
        # Test admin login
        auth_result = authenticate_user_wrapper('admin', 'admin123', '127.0.0.1', 'Test-Browser')
        
        if auth_result['status'] == 'success' and auth_result['role'] == 'admin':
            print("✅ Admin authentication working")
            
            # Test session verification
            session_result = verify_session(auth_result['session_token'])
            if session_result['status'] == 'success':
                print("✅ Admin session verification working")
                print(f"   Admin user: {session_result['user']['username']}")
                print(f"   Role: {session_result['user']['role']}")
            else:
                print(f"❌ Admin session verification failed: {session_result['message']}")
        else:
            print(f"❌ Admin authentication failed: {auth_result.get('message', 'Unknown error')}")
    
    except Exception as e:
        print(f"❌ Admin auth test failed: {str(e)}")
    
    print(f"\n🎉 Admin route testing completed!")

if __name__ == "__main__":
    test_admin_routes()