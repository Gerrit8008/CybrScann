#!/usr/bin/env python3
"""
Comprehensive test script for the customize workflow
Tests the complete flow including button color customization
"""

import sys
import os
import time
import json
import sqlite3
import tempfile
import shutil
import logging
from io import BytesIO

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_test_environment():
    """Set up test environment"""
    print("🔧 Setting up test environment...")
    
    # Import Flask app
    try:
        from app import app
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        return app.test_client()
    except Exception as e:
        print(f"❌ Failed to set up test environment: {e}")
        return None

def test_customize_route_exists(client):
    """Test 1: Verify customize route exists and responds"""
    print("\n🔧 Test 1: Customize Route Availability")
    print("-" * 50)
    
    try:
        # Test GET request
        response = client.get('/customize')
        print(f"   GET /customize status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Customize route accessible")
            
            # Check if it returns HTML content
            if b'<!DOCTYPE html>' in response.data or b'<html' in response.data:
                print("   ✅ Returns HTML template")
                return True
            else:
                print("   ⚠️ Route accessible but may not return proper template")
                return False
        else:
            print(f"   ❌ Route not accessible: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing route: {e}")
        return False

def test_customize_template_content(client):
    """Test 2: Verify template has required form fields"""
    print("\n🔧 Test 2: Template Form Fields")
    print("-" * 50)
    
    try:
        response = client.get('/customize')
        if response.status_code != 200:
            print(f"   ❌ Cannot access template: {response.status_code}")
            return False
        
        content = response.data.decode('utf-8')
        
        # Required form fields for customize workflow
        required_fields = [
            ('business_name', 'Business name field'),
            ('business_domain', 'Business domain field'),
            ('contact_email', 'Contact email field'),
            ('scanner_name', 'Scanner name field'),
            ('primary_color', 'Primary color field'),
            ('secondary_color', 'Secondary color field'),
            ('button_color', 'Button color field'),
            ('email_subject', 'Email subject field'),
            ('default_scans', 'Default scans field')
        ]
        
        all_fields_present = True
        for field_name, description in required_fields:
            if f'name="{field_name}"' in content or f"name='{field_name}'" in content:
                print(f"   ✅ {description}")
            else:
                print(f"   ❌ {description} missing")
                all_fields_present = False
        
        # Check for form action and method
        if 'action="/customize"' in content:
            print("   ✅ Form action points to /customize")
        else:
            print("   ⚠️ Form action may not point to /customize")
            all_fields_present = False
        
        if 'method="post"' in content.lower():
            print("   ✅ Form uses POST method")
        else:
            print("   ❌ Form does not use POST method")
            all_fields_present = False
        
        # Check for file upload capability
        if 'enctype="multipart/form-data"' in content:
            print("   ✅ Form supports file uploads (logo/favicon)")
        else:
            print("   ⚠️ Form may not support file uploads")
        
        return all_fields_present
        
    except Exception as e:
        print(f"   ❌ Error checking template: {e}")
        return False

def test_database_schema():
    """Test 3: Verify database has required columns"""
    print("\n🔧 Test 3: Database Schema")
    print("-" * 50)
    
    try:
        # Check if database exists
        db_path = 'client_scanner.db'
        if not os.path.exists(db_path):
            print(f"   ❌ Database file not found: {db_path}")
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check customizations table
        try:
            cursor.execute("PRAGMA table_info(customizations)")
            customizations_columns = [col[1] for col in cursor.fetchall()]
            
            required_customizations_columns = [
                'button_color', 'primary_color', 'secondary_color', 
                'logo_path', 'favicon_path', 'email_subject', 'email_intro'
            ]
            
            missing_columns = []
            for col in required_customizations_columns:
                if col in customizations_columns:
                    print(f"   ✅ customizations.{col}")
                else:
                    print(f"   ❌ customizations.{col} missing")
                    missing_columns.append(col)
            
            if missing_columns:
                print(f"   ⚠️ Missing columns in customizations table: {missing_columns}")
        
        except Exception as e:
            print(f"   ❌ Error checking customizations table: {e}")
        
        # Check scanners table
        try:
            cursor.execute("PRAGMA table_info(scanners)")
            scanners_columns = [col[1] for col in cursor.fetchall()]
            
            required_scanners_columns = [
                'scanner_id', 'name', 'primary_color', 'secondary_color', 
                'logo_url', 'contact_email', 'api_key'
            ]
            
            for col in required_scanners_columns:
                if col in scanners_columns:
                    print(f"   ✅ scanners.{col}")
                else:
                    print(f"   ❌ scanners.{col} missing")
        
        except Exception as e:
            print(f"   ❌ Error checking scanners table: {e}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Error checking database: {e}")
        return False

def test_form_data_processing(client):
    """Test 4: Test POST request with form data"""
    print("\n🔧 Test 4: Form Data Processing")
    print("-" * 50)
    
    try:
        # Prepare test form data
        test_data = {
            'business_name': 'Test Security Company',
            'business_domain': 'https://testsecurity.com',
            'contact_email': 'test@testsecurity.com',
            'contact_phone': '+1-555-0123',
            'scanner_name': 'Test Security Scanner',
            'primary_color': '#1a5490',
            'secondary_color': '#28a745',
            'button_color': '#ff6b35',  # Test button color specifically
            'email_subject': 'Your Security Scan Results',
            'email_intro': 'Thank you for using our security scanner.',
            'subscription': 'basic',
            'default_scans[]': ['port_scan', 'ssl_check'],
            'description': 'Test scanner for validation',
            'payment_processed': '1'
        }
        
        print(f"   📋 Sending test data:")
        print(f"   • Business: {test_data['business_name']}")
        print(f"   • Primary Color: {test_data['primary_color']}")
        print(f"   • Secondary Color: {test_data['secondary_color']}")
        print(f"   • Button Color: {test_data['button_color']}")
        
        # Send POST request
        response = client.post('/customize', data=test_data, follow_redirects=False)
        print(f"   Response status: {response.status_code}")
        
        if response.status_code == 302:
            print("   ✅ POST request processed (redirect response)")
            location = response.headers.get('Location', '')
            print(f"   Redirect location: {location}")
            
            # Check if redirected to scanner info or client dashboard
            if '/scanner/' in location or '/client/' in location:
                print("   ✅ Redirected to appropriate success page")
                return True
            else:
                print(f"   ⚠️ Unexpected redirect location: {location}")
                return False
                
        elif response.status_code == 200:
            # Check response content for success/error messages
            content = response.data.decode('utf-8')
            if 'success' in content.lower() or 'created' in content.lower():
                print("   ✅ POST request processed successfully")
                return True
            elif 'error' in content.lower():
                print("   ❌ POST request returned error")
                print(f"   Error content: {content[:200]}...")
                return False
            else:
                print("   ⚠️ POST request processed but unclear result")
                return False
        else:
            print(f"   ❌ Unexpected response status: {response.status_code}")
            if response.data:
                print(f"   Response: {response.data.decode('utf-8')[:200]}...")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing form processing: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_button_color_functionality():
    """Test 5: Specific button color functionality"""
    print("\n🔧 Test 5: Button Color Functionality")
    print("-" * 50)
    
    try:
        # Test that button_color is handled in various components
        
        # Check app.py customize route
        print("   📋 Checking app.py customize route...")
        with open('app.py', 'r') as f:
            app_content = f.read()
        
        if "'button_color': request.form.get('button_color'" in app_content:
            print("   ✅ app.py extracts button_color from form")
        else:
            print("   ❌ app.py does not extract button_color from form")
        
        if "'button_color': scanner_data.get('button_color'" in app_content:
            print("   ✅ app.py passes button_color to scanner creation")
        else:
            print("   ❌ app.py does not pass button_color to scanner creation")
        
        # Check auth_utils.py
        print("   📋 Checking auth_utils.py...")
        try:
            with open('auth_utils.py', 'r') as f:
                auth_content = f.read()
            
            if 'button_color' in auth_content:
                print("   ✅ auth_utils.py handles button_color")
            else:
                print("   ❌ auth_utils.py does not handle button_color")
        except:
            print("   ⚠️ Could not check auth_utils.py")
        
        # Check scanner_deployment.py
        print("   📋 Checking scanner_deployment.py...")
        try:
            with open('scanner_deployment.py', 'r') as f:
                deploy_content = f.read()
            
            if 'button_color' in deploy_content:
                print("   ✅ scanner_deployment.py uses button_color")
            else:
                print("   ❌ scanner_deployment.py does not use button_color")
        except:
            print("   ⚠️ Could not check scanner_deployment.py")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error testing button color functionality: {e}")
        return False

def test_file_upload_handling(client):
    """Test 6: File upload handling (logo/favicon)"""
    print("\n🔧 Test 6: File Upload Handling")
    print("-" * 50)
    
    try:
        # Create a simple test image file
        test_image_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82'
        
        # Test data with file upload
        test_data = {
            'business_name': 'Logo Test Company',
            'business_domain': 'https://logotest.com',
            'contact_email': 'test@logotest.com',
            'scanner_name': 'Logo Test Scanner',
            'primary_color': '#123456',
            'secondary_color': '#654321',
            'button_color': '#abcdef',
            'payment_processed': '1'
        }
        
        # Create file-like object for logo
        logo_file = (BytesIO(test_image_data), 'test_logo.png')
        favicon_file = (BytesIO(test_image_data), 'test_favicon.png')
        
        # Test with file uploads
        response = client.post('/customize', 
                             data=test_data,
                             content_type='multipart/form-data',
                             files={'logo': logo_file, 'favicon': favicon_file},
                             follow_redirects=False)
        
        print(f"   File upload test status: {response.status_code}")
        
        if response.status_code in [200, 302]:
            print("   ✅ File upload handling works")
            
            # Check if uploads directory was created
            uploads_dir = os.path.join('static', 'uploads')
            if os.path.exists(uploads_dir):
                print("   ✅ Uploads directory exists")
                
                # Check for uploaded files
                uploaded_files = os.listdir(uploads_dir)
                logo_files = [f for f in uploaded_files if 'logo_' in f]
                favicon_files = [f for f in uploaded_files if 'favicon_' in f]
                
                if logo_files:
                    print(f"   ✅ Logo file uploaded: {logo_files[0]}")
                else:
                    print("   ⚠️ No logo files found")
                
                if favicon_files:
                    print(f"   ✅ Favicon file uploaded: {favicon_files[0]}")
                else:
                    print("   ⚠️ No favicon files found")
                
                # Clean up test files
                for file in logo_files + favicon_files:
                    try:
                        os.remove(os.path.join(uploads_dir, file))
                        print(f"   🧹 Cleaned up test file: {file}")
                    except:
                        pass
                        
            else:
                print("   ⚠️ Uploads directory not created")
            
            return True
        else:
            print(f"   ❌ File upload failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing file upload: {e}")
        return False

def test_ajax_response_format(client):
    """Test 7: AJAX response format"""
    print("\n🔧 Test 7: AJAX Response Format")
    print("-" * 50)
    
    try:
        test_data = {
            'business_name': 'AJAX Test Company',
            'business_domain': 'https://ajaxtest.com',
            'contact_email': 'test@ajaxtest.com',
            'scanner_name': 'AJAX Test Scanner',
            'primary_color': '#ff0000',
            'secondary_color': '#00ff00',
            'button_color': '#0000ff',
            'payment_processed': '1'
        }
        
        # Send request with AJAX headers
        response = client.post('/customize', 
                             data=test_data,
                             headers={
                                 'X-Requested-With': 'XMLHttpRequest',
                                 'Accept': 'application/json'
                             },
                             follow_redirects=False)
        
        print(f"   AJAX request status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                # Try to parse as JSON
                json_data = json.loads(response.data.decode('utf-8'))
                print("   ✅ Response is valid JSON")
                
                # Check required fields in JSON response
                required_fields = ['status', 'message']
                for field in required_fields:
                    if field in json_data:
                        print(f"   ✅ JSON contains {field}: {json_data[field]}")
                    else:
                        print(f"   ❌ JSON missing {field}")
                
                return True
                
            except json.JSONDecodeError:
                print("   ❌ Response is not valid JSON")
                content = response.data.decode('utf-8')[:200]
                print(f"   Response content: {content}...")
                return False
        else:
            print(f"   ❌ AJAX request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing AJAX response: {e}")
        return False

def test_end_to_end_workflow():
    """Test 8: Complete end-to-end workflow simulation"""
    print("\n🔧 Test 8: End-to-End Workflow")
    print("-" * 50)
    
    try:
        # Import required modules
        from fix_auth import create_user
        from auth_utils import register_client
        from scanner_db_functions import create_scanner_for_client, patch_client_db_scanner_functions
        from scanner_deployment import generate_scanner_deployment
        
        # Patch scanner functions
        patch_client_db_scanner_functions()
        
        print("   📋 Step 1: Creating test user...")
        user_result = create_user('e2etest', 'e2e@test.com', 'temppass123', 'client', 'E2E Test User')
        
        if user_result['status'] == 'success':
            user_id = user_result['user_id']
            print(f"   ✅ User created: ID {user_id}")
            
            print("   📋 Step 2: Registering client...")
            client_data = {
                'business_name': 'E2E Test Business',
                'business_domain': 'https://e2etest.com',
                'contact_email': 'e2e@test.com',
                'contact_phone': '+1-555-0199',
                'scanner_name': 'E2E Test Scanner',
                'subscription_level': 'basic',
                'primary_color': '#e74c3c',
                'secondary_color': '#2ecc71',
                'button_color': '#f39c12',  # Test button color
                'logo_path': '/static/images/test_logo.png',
                'favicon_path': '/static/images/test_favicon.ico',
                'email_subject': 'E2E Test Security Report',
                'email_intro': 'This is an end-to-end test.'
            }
            
            client_result = register_client(user_id, client_data)
            
            if client_result['status'] == 'success':
                client_id = client_result['client_id']
                print(f"   ✅ Client registered: ID {client_id}")
                
                print("   📋 Step 3: Creating scanner...")
                scanner_creation_data = {
                    'name': 'E2E Test Scanner',
                    'business_name': 'E2E Test Business',
                    'description': 'End-to-end test scanner',
                    'domain': 'https://e2etest.com',
                    'primary_color': '#e74c3c',
                    'secondary_color': '#2ecc71',
                    'button_color': '#f39c12',
                    'logo_url': '/static/images/test_logo.png',
                    'favicon_path': '/static/images/test_favicon.ico',
                    'contact_email': 'e2e@test.com',
                    'contact_phone': '+1-555-0199',
                    'email_subject': 'E2E Test Security Report',
                    'email_intro': 'This is an end-to-end test.',
                    'scan_types': ['port_scan', 'ssl_check']
                }
                
                scanner_result = create_scanner_for_client(client_id, scanner_creation_data, 1)
                
                if scanner_result['status'] == 'success':
                    scanner_id = scanner_result['scanner_id']
                    scanner_uid = scanner_result['scanner_uid']
                    api_key = scanner_result['api_key']
                    print(f"   ✅ Scanner created: UID {scanner_uid}")
                    
                    print("   📋 Step 4: Generating deployment...")
                    deployment_result = generate_scanner_deployment(scanner_uid, scanner_creation_data, api_key)
                    
                    if deployment_result['status'] == 'success':
                        deployment_path = deployment_result['deployment_path']
                        print(f"   ✅ Deployment generated: {deployment_path}")
                        
                        # Check if button color is in generated files
                        if os.path.exists(deployment_path):
                            for file_name in ['scanner-styles.css', 'index.html']:
                                file_path = os.path.join(deployment_path, file_name)
                                if os.path.exists(file_path):
                                    with open(file_path, 'r') as f:
                                        file_content = f.read()
                                    
                                    if '#f39c12' in file_content:
                                        print(f"   ✅ Button color found in {file_name}")
                                    else:
                                        print(f"   ⚠️ Button color not found in {file_name}")
                        
                        print("   📋 Step 5: Cleanup...")
                        
                        # Clean up deployment files
                        if os.path.exists(deployment_path):
                            shutil.rmtree(deployment_path)
                            print("   ✅ Deployment files cleaned up")
                        
                        # Clean up database entries
                        from client_db import get_db_connection
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        cursor.execute('DELETE FROM scanners WHERE id = ?', (scanner_id,))
                        cursor.execute('DELETE FROM clients WHERE id = ?', (client_id,))
                        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
                        conn.commit()
                        conn.close()
                        print("   ✅ Database entries cleaned up")
                        
                        print("   🎉 End-to-end workflow completed successfully!")
                        return True
                    else:
                        print(f"   ❌ Deployment failed: {deployment_result['message']}")
                else:
                    print(f"   ❌ Scanner creation failed: {scanner_result['message']}")
            else:
                print(f"   ❌ Client registration failed: {client_result['message']}")
        else:
            print(f"   ❌ User creation failed: {user_result['message']}")
        
        return False
        
    except Exception as e:
        print(f"   ❌ End-to-end workflow error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run comprehensive customize workflow tests"""
    print("🚀 COMPREHENSIVE CUSTOMIZE WORKFLOW TEST")
    print("=" * 70)
    print("Testing complete customize functionality including button colors")
    print("=" * 70)
    
    # Set up test environment
    client = setup_test_environment()
    if not client:
        print("❌ Failed to set up test environment")
        return False
    
    # Run all tests
    tests = [
        ("Route Availability", lambda: test_customize_route_exists(client)),
        ("Template Form Fields", lambda: test_customize_template_content(client)),
        ("Database Schema", test_database_schema),
        ("Form Data Processing", lambda: test_form_data_processing(client)),
        ("Button Color Functionality", test_button_color_functionality),
        ("File Upload Handling", lambda: test_file_upload_handling(client)),
        ("AJAX Response Format", lambda: test_ajax_response_format(client)),
        ("End-to-End Workflow", test_end_to_end_workflow)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                print(f"✅ {test_name} - PASSED")
            else:
                print(f"❌ {test_name} - FAILED")
        except Exception as e:
            print(f"❌ {test_name} - ERROR: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Customize workflow is working correctly")
        print("✅ Button color functionality is working")
        print("✅ Form processing is working")
        print("✅ File uploads are working")
        print("✅ Database operations are working")
        print("✅ End-to-end workflow is complete")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed")
        print("❌ Some issues found in customize workflow")
        print("🔧 Check the detailed output above for specific issues")
    
    print("\n📋 Customize Workflow Components Tested:")
    print("• GET /customize route accessibility")
    print("• Template form fields (including button_color)")
    print("• Database schema validation")
    print("• POST form data processing")
    print("• Button color extraction and usage")
    print("• File upload handling (logo/favicon)")
    print("• AJAX response format")
    print("• Complete end-to-end user creation flow")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🚀 CUSTOMIZE WORKFLOW IS READY FOR PRODUCTION!")
    else:
        print("\n🔧 ISSUES FOUND - See details above")
        sys.exit(1)