#!/usr/bin/env python3
"""
Debug script to check why scan counts are showing 0
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from client_db import get_db_connection
from client_database_manager import get_scanner_scan_count
from scanner_db_functions import get_scanners_by_client_id
import sqlite3

def debug_scan_counts():
    """Debug scan count issues"""
    print("🔍 Debugging scan count issues...")
    
    # Check main database scanners
    print("\n1. Checking main database scanners...")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, scanner_id, name, client_id, status FROM scanners ORDER BY id")
        scanners = cursor.fetchall()
        
        print(f"   Found {len(scanners)} scanners in main database:")
        for scanner in scanners:
            print(f"   - ID: {scanner[0]}, scanner_id: '{scanner[1]}', name: '{scanner[2]}', client_id: {scanner[3]}, status: {scanner[4]}")
        
        conn.close()
    except Exception as e:
        print(f"   ❌ Error checking main database: {e}")
        return
    
    # Check client-specific databases
    print("\n2. Checking client-specific databases...")
    for client_id in [1, 2, 3]:  # Check first few clients
        db_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'client_databases')
        db_path = os.path.join(db_dir, f'client_{client_id}_scans.db')
        print(f"\n   Client {client_id} database: {db_path}")
        
        if os.path.exists(db_path):
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Check scans table
                cursor.execute("SELECT scanner_id, COUNT(*) FROM scans GROUP BY scanner_id")
                scan_counts = cursor.fetchall()
                
                print(f"     Scans by scanner_id:")
                for scanner_id, count in scan_counts:
                    print(f"       - '{scanner_id}': {count} scans")
                
                conn.close()
            except Exception as e:
                print(f"     ❌ Error reading client database: {e}")
        else:
            print(f"     ⚠️ Database does not exist")
    
    # Test get_scanners_by_client_id function
    print("\n3. Testing get_scanners_by_client_id function...")
    for client_id in [1, 2, 3]:
        try:
            scanners = get_scanners_by_client_id(client_id)
            print(f"\n   Client {client_id} scanners from function:")
            for scanner in scanners:
                scanner_id = scanner.get('scanner_id', 'missing')
                scan_count = scanner.get('scan_count', 'missing')
                name = scanner.get('name', 'missing')
                print(f"     - {name} ('{scanner_id}'): {scan_count} scans")
        except Exception as e:
            print(f"     ❌ Error getting scanners for client {client_id}: {e}")
    
    # Test individual scanner scan count lookups
    print("\n4. Testing individual scanner scan count lookups...")
    
    # Get all scanner_ids from main database
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT scanner_id, client_id FROM scanners WHERE client_id IN (1,2,3)")
        scanner_data = cursor.fetchall()
        conn.close()
        
        for scanner_id, client_id in scanner_data:
            count = get_scanner_scan_count(client_id, scanner_id)
            print(f"     Client {client_id}, Scanner '{scanner_id}': {count} scans")
            
    except Exception as e:
        print(f"     ❌ Error testing individual lookups: {e}")

if __name__ == "__main__":
    debug_scan_counts()