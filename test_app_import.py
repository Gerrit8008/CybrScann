#!/usr/bin/env python3
"""
Test script to verify the app can be imported and started
"""

import sys
import traceback

def test_app_import():
    """Test if we can import the app successfully"""
    print("🧪 Testing CybrScan App Import")
    print("=" * 50)
    
    try:
        print("📦 Attempting to import app...")
        from app import app
        print("✅ App imported successfully!")
        
        print(f"📊 App name: {app.name}")
        print(f"📊 Blueprints registered: {len(app.blueprints)}")
        print(f"📊 Blueprint names: {list(app.blueprints.keys())}")
        
        # Test if we can get the app context
        with app.app_context():
            print("✅ App context works!")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to import app: {e}")
        print("Full traceback:")
        traceback.print_exc()
        return False

def test_wsgi_import():
    """Test if we can import via wsgi"""
    print("\n🧪 Testing WSGI Import")
    print("=" * 50)
    
    try:
        print("📦 Attempting to import via wsgi...")
        from wsgi import application
        print("✅ WSGI import successful!")
        
        print(f"📊 Application name: {application.name}")
        print(f"📊 Blueprints: {list(application.blueprints.keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to import via wsgi: {e}")
        print("Full traceback:")
        traceback.print_exc()
        return False

if __name__ == '__main__':
    app_success = test_app_import()
    wsgi_success = test_wsgi_import()
    
    print("\n" + "=" * 50)
    print("📋 SUMMARY:")
    print(f"   Direct app import: {'✅ PASS' if app_success else '❌ FAIL'}")
    print(f"   WSGI import: {'✅ PASS' if wsgi_success else '❌ FAIL'}")
    
    if app_success and wsgi_success:
        print("\n🎉 All tests passed! App should work on Render.")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")