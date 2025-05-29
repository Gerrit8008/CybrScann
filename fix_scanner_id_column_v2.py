#!/usr/bin/env python3
"""
Fix script for scanner_routes.py to correct the scanner_id column issue
"""

import os
import sqlite3

def check_scanner_table_schema():
    """Check the scanner table schema in all databases to determine the correct column name"""
    # Include all possible database files
    db_paths = [
        '/home/ggrun/CybrScan_1/cybrscan.db',
        '/home/ggrun/CybrScan_1/leads.db', 
        '/home/ggrun/CybrScan_1/client_scanner.db'
    ]
    
    column_names = set()
    found_scanners_table = False
    
    for db_path in db_paths:
        if not os.path.exists(db_path):
            print(f"Database not found: {db_path}")
            continue
            
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Check if scanners table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='scanners'")
            if cursor.fetchone():
                found_scanners_table = True
                print(f"Found scanners table in {db_path}")
                
                # Get column names from scanners table
                cursor.execute("PRAGMA table_info(scanners)")
                table_info = cursor.fetchall()
                for column in table_info:
                    column_names.add(column['name'])
                    print(f"  Column: {column['name']}")
                
                # Check for specific rows to see actual data
                cursor.execute("SELECT * FROM scanners LIMIT 1")
                row = cursor.fetchone()
                if row:
                    print(f"  Sample scanner data: {dict(row)}")
            
            conn.close()
        except Exception as e:
            print(f"Error checking {db_path}: {str(e)}")
    
    if not found_scanners_table:
        print("WARNING: No scanners table found in any database!")
        
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
    robust_query = """        # Get scanner details - using robust query to handle different column names
        scanner = None
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
        except sqlite3.OperationalError as e:
            # If scanner_id column doesn't exist, try with id column
            print(f"DB Error (trying alternate column): {e}")
            cursor.execute(
                "SELECT * FROM scanners WHERE id = ?", 
                (scanner_id,)
            )
            scanner = cursor.fetchone()"""
    
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
        
        # Let's try to search for a similar pattern
        import re
        pattern = r'# Get scanner details\s+cursor\.execute\('
        match = re.search(pattern, content)
        if match:
            start_pos = match.start()
            end_pos = content.find("scanner = cursor.fetchone()", start_pos) + len("scanner = cursor.fetchone()")
            
            if start_pos >= 0 and end_pos > start_pos:
                original_query_alt = content[start_pos:end_pos]
                content = content.replace(original_query_alt, robust_query)
                
                with open(scanner_routes_path, 'w') as f:
                    f.write(content)
                
                print("Updated scanner_routes.py with a more robust scanner query (using regex search)")
            else:
                print("Could not find the scanner query section in scanner_routes.py")
        else:
            print("Could not find any matching scanner query pattern in scanner_routes.py")

if __name__ == "__main__":
    print("Fixing scanner_id column issue...")
    fix_scanner_embed_route()
    print("Done!")