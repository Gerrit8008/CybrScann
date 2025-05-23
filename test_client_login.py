#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sqlite3
from fix_auth import authenticate_user_wrapper, create_user
from auth_utils import register_client
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_client_login_issue():
    """Test the exact client login flow to identify the issue"""
    print("🔍 Testing Client Login Issue")
    print("=" * 50)
    
    # Test credentials
    test_username = "debugclient"
    test_email = "debug@example.com"
    test_password = "password123"
    
    try:
        # Step 1: Create a test user
        print(f"\n🔧 Step 1: Creating user '{test_username}'...")
        user_result = create_user(test_username, test_email, test_password, "Debug Client")
        
        if user_result['status'] != 'success':
            print(f"❌ User creation failed: {user_result['message']}")
            return
        
        user_id = user_result['user_id']
        print(f"✅ User created with ID: {user_id}")
        
        # Step 2: Create client profile
        print(f"\n🔧 Step 2: Creating client profile...")
        client_data = {
            'business_name': 'Debug Business',
            'business_domain': 'debug.com',
            'contact_email': test_email,
            'contact_phone': '+1234567890',
            'scanner_name': "Debug Scanner",
            'subscription_level': 'basic'
        }
        
        client_result = register_client(user_id, client_data)
        
        if client_result['status'] != 'success':
            print(f"❌ Client creation failed: {client_result['message']}")
            return
        
        print(f"✅ Client created with ID: {client_result['client_id']}")
        
        # Step 3: Test authentication
        print(f"\n🔧 Step 3: Testing authentication...")
        auth_result = authenticate_user_wrapper(test_username, test_password, "127.0.0.1", "Test-Agent")
        
        if auth_result['status'] != 'success':
            print(f"❌ Authentication failed: {auth_result['message']}")
            return
        
        print(f"✅ Authentication successful!")
        print(f"   Username: {auth_result['username']}")
        print(f"   Role: {auth_result['role']}")
        print(f"   Session Token: {auth_result['session_token']}")
        
        # Step 4: Test session verification (this is what client.py uses)
        print(f"\n🔧 Step 4: Testing session verification...")
        from client_db import verify_session
        
        session_result = verify_session(auth_result['session_token'])
        
        if session_result['status'] != 'success':
            print(f"❌ Session verification failed: {session_result['message']}")
            return
        
        print(f"✅ Session verification successful!")
        print(f"   User ID: {session_result['user']['user_id']}")
        print(f"   Username: {session_result['user']['username']}")
        print(f"   Role: {session_result['user']['role']}")
        
        # Step 5: Test client data retrieval
        print(f"\n🔧 Step 5: Testing client data retrieval...")
        from client_db import get_client_by_user_id
        
        client_info = get_client_by_user_id(user_id)
        
        if client_info:
            print(f"✅ Client data retrieved!")
            print(f"   Business Name: {client_info['business_name']}")
            print(f"   Domain: {client_info['business_domain']}")
        else:
            print(f"⚠️ No client data found (this is handled gracefully)")
        
        print(f"\n🎉 All tests passed! Login should work correctly.")
        
        # Cleanup
        print(f"\n🧹 Cleaning up test data...")
        from client_db import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE username = ?', (test_username,))
        cursor.execute('DELETE FROM clients WHERE contact_email = ?', (test_email,))
        conn.commit()
        conn.close()
        print(f"✅ Cleanup completed")
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_client_login_issue()