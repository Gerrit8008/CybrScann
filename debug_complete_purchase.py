#!/usr/bin/env python3
"""
Debug the complete purchase flow step by step
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def debug_complete_purchase():
    """Debug each step of the complete purchase flow"""
    print("🔧 Debugging Complete Purchase Flow")
    print("=" * 50)
    
    # Clean start - remove existing test data
    from client_db import get_db_connection
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Delete test users to start fresh
    cursor.execute("DELETE FROM users WHERE email LIKE 'debug_%'")
    cursor.execute("DELETE FROM clients WHERE contact_email LIKE 'debug_%'")
    cursor.execute("DELETE FROM scanners WHERE contact_email LIKE 'debug_%'")
    conn.commit()
    conn.close()
    print("🧹 Cleaned test data")
    
    # Simulate form data from Complete Purchase
    unique_id = os.urandom(4).hex()
    form_data = {
        'business_name': 'Debug Test Corp',
        'business_domain': 'debugtest.com',
        'contact_email': f'debug_{unique_id}@debugtest.com',
        'contact_phone': '555-DEBUG',
        'scanner_name': 'Debug Test Scanner',
        'primary_color': '#9b59b6',  # Purple
        'secondary_color': '#e67e22',  # Orange
        'email_subject': 'Debug Security Report',
        'email_intro': 'This is a debug test message',
        'subscription': 'pro',
        'default_scans': ['port_scan', 'ssl_check'],
        'logo_url': 'https://debugtest.com/logo.png',
        'description': 'Debug test scanner'
    }
    
    print(f"📝 Testing with email: {form_data['contact_email']}")
    
    try:
        # Step 1: Create user
        print("\n🔧 Step 1: Creating User...")
        from fix_auth import create_user
        
        username = f"debug_{unique_id}"
        user_result = create_user(username, form_data['contact_email'], "debug123", 'client', 'Debug User')
        
        if user_result['status'] != 'success':
            print(f"❌ User creation failed: {user_result['message']}")
            return
            
        user_id = user_result['user_id']
        print(f"✅ User created: ID {user_id}")
        
        # Step 2: Create client with customizations
        print("\n🔧 Step 2: Creating Client...")
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
        print(f"✅ Client created: ID {client_id}")
        
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
        
        print(f"Creating scanner for client_id: {client_id}")
        scanner_result = create_scanner_for_client(client_id, scanner_creation_data, 1)
        
        if scanner_result['status'] != 'success':
            print(f"❌ Scanner creation failed: {scanner_result['message']}")
            return
            
        scanner_uid = scanner_result['scanner_uid']
        print(f"✅ Scanner created: UID {scanner_uid}")
        
        # Step 4: Verify the relationships
        print("\n🔍 Step 4: Verifying Database Relationships...")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check the specific user/client/scanner chain
        cursor.execute('''
            SELECT 
                u.id as user_id, u.email,
                c.id as client_id, c.business_name,
                s.id as scanner_id, s.name as scanner_name,
                s.primary_color, s.secondary_color,
                cust.primary_color as cust_primary, cust.secondary_color as cust_secondary
            FROM users u
            LEFT JOIN clients c ON u.id = c.user_id
            LEFT JOIN scanners s ON c.id = s.client_id
            LEFT JOIN customizations cust ON c.id = cust.client_id
            WHERE u.id = ?
        ''', (user_id,))
        
        relationship = cursor.fetchone()
        
        if relationship:
            print(f"✅ Relationship verified:")
            print(f"   User {relationship[0]}: {relationship[1]}")
            print(f"   Client {relationship[2]}: {relationship[3]}")
            print(f"   Scanner {relationship[4]}: {relationship[5]}")
            print(f"   Scanner Colors: {relationship[6]}, {relationship[7]}")
            print(f"   Custom Colors: {relationship[8]}, {relationship[9]}")
            
            if relationship[4]:  # Scanner exists
                print("✅ Scanner properly linked to client")
                
                # Step 5: Test the scan page query
                print("\n🔍 Step 5: Testing Scan Page Query...")
                
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
                
                scanners = cursor.fetchall()
                
                if scanners:
                    scanner = scanners[0]
                    print(f"✅ Scan page would show:")
                    print(f"   Scanner Name: {scanner[1]}")
                    print(f"   Business Name: {scanner[6]}")
                    print(f"   Domain: {scanner[3]}")
                    print(f"   Primary Color: {scanner[4]}")
                    print(f"   Secondary Color: {scanner[5]}")
                    print(f"   Logo URL: {scanner[7]}")
                    
                    print("\n🎉 SUCCESS! Complete Purchase flow works correctly!")
                    print("✅ User created with customizations")
                    print("✅ Scanner properly linked")
                    print("✅ Scan page will show white label branding")
                    
                else:
                    print("❌ Scan page query returned no results")
            else:
                print("❌ Scanner not linked to client")
        else:
            print("❌ Could not verify relationships")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Debug error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_complete_purchase()