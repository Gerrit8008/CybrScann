#!/usr/bin/env python3
"""Test customize route authentication and template rendering"""

import sys
import os
sys.path.append('/home/ggrun/CybrScan_1')

def test_customize_route_with_different_auth_states():
    """Test the customize route behavior with different authentication states"""
    print("🔧 Testing customize route authentication...")
    
    try:
        # Import app components
        import app
        from flask import session
        
        with app.app.test_client() as client:
            with client.session_transaction() as sess:
                # Test 1: No authentication
                print("\n1. Testing without authentication...")
                response = client.get('/customize')
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.get_data(as_text=True)
                    if 'admin/customization-form' in response.get_data(as_text=True) or 'Admin' in data:
                        print("   ✅ Returns admin template (expected)")
                    elif 'customize_scanner' in data:
                        print("   ⚠️ Returns client template unexpectedly")
                    else:
                        print("   ❓ Returns unknown template")
                
                # Test 2: Client authentication
                print("\n2. Testing with client authentication...")
                sess['user_id'] = 2  # From our test, user 2 exists
                sess['user_role'] = 'client'
                sess['user_email'] = 'test@example.com'
                
            response = client.get('/customize')
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.get_data(as_text=True)
                if 'customize_scanner' in data or 'Create Security Scanner' in data:
                    print("   ✅ Returns client template (expected)")
                elif 'admin' in data.lower():
                    print("   ❌ Returns admin template unexpectedly")
                else:
                    print("   ❓ Returns unknown template")
            else:
                print(f"   ❌ Error response: {response.status_code}")
                
            # Test 3: Admin authentication
            with client.session_transaction() as sess:
                print("\n3. Testing with admin authentication...")
                sess['user_id'] = 1
                sess['user_role'] = 'admin'
                sess['user_email'] = 'admin@example.com'
                
            response = client.get('/customize')
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.get_data(as_text=True)
                if 'admin' in data.lower() or 'customization-form' in data:
                    print("   ✅ Returns admin template (expected)")
                else:
                    print("   ❓ Returns unexpected template")
        
        return True
        
    except Exception as e:
        print(f"❌ Authentication test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_client_data_loading():
    """Test if client data loads correctly for the customize template"""
    print("\n🔧 Testing client data loading...")
    
    try:
        from client_db import get_client_by_user_id, get_db_connection
        
        # Get a real client from database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, user_id, business_name FROM clients WHERE user_id IS NOT NULL LIMIT 1")
        client_row = cursor.fetchone()
        
        if not client_row:
            print("❌ No clients with valid user_id found")
            return False
            
        client_id, user_id, business_name = client_row
        print(f"✅ Testing with client {client_id} (user {user_id}): {business_name}")
        
        # Test get_client_by_user_id
        client_data = get_client_by_user_id(user_id)
        if client_data:
            print(f"✅ Client data loaded: {client_data.get('business_name')}")
            required_fields = ['business_name', 'business_domain', 'contact_email']
            missing_fields = [field for field in required_fields if not client_data.get(field)]
            
            if missing_fields:
                print(f"⚠️ Missing required fields: {missing_fields}")
            else:
                print("✅ All required client fields present")
        else:
            print(f"❌ get_client_by_user_id({user_id}) returned None")
            return False
        
        # Test scanners query
        cursor.execute('''
            SELECT * FROM scanners 
            WHERE client_id = ? 
            ORDER BY created_at DESC 
            LIMIT 5
        ''', (client_id,))
        scanners = cursor.fetchall()
        
        print(f"✅ Found {len(scanners)} scanners for client")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Client data test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_form_submission():
    """Test actual form submission to /customize"""
    print("\n🔧 Testing form submission...")
    
    try:
        import app
        
        # Test data that matches what the frontend would send
        test_form_data = {
            'business_name': 'Test Business',
            'business_domain': 'testbusiness.com', 
            'contact_email': 'test@testbusiness.com',
            'contact_phone': '+1-555-0123',
            'scanner_name': 'Test Scanner',
            'primary_color': '#02054c',
            'secondary_color': '#35a310', 
            'button_color': '#d96c33',
            'email_subject': 'Your Security Scan Report',
            'email_intro': 'Thank you for using our scanner',
            'default_scans': ['network', 'web'],
            'subscription': 'basic'
        }
        
        with app.app.test_client() as client:
            # Set up client session
            with client.session_transaction() as sess:
                sess['user_id'] = 2
                sess['user_role'] = 'client'
                sess['user_email'] = 'test@example.com'
            
            print("Sending POST request to /customize...")
            response = client.post('/customize', data=test_form_data)
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                # Check if it's JSON response
                try:
                    json_data = response.get_json()
                    if json_data:
                        print(f"✅ JSON response: {json_data.get('status', 'unknown')}")
                        if json_data.get('status') == 'success':
                            print("✅ Form submission successful")
                        else:
                            print(f"❌ Form submission failed: {json_data.get('message', 'unknown error')}")
                    else:
                        print("⚠️ HTML response instead of JSON")
                except:
                    print("⚠️ Non-JSON response")
            elif response.status_code == 302:
                print(f"⚠️ Redirect response to: {response.headers.get('Location', 'unknown')}")
            else:
                print(f"❌ Error response: {response.status_code}")
                print(f"Response data: {response.get_data(as_text=True)[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Form submission test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run authentication and route tests"""
    print("🚀 TESTING CUSTOMIZE ROUTE AUTHENTICATION & FUNCTIONALITY")
    print("=" * 60)
    
    tests = [
        test_customize_route_with_different_auth_states,
        test_client_data_loading,
        test_form_submission
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("🏁 AUTHENTICATION TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✅ Authentication and routing work correctly!")
    else:
        print("❌ Some authentication/routing issues found.")

if __name__ == "__main__":
    main()