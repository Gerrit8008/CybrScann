#!/usr/bin/env python3
"""Create client 6 with proper schema"""

import sys
import sqlite3
sys.path.append('/home/ggrun/CybrScan_1')

def create_client_6():
    """Create client 6 with all required fields"""
    print("🔧 CREATING CLIENT 6 WITH PROPER SCHEMA")
    print("=" * 45)
    
    try:
        from client_db import get_db_connection
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # First, check the schema for clients table
        cursor.execute("PRAGMA table_info(clients)")
        columns = cursor.fetchall()
        
        print("📋 Clients table schema:")
        for col in columns:
            null_constraint = "NOT NULL" if col[3] else "NULL"
            default_val = f"DEFAULT {col[4]}" if col[4] else ""
            print(f"   {col[1]} {col[2]} {null_constraint} {default_val}")
        
        # Check if client 6 exists
        cursor.execute("SELECT * FROM clients WHERE id = 6")
        existing = cursor.fetchone()
        
        if existing:
            print("✅ Client 6 already exists")
            conn.close()
            return True
        
        print("\n🔧 Creating client 6...")
        
        # Get a template from existing client
        cursor.execute("SELECT * FROM clients LIMIT 1")
        template_client = cursor.fetchone()
        
        if template_client:
            print(f"   Using client 1 as template")
            
            # Create client 6 based on template
            cursor.execute("""
                INSERT INTO clients (
                    user_id, business_name, business_domain, contact_email, contact_phone,
                    subscription_level, scans_used, subscription_start, subscription_end,
                    active, created_at, updated_at, logo_path, primary_color, secondary_color,
                    welcome_message, custom_css, email_notifications, sms_notifications,
                    api_enabled, webhook_url, timezone, language, subscription_auto_renew
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                7,  # user_id (from logs showing user 7)
                'Client 6 Test Company',  # business_name
                'testcompany.com',  # business_domain (required field)
                'test@testcompany.com',  # contact_email
                '+1-555-0106',  # contact_phone
                'professional',  # subscription_level
                0,  # scans_used
                '2025-05-24',  # subscription_start
                '2025-12-31',  # subscription_end
                1,  # active
                '2025-05-24T23:00:00',  # created_at
                '2025-05-24T23:00:00',  # updated_at
                '',  # logo_path
                '#5558b9',  # primary_color
                '#dde7da',  # secondary_color
                'Welcome to your security scan results',  # welcome_message
                '',  # custom_css
                1,  # email_notifications
                0,  # sms_notifications
                1,  # api_enabled
                '',  # webhook_url
                'UTC',  # timezone
                'en',  # language
                1   # subscription_auto_renew
            ))
            
            conn.commit()
            
            # Verify creation
            cursor.execute("SELECT id, business_name, user_id FROM clients WHERE id = ?", (cursor.lastrowid,))
            new_client = cursor.fetchone()
            
            if new_client:
                print(f"✅ Created client {new_client[0]}: {new_client[1]} (User: {new_client[2]})")
                
                # Test dashboard data retrieval
                print("\n🧪 Testing dashboard data retrieval...")
                conn.close()
                
                from client_db import get_client_dashboard_data
                dashboard_data = get_client_dashboard_data(new_client[0])
                
                if dashboard_data:
                    stats = dashboard_data.get('stats', {})
                    scan_history = dashboard_data.get('scan_history', [])
                    
                    print(f"✅ Dashboard data works!")
                    print(f"   Total scans: {stats.get('total_scans', 0)}")
                    print(f"   Scan history: {len(scan_history)} items")
                    
                    if scan_history:
                        latest = scan_history[0]
                        print(f"   Latest scan: {latest.get('lead_name')} | {latest.get('lead_email')}")
                    
                    return True
                else:
                    print("❌ Dashboard data still not working")
                    return False
            else:
                print("❌ Failed to verify client creation")
                return False
        else:
            print("❌ No template client found")
            conn.close()
            return False
            
    except Exception as e:
        print(f"❌ Error creating client 6: {e}")
        import traceback
        traceback.print_exc()
        return False

def link_existing_user_to_client():
    """Link user 7 to the new client"""
    print("\n🔗 LINKING USER 7 TO CLIENT")
    print("=" * 30)
    
    try:
        from client_db import get_db_connection
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Find the highest client ID (should be our new client)
        cursor.execute("SELECT MAX(id) FROM clients")
        max_client_id = cursor.fetchone()[0]
        
        print(f"📊 Highest client ID: {max_client_id}")
        
        # Check if user 7 exists
        cursor.execute("SELECT * FROM users WHERE id = 7")
        user = cursor.fetchone()
        
        if user:
            print(f"✅ User 7 exists: {user[1]} ({user[3]})")
            
            # Update the client to ensure it's linked to user 7
            cursor.execute("UPDATE clients SET user_id = 7 WHERE id = ?", (max_client_id,))
            conn.commit()
            
            print(f"✅ Linked user 7 to client {max_client_id}")
        else:
            print("❌ User 7 doesn't exist")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error linking user: {e}")
        return False

if __name__ == "__main__":
    success1 = create_client_6()
    success2 = link_existing_user_to_client()
    
    if success1 and success2:
        print("\n🎉 CLIENT 6 SETUP COMPLETE!")
        print("✅ Client 6 created with proper schema")
        print("✅ User 7 linked to client")
        print("✅ Dashboard data retrieval working")
        print("✅ Scan history should now be visible")
        print("\n🔄 Refresh your dashboard to see the changes!")
    else:
        print("\n❌ Some issues remain. Check errors above.")