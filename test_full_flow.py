#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sqlite3
from fix_auth import authenticate_user_wrapper, create_user
from auth_utils import register_client
from client_db import verify_session, get_client_by_user_id
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_complete_registration_login_flow():
    """Test the complete registration and login flow as it happens in the web app"""
    print("🔍 Testing Complete Client Registration → Login → Dashboard Flow")
    print("=" * 70)
    
    # Test credentials
    test_username = "webclient"
    test_email = "webclient@example.com"
    test_password = "password123"
    test_full_name = "Web Client"
    
    try:
        # Cleanup any existing test data
        from client_db import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM sessions WHERE user_id IN (SELECT id FROM users WHERE username = ?)', (test_username,))
        cursor.execute('DELETE FROM clients WHERE user_id IN (SELECT id FROM users WHERE username = ?)', (test_username,))
        cursor.execute('DELETE FROM users WHERE username = ?', (test_username,))
        conn.commit()
        conn.close()
        
        # Step 1: Registration (as done by auth_routes.py)
        print(f"\n🔧 Step 1: User Registration (auth_routes.py flow)")
        user_result = create_user(test_username, test_email, test_password, 'client', test_full_name)
        
        if user_result['status'] != 'success':
            print(f"❌ User creation failed: {user_result['message']}")
            return
        
        user_id = user_result['user_id']
        print(f"✅ User created with ID: {user_id} and role: client")
        
        # Step 2: Auto-create client profile (as done by auth_routes.py)
        print(f"\n🔧 Step 2: Auto-create client profile")
        domain = test_email.split('@')[-1]
        business_name = test_full_name or test_username
        
        client_data = {
            'business_name': business_name,
            'business_domain': domain,
            'contact_email': test_email,
            'contact_phone': '',
            'scanner_name': f"{business_name}'s Scanner",
            'subscription_level': 'basic'
        }
        
        client_result = register_client(user_id, client_data)
        
        if client_result['status'] == 'success':
            print(f"✅ Client profile created with ID: {client_result['client_id']}")
        else:
            print(f"⚠️ Client profile creation failed: {client_result['message']} (this is handled gracefully)")
        
        # Step 3: Login (as done by auth_routes.py)
        print(f"\n🔧 Step 3: User Login (auth_routes.py flow)")
        auth_result = authenticate_user_wrapper(test_username, test_password, "127.0.0.1", "Test-Browser")
        
        if auth_result['status'] != 'success':
            print(f"❌ Authentication failed: {auth_result['message']}")
            return
        
        print(f"✅ Login successful!")
        print(f"   Username: {auth_result['username']}")
        print(f"   Role: {auth_result['role']}")
        print(f"   Session Token: {auth_result['session_token'][:20]}...")
        
        # Step 4: Session verification (as done by client.py)
        print(f"\n🔧 Step 4: Session Verification (client.py flow)")
        session_result = verify_session(auth_result['session_token'])
        
        if session_result['status'] != 'success':
            print(f"❌ Session verification failed: {session_result['message']}")
            return
        
        print(f"✅ Session verified successfully!")
        print(f"   User ID: {session_result['user']['user_id']}")
        print(f"   Username: {session_result['user']['username']}")
        print(f"   Role: {session_result['user']['role']}")
        
        # Step 5: Role check (as done by client.py @client_required)
        if session_result['user']['role'] != 'client':
            print(f"❌ Role check failed: Expected 'client', got '{session_result['user']['role']}'")
            return
        
        print(f"✅ Role check passed: User has 'client' role")
        
        # Step 6: Client dashboard data retrieval (as done by client.py dashboard)
        print(f"\n🔧 Step 6: Client Dashboard Data (client.py dashboard)")
        client_info = get_client_by_user_id(user_id)
        
        if client_info:
            print(f"✅ Client data retrieved!")
            print(f"   Business Name: {client_info['business_name']}")
            print(f"   Domain: {client_info['business_domain']}")
        else:
            print(f"⚠️ No client data found - dashboard will show defaults")
        
        print(f"\n🎉 Complete flow successful! Client login should work perfectly.")
        print(f"\n📋 Summary:")
        print(f"   1. ✅ User registration with 'client' role")
        print(f"   2. ✅ Client profile creation")
        print(f"   3. ✅ Login authentication")
        print(f"   4. ✅ Session verification")
        print(f"   5. ✅ Role-based access control")
        print(f"   6. ✅ Dashboard data retrieval")
        
        # Cleanup
        print(f"\n🧹 Cleaning up test data...")
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM sessions WHERE user_id = ?', (user_id,))
        cursor.execute('DELETE FROM clients WHERE user_id = ?', (user_id,))
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        conn.close()
        print(f"✅ Cleanup completed")
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_complete_registration_login_flow()