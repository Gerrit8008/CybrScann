#!/usr/bin/env python3
"""
Fix script for scanner_routes.py to correct the scanner_id column issue
"""

import os
import sqlite3

def check_scanner_table_schema():
    """Check the scanner table schema in client databases to determine the correct column name"""
    db_paths = []
    for i in range(1, 7):  # Checking client_1 through client_6
        db_path = f'/home/ggrun/CybrScan_1/client_databases/client_{i}_scans.db'
        if os.path.exists(db_path):
            db_paths.append(db_path)
    
    column_names = set()
    
    for db_path in db_paths:
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Check if scanners table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='scanners'")
            if cursor.fetchone():
                # Get column names from scanners table
                cursor.execute("PRAGMA table_info(scanners)")
                table_info = cursor.fetchall()
                for column in table_info:
                    column_names.add(column['name'])
                
                # Check for specific rows to see actual data
                cursor.execute("SELECT * FROM scanners LIMIT 1")
                row = cursor.fetchone()
                if row:
                    print(f"Sample scanner data from {db_path}: {dict(row)}")
            else:
                print(f"No scanners table found in {db_path}")
            
            conn.close()
        except Exception as e:
            print(f"Error checking {db_path}: {str(e)}")
    
    return column_names

def fix_scanner_embed_route():
    """Fix the scanner_id query in scanner_routes.py based on the actual column name"""
    scanner_routes_path = '/home/ggrun/CybrScan_1/scanner_routes.py'
    
    # First, check the schema to determine the correct column name
    column_names = check_scanner_table_schema()
    
    id_column = None
    if 'scanner_id' in column_names:
        id_column = 'scanner_id'
    elif 'id' in column_names:
        id_column = 'id'
    else:
        # If we can't determine the column name, try both with a fallback
        id_column = 'id'  # Default to 'id' if uncertain
        
    print(f"Scanner table columns found: {column_names}")
    print(f"Using '{id_column}' as the scanner identifier column")
    
    with open(scanner_routes_path, 'r') as f:
        content = f.read()
    
    # Prepare a more robust query that tries both column names
    # This will work regardless of which column name is correct
    robust_query = """
        # Get scanner details
        try:
            # First try with scanner_id column
            cursor.execute(
                "SELECT * FROM scanners WHERE scanner_id = ?", 
                (scanner_id,)
            )
            scanner = cursor.fetchone()
            
            # If that fails, try with id column
            if not scanner:
                cursor.execute(
                    "SELECT * FROM scanners WHERE id = ?", 
                    (scanner_id,)
                )
                scanner = cursor.fetchone()
        except sqlite3.OperationalError:
            # If scanner_id column doesn't exist, try with id column
            cursor.execute(
                "SELECT * FROM scanners WHERE id = ?", 
                (scanner_id,)
            )
            scanner = cursor.fetchone()
    """
    
    # Replace the current scanner query with our robust version
    original_query = """        # Get scanner details
        cursor.execute(
            "SELECT * FROM scanners WHERE scanner_id = ?", 
            (scanner_id,)
        )
        scanner = cursor.fetchone()"""
    
    if original_query in content:
        content = content.replace(original_query, robust_query)
        
        with open(scanner_routes_path, 'w') as f:
            f.write(content)
        
        print("Updated scanner_routes.py with a more robust scanner query")
    else:
        print("Could not find the original scanner query in scanner_routes.py")

if __name__ == "__main__":
    print("Fixing scanner_id column issue...")
    fix_scanner_embed_route()
    print("Done!")