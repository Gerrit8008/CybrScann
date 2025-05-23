#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_login_redirect():
    """Test the login flow with the actual Flask app"""
    with app.test_client() as client:
        with app.test_request_context():
            print("🧪 Testing Login Flow with Flask Test Client")
            print("=" * 60)
            
            # Step 1: Test registration
            print("\n🔧 Step 1: Testing registration...")
            registration_data = {
                'username': 'testuser123',
                'email': 'testuser123@example.com',
                'password': 'password123',
                'confirm_password': 'password123',
                'full_name': 'Test User'
            }
            
            response = client.post('/auth/register', data=registration_data, follow_redirects=False)
            print(f"Registration response status: {response.status_code}")
            print(f"Registration response location: {response.location}")
            
            # Step 2: Test login
            print("\n🔧 Step 2: Testing login...")
            login_data = {
                'username': 'testuser123',
                'password': 'password123'
            }
            
            response = client.post('/auth/login', data=login_data, follow_redirects=False)
            print(f"Login response status: {response.status_code}")
            print(f"Login response location: {response.location}")
            print(f"Login response headers: {dict(response.headers)}")
            
            # Check if session is set
            with client.session_transaction() as sess:
                print(f"Session after login: {dict(sess)}")
            
            # Step 3: Test accessing client dashboard
            print("\n🔧 Step 3: Testing client dashboard access...")
            response = client.get('/client/dashboard', follow_redirects=False)
            print(f"Dashboard response status: {response.status_code}")
            print(f"Dashboard response location: {response.location}")
            
            if response.status_code == 200:
                print("✅ Dashboard accessible!")
            elif response.status_code == 302:
                print(f"🔄 Dashboard redirected to: {response.location}")
            else:
                print(f"❌ Dashboard access failed with status: {response.status_code}")
                print(f"Response data: {response.get_data(as_text=True)[:500]}")

if __name__ == "__main__":
    test_login_redirect()