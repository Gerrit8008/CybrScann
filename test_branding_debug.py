#!/usr/bin/env python3

import sqlite3
import os

def debug_client_branding():
    """Debug script to check client branding data"""
    
    db_path = 'client_scanner.db'
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        print("🔍 Checking clients table...")
        cursor.execute('SELECT id, user_id, business_name, contact_email FROM clients ORDER BY created_at DESC LIMIT 5')
        clients = cursor.fetchall()
        
        for client in clients:
            print(f"Client ID: {client[0]}, User ID: {client[1]}, Business: {client[2]}, Email: {client[3]}")
        
        print("\n🎨 Checking customizations table...")
        # First check table structure
        cursor.execute("PRAGMA table_info(customizations)")
        columns = cursor.fetchall()
        print("Customizations table columns:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        cursor.execute('SELECT client_id, primary_color, secondary_color, logo_path, favicon_path FROM customizations LIMIT 5')
        customizations = cursor.fetchall()
        
        for custom in customizations:
            print(f"Client ID: {custom[0]}, Colors: {custom[1]}/{custom[2]}, Logo: {custom[3]}, Favicon: {custom[4]}")
        
        print("\n🔗 Checking client-customization joins...")
        cursor.execute('''
            SELECT 
                c.id as client_id,
                c.user_id,
                c.business_name,
                cust.primary_color,
                cust.secondary_color,
                cust.logo_path,
                cust.favicon_path
            FROM clients c
            LEFT JOIN customizations cust ON c.id = cust.client_id
            ORDER BY c.created_at DESC
            LIMIT 5
        ''')
        
        joined_data = cursor.fetchall()
        for row in joined_data:
            print(f"User ID: {row[1]}, Business: {row[2]}, Logo: {row[5]}, Colors: {row[3]}/{row[4]}")
            
            # Check if logo file exists
            if row[5]:  # logo_path
                full_path = f"static{row[5].replace('/static', '')}" if row[5].startswith('/static') else row[5]
                exists = os.path.exists(full_path)
                print(f"  → Logo file exists: {exists} ({full_path})")
        
        print("\n📁 Checking uploads directory...")
        uploads_dir = 'static/uploads'
        if os.path.exists(uploads_dir):
            files = os.listdir(uploads_dir)
            logo_files = [f for f in files if f.startswith('logo_')]
            favicon_files = [f for f in files if f.startswith('favicon_')]
            print(f"Logo files: {len(logo_files)}")
            print(f"Favicon files: {len(favicon_files)}")
            for f in logo_files[:3]:  # Show first 3
                print(f"  • {f}")
        else:
            print(f"❌ Uploads directory not found: {uploads_dir}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_client_branding()