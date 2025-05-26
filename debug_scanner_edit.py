#!/usr/bin/env python3

import sys
import os
sys.path.append('.')

def debug_scanner_edit():
    """Debug the scanner edit issue step by step"""
    
    print("=== Debugging Scanner Edit Issue ===\n")
    
    # 1. Check if the database update function works
    print("1. Testing database update function...")
    try:
        from client_db import update_scanner_config
        
        test_data = {
            'scanner_name': 'Debug Test',
            'primary_color': '#123456'
        }
        
        result = update_scanner_config(1, test_data, 1)
        print(f"   Database update result: {result}")
        
        if result.get('status') == 'success':
            print("   ✓ Database update function works")
        else:
            print("   ✗ Database update function failed")
            return
    except Exception as e:
        print(f"   ✗ Database update error: {e}")
        return
    
    # 2. Check the route exists
    print("\n2. Checking route registration...")
    try:
        from client import client_bp
        
        # Find the edit route
        edit_routes = []
        for rule in client_bp.url_map.iter_rules():
            if 'edit' in rule.rule:
                edit_routes.append(f"{rule.rule} -> {rule.endpoint}")
        
        print(f"   Edit routes found: {edit_routes}")
        
        if any('scanners/<int:scanner_id>/edit' in route for route in edit_routes):
            print("   ✓ Edit route is registered")
        else:
            print("   ✗ Edit route not found")
            
    except Exception as e:
        print(f"   ✗ Route check error: {e}")
    
    # 3. Check if we can simulate a form submission
    print("\n3. Testing form data processing...")
    try:
        # Simulate what the form would send
        form_data = {
            'scanner_name': 'Test Scanner',
            'business_domain': 'https://test.com',
            'contact_email': 'test@test.com',
            'contact_phone': '123-456-7890',
            'primary_color': '#ff0000',
            'secondary_color': '#00ff00',
            'button_color': '#0000ff',
            'email_subject': 'Test Subject',
            'email_intro': 'Test intro',
            'scanner_description': 'Test description',
            'cta_button_text': 'Click Me',
            'company_tagline': 'Test tagline',
            'support_email': 'support@test.com',
            'custom_footer_text': 'Test footer'
        }
        
        print(f"   Form data keys: {list(form_data.keys())}")
        print(f"   Form data sample: {dict(list(form_data.items())[:3])}")
        
        # Test the update with this data
        result = update_scanner_config(1, form_data, 1)
        print(f"   Update result: {result}")
        
        if result.get('status') == 'success':
            print("   ✓ Form data processing works")
        else:
            print("   ✗ Form data processing failed")
            
    except Exception as e:
        print(f"   ✗ Form processing error: {e}")
        import traceback
        traceback.print_exc()
    
    # 4. Check what might be wrong with the web form
    print("\n4. Checking for common web form issues...")
    
    # Check template for CSRF token or other issues
    try:
        with open('/home/ggrun/CybrScan_1/templates/client/scanner-edit.html', 'r') as f:
            template_content = f.read()
        
        # Check for form tag
        if '<form' in template_content:
            print("   ✓ Form tag found in template")
        else:
            print("   ✗ No form tag found")
            
        # Check for method POST
        if 'method="POST"' in template_content:
            print("   ✓ POST method specified")
        else:
            print("   ✗ POST method not found")
            
        # Check for required name attributes
        required_names = ['scanner_name', 'cta_button_text', 'primary_color']
        missing_names = []
        for name in required_names:
            if f'name="{name}"' not in template_content:
                missing_names.append(name)
        
        if not missing_names:
            print("   ✓ All required form field names found")
        else:
            print(f"   ✗ Missing form field names: {missing_names}")
            
    except Exception as e:
        print(f"   ✗ Template check error: {e}")
    
    print("\n=== Debug Complete ===")

if __name__ == '__main__':
    debug_scanner_edit()