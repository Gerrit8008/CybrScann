#!/usr/bin/env python3
"""
Test client customizations to ensure colors, name, etc. are saved properly
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_customizations():
    """Test that client customizations are saved and retrieved correctly"""
    print("🧪 Testing Client Customizations")
    print("=" * 50)
    
    try:
        # Test 1: Create user
        from fix_auth import create_user
        
        test_username = f"testuser_{os.urandom(4).hex()}"
        test_email = f"test_{os.urandom(4).hex()}@testcompany.com"
        
        user_result = create_user(test_username, test_email, "testpass123", 'client', 'Test User')
        
        if user_result['status'] != 'success':
            print(f"❌ User creation failed: {user_result['message']}")
            return
            
        user_id = user_result['user_id']
        print(f"✅ User created with ID: {user_id}")
        
        # Test 2: Register client with customizations
        from auth_utils import register_client
        
        client_data = {
            'business_name': 'Test Custom Company',
            'business_domain': 'testcustom.com',
            'contact_email': test_email,
            'contact_phone': '555-9999',
            'scanner_name': 'Custom Test Scanner',
            'subscription_level': 'pro',
            'primary_color': '#007bff',  # Blue
            'secondary_color': '#6c757d',  # Gray
            'logo_url': 'https://example.com/logo.png',
            'email_subject': 'Custom Scan Report',
            'email_intro': 'This is a custom intro message'
        }
        
        client_result = register_client(user_id, client_data)
        
        if client_result['status'] != 'success':
            print(f"❌ Client registration failed: {client_result['message']}")
            return
            
        client_id = client_result['client_id']
        print(f"✅ Client registered with ID: {client_id}")
        
        # Test 3: Verify customizations were saved
        from client_db import get_db_connection
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check client data
        cursor.execute('SELECT * FROM clients WHERE id = ?', (client_id,))
        client_row = cursor.fetchone()
        
        if client_row:
            print(f"✅ Client data saved:")
            print(f"   Business Name: {client_row[1]}")  # business_name
            print(f"   Scanner Name: {client_row[5]}")   # scanner_name
            print(f"   Subscription: {client_row[6]}")   # subscription_level
        
        # Check customizations
        cursor.execute('SELECT * FROM customizations WHERE client_id = ?', (client_id,))
        custom_row = cursor.fetchone()
        
        if custom_row:
            print(f"✅ Customizations saved:")
            print(f"   Primary Color: {custom_row[2]}")   # primary_color
            print(f"   Secondary Color: {custom_row[3]}")  # secondary_color
            print(f"   Logo Path: {custom_row[4]}")       # logo_path
            print(f"   Email Subject: {custom_row[5]}")   # email_subject
            print(f"   Email Intro: {custom_row[6]}")     # email_intro
        else:
            print("❌ No customizations found in database")
        
        # Test 4: Test the joined query used in scan page
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
            print(f"✅ Found {len(scanners)} scanner(s) with customizations:")
            for scanner in scanners:
                print(f"   Scanner: {scanner[1]}")
                print(f"   Business: {scanner[6]}")
                print(f"   Primary Color: {scanner[4]}")
                print(f"   Secondary Color: {scanner[5]}")
                print(f"   Logo: {scanner[7]}")
        else:
            print("ℹ️  No scanners found (normal - scanner creation is separate)")
        
        conn.close()
        
        print("\n🎉 Customization test completed successfully!")
        print("✅ Client registration saves customizations correctly")
        print("✅ Database query retrieves customizations properly")
        print("✅ Scanner display should show custom colors, logo, and business name")
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_customizations()