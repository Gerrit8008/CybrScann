#!/usr/bin/env python3

import sys
import os
sys.path.append('.')

def test_scanner_update():
    """Test the update_scanner_config function directly"""
    try:
        from client_db import update_scanner_config, get_db_connection
        import sqlite3
        
        # First, let's see what scanners exist
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, client_id FROM scanners LIMIT 5")
        scanners = cursor.fetchall()
        conn.close()
        
        print("Available scanners:")
        for scanner in scanners:
            print(f"  ID: {scanner['id']}, Name: {scanner['name']}, Client ID: {scanner['client_id']}")
        
        if not scanners:
            print("No scanners found in database")
            return
            
        # Test with the first scanner
        test_scanner_id = scanners[0]['id']
        test_user_id = 1  # Assuming user 1 exists
        
        print(f"\nTesting update on scanner ID: {test_scanner_id}")
        
        # Simple test data
        test_data = {
            'scanner_name': 'Updated Test Scanner',
            'primary_color': '#ff0000',
            'secondary_color': '#00ff00',
            'button_color': '#0000ff',
            'contact_email': 'test@example.com'
        }
        
        print(f"Test data: {test_data}")
        
        # Call the function
        result = update_scanner_config(test_scanner_id, test_data, test_user_id)
        print(f"Result: {result}")
        
        if result and result.get('status') == 'success':
            print("✓ Scanner update function worked!")
        else:
            print("✗ Scanner update function failed")
            
    except Exception as e:
        print(f"✗ Error testing scanner update: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_scanner_update()