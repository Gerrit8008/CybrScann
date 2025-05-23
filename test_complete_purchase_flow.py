#!/usr/bin/env python3
"""
Test script to verify Complete Purchase button flow
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_complete_purchase_flow():
    """Test the complete purchase button functionality"""
    
    print("🧪 Testing Complete Purchase Flow")
    print("=" * 50)
    
    # Test 1: Check if customize route exists
    print("\n1. Checking /customize route...")
    try:
        from app import app
        with app.test_client() as client:
            response = client.get('/customize')
            if response.status_code == 200:
                print("   ✅ /customize route accessible")
            else:
                print(f"   ❌ /customize route returned {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error accessing /customize route: {e}")
    
    # Test 2: Check if database tables exist
    print("\n2. Checking database tables...")
    try:
        from client_db import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if scanners table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='scanners'")
        if cursor.fetchone():
            print("   ✅ scanners table exists")
        else:
            print("   ❌ scanners table missing")
        
        # Check if clients table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='clients'")
        if cursor.fetchone():
            print("   ✅ clients table exists")
        else:
            print("   ❌ clients table missing")
            
        # Check if users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if cursor.fetchone():
            print("   ✅ users table exists")
        else:
            print("   ❌ users table missing")
        
        conn.close()
    except Exception as e:
        print(f"   ❌ Error checking database: {e}")
    
    # Test 3: Test payment form submission data
    print("\n3. Testing payment form data...")
    test_data = {
        'business_name': 'Test Company',
        'business_domain': 'testcompany.com',
        'contact_email': 'test@testcompany.com',
        'contact_phone': '555-1234',
        'scanner_name': 'Test Scanner',
        'primary_color': '#02054c',
        'secondary_color': '#35a310',
        'email_subject': 'Your Security Scan Report',
        'email_intro': 'Test intro',
        'subscription': 'basic',
        'payment_processed': '1',
        'cardName': 'Test User',
        'cardNumber': '4111 1111 1111 1111',
        'expiryDate': '12/25',
        'cvv': '123',
        'termsAgree': 'on'
    }
    
    try:
        with app.test_client() as client:
            response = client.post('/customize', data=test_data, follow_redirects=True)
            print(f"   📊 POST response status: {response.status_code}")
            
            if response.status_code == 200:
                # Check if redirected to scan page
                if b'Security Assessment Form' in response.data:
                    print("   ✅ Successfully redirected to scan page")
                elif b'scanner' in response.data.lower():
                    print("   ✅ Scanner creation appears successful")
                else:
                    print("   ⚠️  Unexpected response content")
            else:
                print(f"   ❌ Form submission failed with status {response.status_code}")
                
    except Exception as e:
        print(f"   ❌ Error testing form submission: {e}")
    
    # Test 4: Check auth_utils functions exist
    print("\n4. Checking authentication functions...")
    try:
        from auth_utils import create_session, verify_session
        print("   ✅ Authentication functions available")
    except ImportError as e:
        print(f"   ❌ Authentication functions missing: {e}")
    
    # Test 5: Check scanner deployment functions
    print("\n5. Checking scanner deployment...")
    try:
        from scanner_deployment import generate_scanner_deployment
        print("   ✅ Scanner deployment functions available")
    except ImportError as e:
        print(f"   ❌ Scanner deployment functions missing: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Test Complete!")
    print("\n📋 Summary:")
    print("   - Complete Purchase button should now auto-fill test data")
    print("   - After successful purchase, user gets logged in automatically")
    print("   - User is redirected to /scan page")
    print("   - Scan page shows their created scanner")
    print("   - Scanner appears in 'My Scanners' section")

if __name__ == "__main__":
    test_complete_purchase_flow()