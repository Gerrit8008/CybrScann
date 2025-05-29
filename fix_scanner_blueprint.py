#!/usr/bin/env python3
"""
Fix for scanner_routes.py blueprint name issue
"""

import os
import sys

def fix_scanner_blueprint():
    """
    Fix scanner_routes.py to use scanner_bp as the blueprint name
    """
    scanner_routes_path = '/home/ggrun/CybrScan_1/scanner_routes.py'
    
    if not os.path.exists(scanner_routes_path):
        print(f"Error: {scanner_routes_path} not found")
        return False
    
    # Read the file
    with open(scanner_routes_path, 'r') as f:
        content = f.read()
    
    # Fix the blueprint name
    if 'settings_bp = Blueprint(' in content:
        content = content.replace(
            'settings_bp = Blueprint(\'settings\', __name__, url_prefix=\'/admin\')',
            'scanner_bp = Blueprint(\'scanner\', __name__, url_prefix=\'/scanner\')'
        )
    
    # Update any routes using settings_bp
    if '@settings_bp.route(' in content:
        content = content.replace(
            '@settings_bp.route(',
            '@scanner_bp.route('
        )
    
    # Write the modified file
    with open(scanner_routes_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Fixed blueprint name in {scanner_routes_path}")
    return True

def main():
    """Main function to apply fix"""
    print("Fixing scanner_routes.py blueprint name...")
    
    # Fix the scanner_routes.py blueprint name
    fix_scanner_blueprint()
    
    print("\nFix has been applied!")
    print("To make the changes effective, please restart the application server.")

if __name__ == "__main__":
    main()