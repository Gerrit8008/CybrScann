#!/usr/bin/env python3
"""
Test script to verify all imports work correctly
"""

import sys
import traceback

def test_import(module_name, description):
    """Test importing a module"""
    try:
        __import__(module_name)
        print(f"✅ {description}: SUCCESS")
        return True
    except Exception as e:
        print(f"❌ {description}: FAILED - {e}")
        traceback.print_exc()
        return False

def main():
    print("🧪 Testing CybrScan Import Dependencies")
    print("=" * 50)
    
    success_count = 0
    total_tests = 0
    
    tests = [
        ("admin", "Admin Blueprint"),
        ("auth_routes", "Auth Routes Blueprint"),
        ("client", "Client Blueprint"),
        ("client_db", "Client Database"),
        ("config", "Configuration"),
        ("email_handler", "Email Handler"),
        ("database_manager", "Database Manager"),
        ("database_utils", "Database Utils")
    ]
    
    for module, description in tests:
        total_tests += 1
        if test_import(module, description):
            success_count += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Results: {success_count}/{total_tests} imports successful")
    
    if success_count == total_tests:
        print("🎉 All imports working! App should start correctly.")
        return True
    else:
        print("⚠️  Some imports failed. Check the errors above.")
        return False

if __name__ == '__main__':
    main()