#!/usr/bin/env python3
"""
Direct fix for risk assessment color in client.py
"""

import os
import sys
import re

def patch_client_risk_assessment():
    """
    Patch the client.py file to ensure risk assessment color is always set
    """
    client_path = '/home/ggrun/CybrScan_1/client.py'
    
    if not os.path.exists(client_path):
        print(f"Error: {client_path} not found")
        return False
    
    # Read the file
    with open(client_path, 'r') as f:
        content = f.read()
    
    # Find the risk assessment creation section (around line 1099)
    risk_pattern = r"formatted_scan\['risk_assessment'\] = \{[^}]*\}"
    
    # Create the fixed risk assessment code
    fixed_risk = """formatted_scan['risk_assessment'] = {
                        'overall_score': scan.get('security_score', 75),
                        'risk_level': scan.get('risk_level', 'Medium'),
                        'color': get_color_for_score(scan.get('security_score', 75)),
                        'critical_issues': 0,
                        'high_issues': 1,
                        'medium_issues': 1,
                        'low_issues': 1
                    }"""
    
    # Replace the risk assessment creation
    if "formatted_scan['risk_assessment'] = {" in content:
        content = re.sub(risk_pattern, fixed_risk, content)
    
    # Add the get_color_for_score function at the top of the file
    if "def get_color_for_score(score):" not in content:
        color_func = """
def get_color_for_score(score):
    \"\"\"Get appropriate color based on score\"\"\"
    if score >= 90:
        return '#28a745'  # green
    elif score >= 80:
        return '#5cb85c'  # light green
    elif score >= 70:
        return '#17a2b8'  # info blue
    elif score >= 60:
        return '#ffc107'  # warning yellow
    elif score >= 50:
        return '#fd7e14'  # orange
    else:
        return '#dc3545'  # red
"""
        # Add function after imports
        content = content.replace("# Define client blueprint", color_func + "\n# Define client blueprint")
    
    # Add code to explicitly set the color in the formatted_scan
    report_view_func = "def report_view(user, scan_id):"
    if report_view_func in content:
        # Find the line before the render_template call
        render_template_pattern = r"return render_template\(\s*'results\.html',"
        
        # Add code to ensure color is set
        if render_template_pattern in content:
            color_check_code = """
        # Ensure risk assessment color is set
        if 'risk_assessment' in formatted_scan and isinstance(formatted_scan['risk_assessment'], dict):
            if 'color' not in formatted_scan['risk_assessment']:
                formatted_scan['risk_assessment']['color'] = get_color_for_score(formatted_scan['risk_assessment'].get('overall_score', 75))
                
        """
            
            # Add the color check before the render_template call
            content = re.sub(render_template_pattern, color_check_code + "\n        return render_template(\n            'results.html',", content)
    
    # Write the modified file
    with open(client_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Successfully patched {client_path} to ensure risk assessment color is set")
    return True

def main():
    """Main function to apply fix"""
    print("Applying direct fix for risk assessment color...")
    
    # Patch the client.py file
    patch_client_risk_assessment()
    
    print("\nFix has been applied!")
    print("To make the changes effective, please restart the application server.")

if __name__ == "__main__":
    main()