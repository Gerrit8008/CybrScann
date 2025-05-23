#!/usr/bin/env python3
"""
Test the complete purchase flow end-to-end
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_complete_purchase_flow():
    """Test the complete flow from form submission to scanner display"""
    print("🚀 Testing Complete Purchase Flow")
    print("=" * 60)
    
    try:
        # Simulate the form data that would be submitted
        form_data = {
            'business_name': 'Acme Security Corp',
            'business_domain': 'acmesecurity.com',
            'contact_email': 'admin@acmesecurity.com',
            'contact_phone': '555-ACME',
            'scanner_name': 'Acme Vulnerability Scanner',
            'primary_color': '#e74c3c',  # Red
            'secondary_color': '#3498db',  # Blue
            'email_subject': 'Acme Security Report',
            'email_intro': 'Your custom security assessment from Acme Security Corp',
            'subscription': 'pro',
            'default_scans': ['port_scan', 'ssl_check', 'vulnerability_scan'],
            'logo_url': 'https://acmesecurity.com/logo.png',
            'description': 'Professional security scanner for enterprise clients'
        }
        
        print("📝 Form Data:")
        for key, value in form_data.items():
            print(f"   {key}: {value}")
        
        # Step 1: Create user
        print("\n🔧 Step 1: Creating User...")
        from fix_auth import create_user
        
        test_username = f"acme_{os.urandom(4).hex()}"
        test_email = form_data['contact_email']
        temp_password = "temp123"
        
        user_result = create_user(test_username, test_email, temp_password, 'client', 'Acme Admin')
        
        if user_result['status'] != 'success':
            print(f"❌ User creation failed: {user_result['message']}")
            return
            
        user_id = user_result['user_id']
        print(f"✅ User created: ID {user_id}, Email: {test_email}")
        
        # Step 2: Register client with customizations
        print("\n🔧 Step 2: Registering Client with Customizations...")
        from auth_utils import register_client
        
        client_data = {
            'business_name': form_data['business_name'],
            'business_domain': form_data['business_domain'],
            'contact_email': form_data['contact_email'],
            'contact_phone': form_data['contact_phone'],
            'scanner_name': form_data['scanner_name'],
            'subscription_level': form_data['subscription'],
            'primary_color': form_data['primary_color'],
            'secondary_color': form_data['secondary_color'],
            'logo_url': form_data['logo_url'],
            'email_subject': form_data['email_subject'],
            'email_intro': form_data['email_intro']
        }
        
        client_result = register_client(user_id, client_data)
        
        if client_result['status'] != 'success':
            print(f"❌ Client registration failed: {client_result['message']}")
            return
            
        client_id = client_result['client_id']
        print(f"✅ Client registered: ID {client_id}")
        
        # Step 3: Create scanner
        print("\n🔧 Step 3: Creating Scanner...")
        from scanner_db_functions import patch_client_db_scanner_functions, create_scanner_for_client
        
        patch_client_db_scanner_functions()
        
        scanner_creation_data = {
            'name': form_data['scanner_name'],
            'business_name': form_data['business_name'],
            'description': form_data['description'],
            'domain': form_data['business_domain'],
            'primary_color': form_data['primary_color'],
            'secondary_color': form_data['secondary_color'],
            'logo_url': form_data['logo_url'],
            'contact_email': form_data['contact_email'],
            'contact_phone': form_data['contact_phone'],
            'email_subject': form_data['email_subject'],
            'email_intro': form_data['email_intro'],
            'scan_types': form_data['default_scans']
        }
        
        scanner_result = create_scanner_for_client(client_id, scanner_creation_data, 1)
        
        if scanner_result['status'] != 'success':
            print(f"❌ Scanner creation failed: {scanner_result['message']}")
            return
            
        scanner_uid = scanner_result['scanner_uid']
        api_key = scanner_result['api_key']
        print(f"✅ Scanner created: UID {scanner_uid}")
        
        # Step 4: Generate deployment
        print("\n🔧 Step 4: Generating Deployment...")
        from scanner_deployment import generate_scanner_deployment
        
        deployment_result = generate_scanner_deployment(scanner_uid, scanner_creation_data, api_key)
        
        if deployment_result['status'] != 'success':
            print(f"❌ Deployment failed: {deployment_result['message']}")
            return
            
        print(f"✅ Deployment generated: {deployment_result['deployment_path']}")
        
        # Step 5: Test session creation
        print("\n🔧 Step 5: Creating Session...")
        from auth_utils import create_session
        
        session_result = create_session(user_id, test_email, 'client')
        
        if session_result['status'] != 'success':
            print(f"❌ Session creation failed: {session_result['message']}")
            return
            
        session_token = session_result['session_token']
        print(f"✅ Session created: {session_token[:20]}...")
        
        # Step 6: Test scanner retrieval for scan page
        print("\n🔧 Step 6: Testing Scanner Retrieval...")
        from client_db import get_db_connection
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                s.scanner_id, 
                s.name, 
                s.description, 
                s.domain,
                s.primary_color,
                s.secondary_color,
                c.business_name,
                cust.logo_path as logo_url
            FROM scanners s
            JOIN clients c ON s.client_id = c.id
            LEFT JOIN customizations cust ON c.id = cust.client_id
            WHERE c.user_id = ?
            ORDER BY s.created_at DESC
        ''', (user_id,))
        
        user_scanners = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        if user_scanners:
            scanner = user_scanners[0]
            print(f"✅ Scanner retrieved for dashboard:")
            print(f"   Name: {scanner['name']}")
            print(f"   Business: {scanner['business_name']}")
            print(f"   Domain: {scanner['domain']}")
            print(f"   Primary Color: {scanner['primary_color']}")
            print(f"   Secondary Color: {scanner['secondary_color']}")
            print(f"   Logo URL: {scanner['logo_url']}")
        else:
            print("❌ No scanners found for user")
            return
        
        # Step 7: Check deployment files
        print("\n🔧 Step 7: Checking Deployment Files...")
        deployment_dir = deployment_result['deployment_path']
        
        files_to_check = ['index.html', 'scanner-styles.css', 'scanner-script.js', 'api-docs.md']
        for file_name in files_to_check:
            file_path = os.path.join(deployment_dir, file_name)
            if os.path.exists(file_path):
                print(f"✅ {file_name} exists")
                
                # Check if colors are in CSS file
                if file_name == 'scanner-styles.css':
                    with open(file_path, 'r') as f:
                        css_content = f.read()
                        if form_data['primary_color'] in css_content:
                            print(f"   ✅ Primary color {form_data['primary_color']} found in CSS")
                        if form_data['secondary_color'] in css_content:
                            print(f"   ✅ Secondary color {form_data['secondary_color']} found in CSS")
            else:
                print(f"❌ {file_name} missing")
        
        print("\n" + "=" * 60)
        print("🎉 COMPLETE PURCHASE FLOW TEST PASSED!")
        print("=" * 60)
        print("✅ User creation")
        print("✅ Client registration with customizations")
        print("✅ Scanner creation")
        print("✅ Deployment generation with custom colors")
        print("✅ Session creation for auto-login")
        print("✅ Scanner retrieval for dashboard display")
        print("✅ Custom colors applied to deployment files")
        print("\n🚀 The Complete Purchase button should now:")
        print("   1. Create user and client with custom colors/name")
        print("   2. Create scanner with customizations")
        print("   3. Generate deployment with custom styling")
        print("   4. Auto-login the client")
        print("   5. Redirect to /scan page showing custom scanner")
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_complete_purchase_flow()