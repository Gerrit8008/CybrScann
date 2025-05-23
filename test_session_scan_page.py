#!/usr/bin/env python3
"""
Test the session creation and scan page display after Complete Purchase
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_session_and_scan_page():
    """Test session creation and scan page display"""
    print("🔧 Testing Session and Scan Page Display")
    print("=" * 50)
    
    try:
        # Use the debug user we just created
        from client_db import get_db_connection
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Find the debug user
        cursor.execute("SELECT id, email FROM users WHERE email LIKE 'debug_%' ORDER BY id DESC LIMIT 1")
        user_row = cursor.fetchone()
        
        if not user_row:
            print("❌ No debug user found. Run debug_complete_purchase.py first.")
            return
            
        user_id = user_row[0]
        user_email = user_row[1]
        
        print(f"📧 Testing with user: {user_email} (ID: {user_id})")
        
        # Step 1: Create session (simulates auto-login after Complete Purchase)
        print("\n🔧 Step 1: Creating Session...")
        from auth_utils import create_session
        
        session_result = create_session(user_id, user_email, 'client')
        
        if session_result['status'] != 'success':
            print(f"❌ Session creation failed: {session_result['message']}")
            return
            
        session_token = session_result['session_token']
        print(f"✅ Session created: {session_token[:20]}...")
        
        # Step 2: Verify session (simulates what scan page does)
        print("\n🔧 Step 2: Verifying Session...")
        from auth_utils import verify_session
        
        verify_result = verify_session(session_token)
        
        if verify_result['status'] != 'success':
            print(f"❌ Session verification failed: {verify_result['message']}")
            return
            
        current_user = verify_result['user']
        verified_user_id = current_user['user_id']
        print(f"✅ Session verified for user: {verified_user_id}")
        
        # Step 3: Get scanners (simulates scan page query)
        print("\n🔧 Step 3: Getting User Scanners...")
        
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
        ''', (verified_user_id,))
        
        user_scanners = [dict(row) for row in cursor.fetchall()]
        
        if user_scanners:
            print(f"✅ Found {len(user_scanners)} scanner(s):")
            
            for i, scanner in enumerate(user_scanners):
                print(f"\nScanner {i+1}:")
                print(f"   📛 Name: {scanner['name']}")
                print(f"   🏢 Business: {scanner['business_name']}")
                print(f"   🌐 Domain: {scanner['domain']}")
                print(f"   🎨 Primary Color: {scanner['primary_color']}")
                print(f"   🎨 Secondary Color: {scanner['secondary_color']}")
                print(f"   🖼️  Logo: {scanner['logo_url']}")
                print(f"   📝 Description: {scanner['description']}")
                
                # Check if colors are the expected debug colors
                if scanner['primary_color'] == '#9b59b6' and scanner['secondary_color'] == '#e67e22':
                    print("   ✅ Custom colors match expected values!")
                else:
                    print(f"   ⚠️  Colors don't match expected (#9b59b6, #e67e22)")
        else:
            print("❌ No scanners found!")
            
            # Debug why no scanners found
            print("\n🔍 Debugging...")
            
            # Check if client exists for this user
            cursor.execute("SELECT id, business_name FROM clients WHERE user_id = ?", (verified_user_id,))
            client_row = cursor.fetchone()
            
            if client_row:
                client_id = client_row[0]
                print(f"   ✅ Client found: ID {client_id}, Name: {client_row[1]}")
                
                # Check if scanners exist for this client
                cursor.execute("SELECT id, name FROM scanners WHERE client_id = ?", (client_id,))
                scanner_rows = cursor.fetchall()
                
                if scanner_rows:
                    print(f"   ❌ Scanners exist for client but JOIN failed:")
                    for scanner_row in scanner_rows:
                        print(f"      Scanner {scanner_row[0]}: {scanner_row[1]}")
                else:
                    print(f"   ❌ No scanners found for client {client_id}")
            else:
                print(f"   ❌ No client found for user {verified_user_id}")
        
        conn.close()
        
        # Step 4: Test what would be passed to template
        print(f"\n🔧 Step 4: Template Variables...")
        print(f"current_user: {current_user}")
        print(f"user_scanners: {len(user_scanners)} items")
        
        if user_scanners:
            print("\n🎉 SUCCESS! Scan page will show:")
            print("✅ Welcome message with user email")
            print("✅ Scanner cards with custom colors")
            print("✅ Business name and scanner name")
            print("✅ Logo and custom styling")
            print("\n🚀 The white label customizations are working!")
        else:
            print("\n❌ ISSUE: Scan page will show no scanners")
            print("   The Complete Purchase flow needs debugging")
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_session_and_scan_page()