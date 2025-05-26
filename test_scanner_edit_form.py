#!/usr/bin/env python3

import sys
import os
sys.path.append('.')

def test_scanner_edit_form():
    """Test the scanner edit form submission"""
    try:
        from client_db import update_scanner_config
        
        # Simulate form data like it would come from the form
        form_data = {
            'scanner_name': 'Updated Scanner Name',
            'business_domain': 'https://example.com',
            'contact_email': 'contact@example.com',
            'contact_phone': '+1234567890',
            'primary_color': '#ff0000',
            'secondary_color': '#00ff00',
            'button_color': '#0000ff',
            'email_subject': 'Updated Email Subject',
            'email_intro': 'Updated email intro text',
            'scanner_description': 'Updated scanner description',
            'cta_button_text': 'Click Here Now',
            'company_tagline': 'We protect everything',
            'support_email': 'support@example.com',
            'custom_footer_text': 'Custom footer text here'
        }
        
        # Test with scanner ID 1
        scanner_id = 1
        user_id = 1
        
        print(f"Testing scanner edit with data: {form_data}")
        
        result = update_scanner_config(scanner_id, form_data, user_id)
        
        print(f"Result: {result}")
        
        if result and result.get('status') == 'success':
            print("✓ Scanner edit form test succeeded!")
        else:
            print("✗ Scanner edit form test failed")
            
    except Exception as e:
        print(f"✗ Error testing form: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_scanner_edit_form()