#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_app_startup():
    """Test application startup without the errors"""
    print("🔍 Testing Application Startup")
    print("=" * 50)
    
    try:
        # Import the app to test startup process
        print("📦 Importing application...")
        from app import app
        
        print("✅ Application imported successfully")
        
        # Test that the app was created
        if app:
            print("✅ Flask app instance created")
        else:
            print("❌ Flask app is None")
            return
            
        # Test blueprints are registered
        print(f"\n📋 Registered Blueprints:")
        print("-" * 30)
        
        for blueprint_name in app.blueprints:
            print(f"✅ {blueprint_name}")
        
        # Test for route conflicts
        print(f"\n🔍 Checking for Route Conflicts:")
        print("-" * 30)
        
        routes = {}
        conflicts = []
        
        for rule in app.url_map.iter_rules():
            route_key = f"{rule.rule} [{','.join(rule.methods)}]"
            if route_key in routes:
                conflicts.append(f"{route_key}: {routes[route_key]} vs {rule.endpoint}")
            else:
                routes[route_key] = rule.endpoint
        
        if conflicts:
            for conflict in conflicts:
                print(f"⚠️ {conflict}")
        else:
            print("✅ No route conflicts detected")
        
        # Test critical routes exist
        print(f"\n🎯 Testing Critical Routes:")
        print("-" * 30)
        
        critical_routes = [
            '/admin/dashboard',
            '/admin/clients',
            '/admin/subscriptions', 
            '/admin/reports',
            '/admin/settings',
            '/client/dashboard',
            '/auth/login',
            '/auth/logout',
            '/customize'
        ]
        
        route_rules = [rule.rule for rule in app.url_map.iter_rules()]
        
        for route in critical_routes:
            if route in route_rules:
                print(f"✅ {route}")
            else:
                print(f"❌ {route} (MISSING)")
        
        print(f"\n🎉 Application startup test completed!")
        print(f"Total blueprints: {len(app.blueprints)}")
        print(f"Total routes: {len(routes)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Application startup failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_app_startup()
    if success:
        print("\n🚀 Application is ready to run!")
    else:
        print("\n💥 Application has startup issues that need fixing")