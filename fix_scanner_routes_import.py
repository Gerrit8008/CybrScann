#!/usr/bin/env python3
"""
Fix for scanner_routes.py import error
Replaces 'generate_password_hash' with 'hash_password'
"""

import os
import sys

def fix_scanner_routes_import():
    """
    Fix scanner_routes.py to use hash_password instead of generate_password_hash
    """
    scanner_routes_path = '/home/ggrun/CybrScan_1/scanner_routes.py'
    
    if not os.path.exists(scanner_routes_path):
        print(f"Error: {scanner_routes_path} not found")
        return False
    
    # Read the file
    with open(scanner_routes_path, 'r') as f:
        content = f.read()
    
    # Fix the import
    if 'from auth_utils import verify_session, generate_password_hash' in content:
        content = content.replace(
            'from auth_utils import verify_session, generate_password_hash',
            'from auth_utils import verify_session, hash_password'
        )
    
    # Fix any usage of generate_password_hash
    if 'generate_password_hash(' in content:
        content = content.replace(
            'generate_password_hash(',
            'hash_password('
        )
    
    # Write the modified file
    with open(scanner_routes_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Fixed import in {scanner_routes_path}")
    return True

def main():
    """Main function to apply fix"""
    print("Fixing scanner_routes.py import error...")
    
    # Fix the scanner_routes.py import
    fix_scanner_routes_import()
    
    print("\nFix has been applied!")
    print("To make the changes effective, please restart the application server.")

if __name__ == "__main__":
    main()