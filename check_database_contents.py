#!/usr/bin/env python3
"""
Check database contents to understand real vs sample data
"""

import sqlite3
import os
import json
from datetime import datetime

def check_database_contents():
    """Check what real data exists in the databases"""
    print("🔍 Checking database contents...")
    
    # Check main database files
    db_files = ['client_scanner.db', 'cybrscan.db', 'leads.db']
    
    for db_file in db_files:
        if os.path.exists(db_file):
            print(f"\n📁 Found database: {db_file}")
            try:
                conn = sqlite3.connect(db_file)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Get table list
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                print(f"   Tables: {tables}")
                
                # Check each table
                for table in tables:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cursor.fetchone()[0]
                        print(f"   {table}: {count} records")
                        
                        # Show sample data for key tables
                        if table in ['users', 'clients', 'scanners'] and count > 0:
                            cursor.execute(f"SELECT * FROM {table} LIMIT 3")
                            rows = cursor.fetchall()
                            print(f"     Sample records:")
                            for row in rows:
                                row_dict = dict(row)
                                # Hide sensitive data
                                if 'password' in row_dict:
                                    row_dict['password'] = '[HIDDEN]'
                                if 'api_key' in row_dict:
                                    row_dict['api_key'] = '[HIDDEN]'
                                print(f"       {row_dict}")
                    except Exception as e:
                        print(f"     Error checking {table}: {e}")
                
                conn.close()
            except Exception as e:
                print(f"   Error opening {db_file}: {e}")
        else:
            print(f"❌ Database not found: {db_file}")
    
    # Check client databases directory
    client_db_dir = 'client_databases'
    if os.path.exists(client_db_dir):
        print(f"\n📁 Found client databases directory: {client_db_dir}")
        client_dbs = [f for f in os.listdir(client_db_dir) if f.endswith('.db')]
        print(f"   Client databases: {client_dbs}")
        
        for client_db in client_dbs[:3]:  # Check first 3
            db_path = os.path.join(client_db_dir, client_db)
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Check scans table
                cursor.execute("SELECT COUNT(*) FROM scans")
                scan_count = cursor.fetchone()[0]
                print(f"   {client_db}: {scan_count} scans")
                
                if scan_count > 0:
                    cursor.execute("SELECT * FROM scans LIMIT 2")
                    scans = cursor.fetchall()
                    print(f"     Recent scans: {len(scans)} samples")
                
                conn.close()
            except Exception as e:
                print(f"   Error checking {client_db}: {e}")
    else:
        print(f"❌ Client databases directory not found: {client_db_dir}")
    
    print(f"\n📊 Summary:")
    print(f"   - Database files found and their real data counts")
    print(f"   - This will help identify what needs real data connections")
    print(f"   - Any sample/hardcoded data can be replaced with actual queries")

if __name__ == "__main__":
    check_database_contents()