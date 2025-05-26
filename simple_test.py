#!/usr/bin/env python3
"""Simple test to check button color implementation"""

import tempfile
import os

def test_css_only():
    """Test just the CSS generation with button color"""
    from scanner_deployment import generate_scanner_css
    
    scanner_data = {
        'business_name': 'Test Company',
        'primary_color': '#ff0000',
        'secondary_color': '#00ff00', 
        'button_color': '#0000ff'
    }
    
    with tempfile.TemporaryDirectory() as temp_dir:
        success = generate_scanner_css(temp_dir, scanner_data)
        if success:
            css_path = os.path.join(temp_dir, 'scanner-styles.css')
            with open(css_path, 'r') as f:
                css_content = f.read()
            
            print("✓ CSS Generated successfully")
            print(f"✓ Button color #0000ff found in CSS: {'#0000ff' in css_content}")
            print(f"✓ Button class found: {'scanner-submit-btn' in css_content}")
            
            # Show a snippet of the button CSS
            lines = css_content.split('\n')
            for i, line in enumerate(lines):
                if 'scanner-submit-btn' in line and 'background:' in lines[i+1]:
                    print(f"Button CSS: {lines[i+1].strip()}")
                    break
        else:
            print("❌ CSS generation failed")

if __name__ == '__main__':
    test_css_only()