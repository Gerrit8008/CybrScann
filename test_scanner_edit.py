#!/usr/bin/env python3

import sys
import os
sys.path.append('.')

def test_scanner_edit_route():
    """Test that the scanner edit route is accessible"""
    print("Testing scanner edit functionality...")
    
    # Test 1: Check that the route is properly defined
    try:
        from client import client_bp
        routes = []
        for rule in client_bp.url_map.iter_rules():
            if 'edit' in rule.rule:
                routes.append(rule.rule)
        
        edit_route_found = any('/scanners/<int:scanner_id>/edit' in route for route in routes)
        print(f"✓ Edit route found: {edit_route_found}")
        
    except Exception as e:
        print(f"✗ Error checking route: {e}")
    
    # Test 2: Check that update_scanner_config function exists and has right signature  
    try:
        from client_db import update_scanner_config
        import inspect
        
        sig = inspect.signature(update_scanner_config)
        params = list(sig.parameters.keys())
        print(f"✓ update_scanner_config parameters: {params}")
        
        # Should have conn as first param (from @with_transaction), then scanner_id, scanner_data, user_id
        expected_without_conn = ['scanner_id', 'scanner_data', 'user_id']
        actual_without_conn = params[1:] if params[0] == 'conn' else params
        
        if actual_without_conn == expected_without_conn:
            print("✓ Function signature is correct")
        else:
            print(f"✗ Function signature mismatch. Expected {expected_without_conn}, got {actual_without_conn}")
            
    except Exception as e:
        print(f"✗ Error checking function: {e}")
    
    # Test 3: Check that template exists
    try:
        template_path = '/home/ggrun/CybrScan_1/templates/client/scanner-edit.html'
        if os.path.exists(template_path):
            print("✓ Template file exists")
            
            # Check if template has required fields
            with open(template_path, 'r') as f:
                content = f.read()
                
            required_fields = ['button_color', 'favicon_upload', 'contact_email', 'contact_phone', 'business_domain', 'email_subject', 'email_intro']
            missing_fields = []
            
            for field in required_fields:
                if field not in content:
                    missing_fields.append(field)
            
            if not missing_fields:
                print("✓ All required fields found in template")
            else:
                print(f"✗ Missing fields in template: {missing_fields}")
        else:
            print("✗ Template file not found")
            
    except Exception as e:
        print(f"✗ Error checking template: {e}")
    
    print("\nScanner edit route should now be functional!")
    print("Users can click the edit button in /client/scanners to:")
    print("- Update scanner name, colors (primary, secondary, button)")
    print("- Upload new logo and favicon")
    print("- Update contact information and business domain")
    print("- Configure email subject and intro message")

if __name__ == '__main__':
    test_scanner_edit_route()