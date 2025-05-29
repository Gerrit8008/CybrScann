#!/usr/bin/env python3
"""
Fix script to remove 'Client 6' prefix from client business names
"""

import sqlite3
import json

def fix_client_business_names():
    """Remove 'Client 6' prefix from client business names in client_scanner.db"""
    try:
        # Connect to client_scanner.db
        conn = sqlite3.connect('client_scanner.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get all clients
        cursor.execute("SELECT id, business_name FROM clients")
        clients = cursor.fetchall()
        
        fixed_count = 0
        for client in clients:
            client_id = client['id']
            business_name = client['business_name']
            
            # Check if business_name has 'Client 6' prefix
            if business_name and isinstance(business_name, str) and business_name.startswith('Client 6'):
                # Remove 'Client 6' prefix
                fixed_name = business_name.replace('Client 6', '').strip()
                
                # Update the client record
                cursor.execute(
                    "UPDATE clients SET business_name = ? WHERE id = ?",
                    (fixed_name, client_id)
                )
                print(f"Fixed client {client_id}: '{business_name}' -> '{fixed_name}'")
                fixed_count += 1
        
        # Commit changes
        conn.commit()
        
        # Also check scanners table for any name issues
        cursor.execute("SELECT id, name FROM scanners")
        scanners = cursor.fetchall()
        
        scanner_fixed_count = 0
        for scanner in scanners:
            scanner_id = scanner['id']
            scanner_name = scanner['name']
            
            # Check if scanner_name has 'Client 6' prefix
            if scanner_name and isinstance(scanner_name, str) and scanner_name.startswith('Client 6'):
                # Remove 'Client 6' prefix
                fixed_name = scanner_name.replace('Client 6', '').strip()
                
                # Update the scanner record
                cursor.execute(
                    "UPDATE scanners SET name = ? WHERE id = ?",
                    (fixed_name, scanner_id)
                )
                print(f"Fixed scanner {scanner_id}: '{scanner_name}' -> '{fixed_name}'")
                scanner_fixed_count += 1
        
        conn.commit()
        conn.close()
        
        print(f"Fixed {fixed_count} client names and {scanner_fixed_count} scanner names")
        return fixed_count + scanner_fixed_count
        
    except Exception as e:
        print(f"Error fixing client business names: {e}")
        return 0

if __name__ == "__main__":
    print("Fixing client business names to remove 'Client 6' prefix...")
    fix_client_business_names()
    print("Done!")