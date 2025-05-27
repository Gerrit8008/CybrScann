#!/usr/bin/env python3
"""
Test auth flow to debug routing issues
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_auth_flow():
    """Test authentication flow"""
    try:
        print("🔍 Testing auth flow...")
        
        # Import the app
        from app import app
        
        print("✅ App imported successfully")
        
        # Create test client
        with app.test_client() as client:
            print("\n📋 Testing routes:")
            print("-" * 50)
            
            # Test GET /auth/login
            response = client.get('/auth/login')
            print(f"GET /auth/login: {response.status_code}")
            
            # Test GET /auth/register  
            response = client.get('/auth/register')
            print(f"GET /auth/register: {response.status_code}")
            
            # Test GET /admin (should redirect to login)
            response = client.get('/admin', follow_redirects=False)
            print(f"GET /admin: {response.status_code}")
            if response.status_code == 302:
                print(f"  Redirects to: {response.location}")
            
            # Test if admin_dashboard endpoint exists
            with app.app_context():
                try:
                    from flask import url_for
                    admin_url = url_for('admin.admin_dashboard')
                    print(f"admin.admin_dashboard URL: {admin_url}")
                except Exception as e:
                    print(f"❌ Error generating admin.admin_dashboard URL: {e}")
                
                try:
                    client_url = url_for('client.dashboard')
                    print(f"client.dashboard URL: {client_url}")
                except Exception as e:
                    print(f"❌ Error generating client.dashboard URL: {e}")
            
            print(f"\n🔍 Route analysis:")
            print(f"-" * 30)
            
            # Check all admin routes
            admin_routes = []
            auth_routes = []
            
            for rule in app.url_map.iter_rules():
                if 'admin' in rule.endpoint:
                    admin_routes.append(f"{rule.rule} -> {rule.endpoint}")
                if 'auth' in rule.endpoint:
                    auth_routes.append(f"{rule.rule} -> {rule.endpoint}")
            
            print(f"Admin routes found: {len(admin_routes)}")
            for route in admin_routes:
                print(f"  {route}")
                
            print(f"\nAuth routes found: {len(auth_routes)}")
            for route in auth_routes:
                print(f"  {route}")
                
    except Exception as e:
        print(f"❌ Error testing auth flow: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_auth_flow()