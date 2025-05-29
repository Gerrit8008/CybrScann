#!/usr/bin/env python3
"""
Direct fix for results.html template
Ensures the template properly uses risk assessment color
"""

import os
import sys
import re

def fix_results_template():
    """
    Fix results.html template to properly use risk assessment color
    """
    template_path = '/home/ggrun/CybrScan_1/templates/results.html'
    
    if not os.path.exists(template_path):
        print(f"Error: Template file not found: {template_path}")
        return False
    
    # Read the template
    with open(template_path, 'r') as f:
        content = f.read()
    
    # Check if the template is already using risk_assessment.color
    if 'stroke: {{ scan.risk_assessment.color|default(' in content:
        print("Template already fixed to use risk_assessment.color")
        return True
    
    # Find the gauge SVG section
    gauge_circle_pattern = r'<circle class="gauge-value"[^>]*>\s*</circle>'
    gauge_text_pattern = r'<text class="gauge-text"[^>]*>\s*{{ scan\.risk_assessment\.overall_score }}\s*</text>'
    
    # Fix the gauge circle
    if '<circle class="gauge-value"' in content:
        # Replace with fixed version using risk_assessment.color
        fixed_circle = """<circle class="gauge-value" r="54" cx="60" cy="60" stroke-width="12" 
                                    style="stroke: {{ scan.risk_assessment.color|default('#17a2b8') }}; 
                                           stroke-dasharray: {{ scan.risk_assessment.overall_score * 3.39 }} 339;"></circle>"""
        
        content = re.sub(gauge_circle_pattern, fixed_circle, content)
    
    # Fix the gauge text
    if '<text class="gauge-text"' in content:
        # Replace with fixed version using risk_assessment.color
        fixed_text = """<text class="gauge-text" x="60" y="60" text-anchor="middle" alignment-baseline="middle"
                                  style="fill: {{ scan.risk_assessment.color|default('#17a2b8') }};">
                                {{ scan.risk_assessment.overall_score }}
                            </text>"""
        
        content = re.sub(gauge_text_pattern, fixed_text, content)
    
    # Write the updated template
    with open(template_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Fixed template file: {template_path}")
    return True

def main():
    """Main function to apply fix"""
    print("Applying direct fix for results template...")
    
    # Fix the results template
    fix_results_template()
    
    print("\nFix has been applied!")
    print("To make the changes effective, please restart the application server.")

if __name__ == "__main__":
    main()