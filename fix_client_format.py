#!/usr/bin/env python3
"""
Fix for client.py - formatted_scan assignment issue
"""

import os
import re

def fix_client_report_view():
    """
    Fix the double assignment to formatted_scan in client.py
    """
    client_path = '/home/ggrun/CybrScan_1/client.py'
    
    if not os.path.exists(client_path):
        print(f"Error: {client_path} not found")
        return False
    
    # Read the file
    with open(client_path, 'r') as f:
        content = f.read()
    
    # Find the problematic section
    if "# Apply processing to ensure all needed data is present" in content and "formatted_scan = process_scan_data(scan)" in content:
        # Check if there's a double assignment
        if "formatted_scan = scan" in content and content.find("formatted_scan = process_scan_data(scan)") < content.find("formatted_scan = scan"):
            # Fix the double assignment
            content = content.replace("# Apply processing to ensure all needed data is present\n        formatted_scan = process_scan_data(scan)", 
                                     "# Apply processing to ensure all needed data is present")
    
    # Write the modified file
    with open(client_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Fixed client.py formatted_scan assignment")
    return True

def apply_process_scan_data():
    """
    Apply the process_scan_data function properly in client.py
    """
    client_path = '/home/ggrun/CybrScan_1/client.py'
    
    if not os.path.exists(client_path):
        print(f"Error: {client_path} not found")
        return False
    
    # Read the file
    with open(client_path, 'r') as f:
        content = f.read()
    
    # Find the report_view function
    report_view_pattern = r"@client_bp\.route\('/reports/<scan_id>'\)(.*?)def report_view\([^)]*\):(?:[^@]*)(?=@|$)"
    report_view_match = re.search(report_view_pattern, content, re.DOTALL)
    
    if report_view_match:
        original_report_view = report_view_match.group(0)
        
        # Replace the existing formatted_scan assignments
        if "formatted_scan = scan" in original_report_view:
            # Find where we assign to formatted_scan
            format_pattern = r"# Format scan data for template.*?formatted_scan = scan"
            format_match = re.search(format_pattern, original_report_view, re.DOTALL)
            
            if format_match:
                original_format = format_match.group(0)
                # Replace with process_scan_data
                new_format = """# Format scan data for template - preserve comprehensive scan data
        formatted_scan = process_scan_data(scan)"""
                modified_report_view = original_report_view.replace(original_format, new_format)
                
                # Update the content
                content = content.replace(original_report_view, modified_report_view)
    
    # Write the modified file
    with open(client_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Applied process_scan_data function in client.py")
    return True

def main():
    """Main function to apply fixes"""
    print("Fixing client.py formatting issues...")
    
    # Fix the formatted_scan assignment
    fix_client_report_view()
    
    # Apply the process_scan_data function properly
    apply_process_scan_data()
    
    print("\nFixes have been applied!")
    print("To make the changes effective, please restart the application server.")

if __name__ == "__main__":
    main()