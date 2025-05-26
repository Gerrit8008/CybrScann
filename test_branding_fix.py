#!/usr/bin/env python3
"""Test to verify the branding system is working correctly"""

import sqlite3
from client_db import get_db_connection

def test_client_branding_query():
    """Test the exact query used in the scan page"""
    try:
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Test for user_id 5 (debug client)
        user_id = 5
        
        print(f"Testing branding query for user_id: {user_id}")
        
        cursor.execute('''
            SELECT 
                c.business_name,
                c.contact_email,
                cust.primary_color,
                cust.secondary_color,
                cust.logo_path,
                cust.favicon_path,
                cust.button_color,
                cust.email_subject,
                cust.email_intro
            FROM clients c
            LEFT JOIN customizations cust ON c.id = cust.client_id
            WHERE c.user_id = ?
            LIMIT 1
        ''', (user_id,))
        
        branding_row = cursor.fetchone()
        if branding_row:
            print("✓ Found branding data:")
            print(f"  Business Name: {branding_row[0]}")
            print(f"  Contact Email: {branding_row[1]}")
            print(f"  Primary Color: {branding_row[2]}")
            print(f"  Secondary Color: {branding_row[3]}")
            print(f"  Logo Path: {branding_row[4]}")
            print(f"  Favicon Path: {branding_row[5]}")
            print(f"  Button Color: {branding_row[6]}")
            print(f"  Email Subject: {branding_row[7]}")
            print(f"  Email Intro: {branding_row[8]}")
            
            # Build client_branding object like in the app
            client_branding = {
                'business_name': branding_row[0],
                'contact_email': branding_row[1],
                'primary_color': branding_row[2] or '#02054c',
                'secondary_color': branding_row[3] or '#35a310',
                'logo_path': branding_row[4] or '',
                'favicon_path': branding_row[5] or '',
                'button_color': branding_row[6] or branding_row[2] or '#02054c',
                'email_subject': branding_row[7] or 'Your Security Scan Report',
                'email_intro': branding_row[8] or ''
            }
            
            print(f"\n✓ Final client_branding object:")
            for key, value in client_branding.items():
                print(f"  {key}: {value}")
                
        else:
            print(f"❌ No branding found for user_id {user_id}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def test_session_token_creation():
    """Test creating a session token for the debug user"""
    try:
        from auth_utils import create_session
        
        # Create session for debug user  
        result = create_session(5)  # user_id 5 is debug user
        
        if result['status'] == 'success':
            print(f"✓ Session created: {result['session_token']}")
            print(f"Session will be used to test /scan page branding")
            return result['session_token']
        else:
            print(f"❌ Session creation failed: {result}")
            
    except Exception as e:
        print(f"❌ Session creation error: {e}")
        return None

if __name__ == '__main__':
    print("Testing branding system...")
    test_client_branding_query()
    print("\n" + "="*50)
    print("Testing session creation...")
    session_token = test_session_token_creation()
    
    if session_token:
        print(f"\n✓ To test the branding, visit /scan with this session:")
        print(f"Use browser developer tools to set cookie: session_token={session_token}")
        print(f"Then visit http://localhost:5000/scan to see the branded page")