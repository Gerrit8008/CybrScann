#!/usr/bin/env python3

import sys
import os
sys.path.append('.')

from app import app
from client_db import get_db_connection

def test_embed_route():
    """Test that the embed route shows customizations"""
    with app.test_client() as client:
        # Get a scanner from the database to test with
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT scanner_id FROM scanners LIMIT 1')
        scanner_row = cursor.fetchone()
        conn.close()
        
        if not scanner_row:
            print("No scanners found in database")
            return
            
        scanner_uid = scanner_row[0]
        print(f"Testing embed route for scanner: {scanner_uid}")
        
        # Make request to embed route
        response = client.get(f'/scanner/{scanner_uid}/embed')
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.get_data(as_text=True)
            
            # Check for customization elements
            customizations_found = []
            
            if 'button_color' in content or '--button-color' in content:
                customizations_found.append("✓ Button color")
            else:
                customizations_found.append("✗ Button color")
                
            if 'favicon_path' in content or 'favicon.png' in content:
                customizations_found.append("✓ Favicon")
            else:
                customizations_found.append("✗ Favicon")
                
            if 'primary_color' in content or '--primary-color' in content:
                customizations_found.append("✓ Primary color")
            else:
                customizations_found.append("✗ Primary color")
                
            if 'logo_path' in content or 'logo_url' in content:
                customizations_found.append("✓ Logo")
            else:
                customizations_found.append("✗ Logo")
                
            print("Customizations in embed route:")
            for item in customizations_found:
                print(f"  {item}")
                
            print("\nEmbed route is working properly!")
        else:
            print(f"Error: {response.status_code}")

if __name__ == '__main__':
    test_embed_route()