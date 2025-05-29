#!/usr/bin/env python3
"""
Fix scanner creation to prevent the 'client 6' prefix issue
This module patches the scanner creation function in scanner_db_functions.py
"""

import os
import sys
import re

def apply_scanner_creation_fix():
    """
    Apply fix to scanner_db_functions.py to prevent adding 'client 6' prefix
    """
    # Path to the scanner_db_functions.py file
    scanner_db_file = '/home/ggrun/CybrScan_1/scanner_db_functions.py'
    
    if not os.path.exists(scanner_db_file):
        print(f"Error: {scanner_db_file} not found")
        return False
    
    # Read the file
    with open(scanner_db_file, 'r') as f:
        content = f.read()
    
    # Look for the create_scanner_for_client function
    if 'def create_scanner_for_client' not in content:
        print("Error: create_scanner_for_client function not found")
        return False
    
    # Check if the function has already been fixed
    if '# Fixed to prevent client 6 prefix issue' in content:
        print("Scanner creation function already fixed")
        return True
    
    # Find the line that might be creating the problem (looking for setting the name)
    pattern = r'(scanner_data\s*=\s*{[^}]*["\']name["\']\s*:\s*)(.*?),'
    match = re.search(pattern, content)
    
    if not match:
        print("Could not find the scanner name assignment pattern")
        return False
    
    # Modify the function to ensure it doesn't add 'client 6' prefix
    # Add a comment and fix the name assignment
    modified_content = content.replace(
        'def create_scanner_for_client(client_id, scanner_data, user_id):',
        'def create_scanner_for_client(client_id, scanner_data, user_id):\n    # Fixed to prevent client 6 prefix issue'
    )
    
    # Replace the problematic code with a safeguard
    modified_content = re.sub(
        pattern,
        r'\1scanner_data.get("name", "").replace("client 6", "").strip(),',
        modified_content
    )
    
    # Add a final safeguard right before inserting into the database
    insert_pattern = r'(cursor\.execute\([^)]*INSERT INTO scanners)'
    modified_content = re.sub(
        insert_pattern,
        r'# Ensure name doesn\'t have client 6 prefix\n        if "name" in scanner_data and isinstance(scanner_data["name"], str):\n            scanner_data["name"] = scanner_data["name"].replace("client 6", "").strip()\n        \n        \1',
        modified_content
    )
    
    # Write the modified file
    with open(scanner_db_file, 'w') as f:
        f.write(modified_content)
    
    print(f"✅ Successfully fixed {scanner_db_file} to prevent 'client 6' prefix")
    return True

if __name__ == "__main__":
    print("Applying scanner creation fix...")
    apply_scanner_creation_fix()
    print("Fix complete. Please restart the application server.")