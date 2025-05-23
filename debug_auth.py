#!/usr/bin/env python3
"""
Debug script to test client registration and login flow
"""

import sys
import os
import sqlite3
from fix_auth import create_user, authenticate_user_wrapper
from auth_utils import register_client

def debug_auth_flow():
    """Test the complete registration and login flow"""
    print("🧪 Testing Client Registration and Login Flow")
    print("=" * 60)
    
    # Test credentials
    test_username = "testclient"
    test_email = "test@example.com"
    test_password = "password123"
    test_fullname = "Test Client"
    
    print("🔧 Step 1: Testing User Creation")
    try:
        result = create_user(test_username, test_email, test_password, 'client', test_fullname)
        print(f"   Result: {result}")
        
        if result['status'] != 'success':
            print("❌ User creation failed!")
            return False
        
        user_id = result['user_id']
        print(f"✅ User created successfully with ID: {user_id}")
        
    except Exception as e:
        print(f"❌ User creation error: {e}")
        return False
    
    print("\n🔧 Step 2: Testing Client Profile Creation")
    try:
        client_data = {
            'business_name': 'Test Business',
            'business_domain': 'test.com',
            'contact_email': test_email,
            'contact_phone': '123-456-7890',
            'scanner_name': 'Test Scanner',
            'subscription_level': 'basic'
        }
        
        client_result = register_client(user_id, client_data)
        print(f"   Result: {client_result}")
        
        if client_result['status'] != 'success':
            print("⚠️ Client profile creation failed, but user still exists")
        else:
            print("✅ Client profile created successfully")
            
    except Exception as e:
        print(f"⚠️ Client profile creation error: {e}")
        print("   Continuing with authentication test...")
    
    print("\n🔧 Step 3: Testing Authentication")
    try:
        auth_result = authenticate_user_wrapper(test_username, test_password)
        print(f"   Result: {auth_result}")
        
        if auth_result['status'] != 'success':
            print("❌ Authentication failed!")
            print(f"   Message: {auth_result.get('message', 'Unknown error')}")
            return False
        
        print("✅ Authentication successful!")
        print(f"   Username: {auth_result.get('username')}")
        print(f"   Role: {auth_result.get('role')}")
        print(f"   Session Token: {auth_result.get('session_token', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False
    
    print("\n🔧 Step 4: Testing Database State")
    try:
        from client_db import CLIENT_DB_PATH
        conn = sqlite3.connect(CLIENT_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check user exists
        cursor.execute('SELECT * FROM users WHERE username = ?', (test_username,))
        user = cursor.fetchone()
        
        if user:
            print(f"✅ User found in database:")
            print(f"   ID: {user['id']}")
            print(f"   Username: {user['username']}")
            print(f"   Email: {user['email']}")
            print(f"   Role: {user['role']}")
            print(f"   Active: {user['active']}")
        else:
            print("❌ User not found in database!")
            
        # Check client profile
        cursor.execute('SELECT * FROM clients WHERE user_id = ?', (user_id,))
        client = cursor.fetchone()
        
        if client:
            print(f"✅ Client profile found:")
            print(f"   Business Name: {client['business_name']}")
            print(f"   Domain: {client['business_domain']}")
        else:
            print("⚠️ Client profile not found (this may be okay)")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ Database check error: {e}")
        return False
    
    print("\n🧹 Cleanup: Removing test user")
    try:
        conn = sqlite3.connect(CLIENT_DB_PATH)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM clients WHERE user_id = ?', (user_id,))
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        conn.close()
        print("✅ Test user cleaned up")
    except Exception as e:
        print(f"⚠️ Cleanup error: {e}")
    
    print("\n🎉 Authentication flow test completed successfully!")
    return True

def check_database_tables():
    """Check if all required tables exist"""
    print("\n🔍 Checking Database Tables")
    print("=" * 40)
    
    try:
        from client_db import CLIENT_DB_PATH
        conn = sqlite3.connect(CLIENT_DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        required_tables = ['users', 'clients', 'sessions']
        
        for table in required_tables:
            if table in tables:
                print(f"✅ Table '{table}' exists")
                
                # Check table structure
                cursor.execute(f"PRAGMA table_info({table})")
                columns = cursor.fetchall()
                print(f"   Columns: {[col[1] for col in columns]}")
            else:
                print(f"❌ Table '{table}' missing!")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database check error: {e}")
        return False

if __name__ == '__main__':
    print("🔍 CybrScan Authentication Debug Tool")
    print("=" * 60)
    
    # Check database first
    if not check_database_tables():
        print("❌ Database issues found. Please check your database setup.")
        sys.exit(1)
    
    # Test authentication flow
    if debug_auth_flow():
        print("\n✅ All tests passed! Authentication should work correctly.")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        sys.exit(1)