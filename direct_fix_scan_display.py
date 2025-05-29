#!/usr/bin/env python3
"""
Direct fix to implement CybrScan_1's process_scan_data function in CybrScann-main
"""
import os
import re
import shutil

def main():
    """Directly copy process_scan_data from CybrScan_1 to CybrScann-main"""
    print("Applying direct fix for scan display issues...")
    
    # Source paths
    source_client = '/home/ggrun/CybrScan_1/client.py'
    
    # Destination paths
    dest_client = '/home/ggrun/CybrScann-main/client.py'
    
    # Create backups
    shutil.copy2(dest_client, f"{dest_client}.bak")
    print(f"Created backup: {dest_client}.bak")
    
    # Read the process_scan_data function from CybrScan_1
    with open(source_client, 'r') as f:
        source_content = f.read()
    
    # Extract the process_scan_data function
    process_scan_data_pattern = r'def process_scan_data\(scan\):.*?return scan_data'
    process_scan_match = re.search(process_scan_data_pattern, source_content, re.DOTALL)
    
    if not process_scan_match:
        print("❌ Error: Couldn't find process_scan_data function in CybrScan_1")
        return
    
    process_scan_data_func = process_scan_match.group(0)
    
    # Extract the detect_os_and_browser function
    detect_os_pattern = r'def detect_os_and_browser\(user_agent\):.*?return os_info, browser_info'
    detect_os_match = re.search(detect_os_pattern, source_content, re.DOTALL)
    
    if not detect_os_match:
        print("❌ Error: Couldn't find detect_os_and_browser function in CybrScan_1")
        return
    
    detect_os_func = detect_os_match.group(0)
    
    # Now modify the destination file
    with open(dest_client, 'r') as f:
        dest_content = f.read()
    
    # First add import for re if not present
    if "import re" not in dest_content:
        dest_content = dest_content.replace("import os", "import os\nimport re")
    
    # Add the functions after the import section
    blueprint_def = dest_content.find("# Define client blueprint")
    if blueprint_def == -1:
        print("❌ Error: Couldn't find blueprint definition in CybrScann-main client.py")
        return
    
    # Add both functions before the blueprint definition
    dest_content = (
        dest_content[:blueprint_def] + 
        "\n" + process_scan_data_func + "\n\n" + 
        detect_os_func + "\n\n" + 
        dest_content[blueprint_def:]
    )
    
    # Modify the report_view function to use process_scan_data
    report_view_pattern = r'def report_view\(user, scan_id\):.*?formatted_scan = format_scan_results_for_client\(scan\)'
    report_view_repl = lambda m: m.group(0).replace(
        "formatted_scan = format_scan_results_for_client(scan)",
        "# Format scan results using the enhanced processor for proper port/OS display\n        formatted_scan = process_scan_data(scan)"
    )
    
    dest_content = re.sub(report_view_pattern, report_view_repl, dest_content, flags=re.DOTALL)
    
    # Write the updated content
    with open(dest_client, 'w') as f:
        f.write(dest_content)
    
    print(f"✅ Successfully added process_scan_data and detect_os_and_browser functions to {dest_client}")
    print(f"✅ Modified report_view to use process_scan_data instead of format_scan_results_for_client")
    print("\nNow the CybrScann-main reports will show port scan results and OS information just like in CybrScan_1.")
    print("To activate the changes, restart the application server.")

if __name__ == "__main__":
    main()