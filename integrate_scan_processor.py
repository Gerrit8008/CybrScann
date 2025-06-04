#!/usr/bin/env python3
"""
Script to integrate the enhanced scan data processor into the restructured codebase
"""

import os
import sys
import re
import shutil
import time

def ensure_directory_structure():
    """Ensure the scanner directory structure exists"""
    os.makedirs('scanner', exist_ok=True)
    
    if not os.path.exists('scanner/__init__.py'):
        with open('scanner/__init__.py', 'w') as f:
            f.write("""# Scanner package
# This file imports all scanner modules and functions
from .data_processor import *
""")

def backup_files():
    """Create backups of files we'll modify"""
    timestamp = int(time.time())
    
    files_to_backup = [
        'client.py',
        'client_db.py',
        'app.py'
    ]
    
    for file in files_to_backup:
        if os.path.exists(file):
            backup = f"{file}.{timestamp}.bak"
            shutil.copy2(file, backup)
            print(f"✅ Created backup: {backup}")

def update_client_py():
    """
    Update client.py to use the enhanced scan data processor
    """
    if not os.path.exists('client.py'):
        print("❌ client.py does not exist")
        return False
    
    with open('client.py', 'r') as f:
        content = f.read()
    
    # Check if process_scan_data is defined in this file
    if "def process_scan_data" in content:
        # Replace the function definition with an import
        pattern = r"def process_scan_data\(.*?\):(.*?)(?=\ndef |\Z)"
        
        import_replacement = """
# Import the scan data processor from the modular structure
from scanner.data_processor import process_scan_data, detect_os_and_browser, get_risk_level, get_color_for_score, enhance_report_view
"""
        
        # Remove the function definition
        content = re.sub(pattern, "", content, flags=re.DOTALL)
        
        # Remove the detect_os_and_browser function if it exists
        if "def detect_os_and_browser" in content:
            pattern = r"def detect_os_and_browser\(.*?\):(.*?)(?=\ndef |\Z)"
            content = re.sub(pattern, "", content, flags=re.DOTALL)
        
        # Remove the get_risk_level function if it exists
        if "def get_risk_level" in content:
            pattern = r"def get_risk_level\(.*?\):(.*?)(?=\ndef |\Z)"
            content = re.sub(pattern, "", content, flags=re.DOTALL)
            
        # Remove the get_color_for_score function if it exists
        if "def get_color_for_score" in content:
            pattern = r"def get_color_for_score\(.*?\):(.*?)(?=\ndef |\Z)"
            content = re.sub(pattern, "", content, flags=re.DOTALL)
        
        # Add the import at the top of the file, after other imports
        if "from datetime import datetime" in content:
            content = content.replace("from datetime import datetime", 
                                    "from datetime import datetime" + import_replacement)
        else:
            # Add after the last import
            import_section_end = max([content.rfind(line) for line in [
                "import logging",
                "import json",
                "import os",
                "from flask"
            ]])
            
            if import_section_end > 0:
                content = content[:import_section_end + 20] + import_replacement + content[import_section_end + 20:]
    else:
        # Just add the import
        if "import logging" in content:
            import_line = """
# Import the scan data processor from the modular structure
from scanner.data_processor import process_scan_data, detect_os_and_browser, get_risk_level, get_color_for_score, enhance_report_view
"""
            content = content.replace("import logging", "import logging" + import_line)
    
    # Update the report_view function to use enhance_report_view if it exists
    if "def report_view" in content and "formatted_scan = process_scan_data" in content:
        # Replace process_scan_data with enhance_report_view
        content = content.replace(
            "formatted_scan = process_scan_data(scan)", 
            "# Use the enhanced report view processor for comprehensive scan display\n        formatted_scan = enhance_report_view(scan)"
        )
    
    with open('client.py', 'w') as f:
        f.write(content)
    
    print("✅ Updated client.py to use the modular scan data processor")
    return True

def update_client_db_py():
    """
    Update client_db.py to use the modular scan data processor for format_scan_results_for_client
    """
    if not os.path.exists('client_db.py'):
        print("❌ client_db.py does not exist")
        return False
    
    with open('client_db.py', 'r') as f:
        content = f.read()
    
    # Check if format_scan_results_for_client is defined in this file
    if "def format_scan_results_for_client" in content:
        # Add import for modular functions
        import_line = """
# Import enhanced scan processing from modular structure
from scanner.data_processor import process_scan_data, enhance_report_view
"""
        if "import logging" in content:
            content = content.replace("import logging", "import logging" + import_line)
        else:
            # Add at the top
            content = import_line + content
        
        # Update the format_scan_results_for_client function to use the modular version
        pattern = r"def format_scan_results_for_client\((.*?)\):(.*?)(?=\ndef |\Z)"
        
        # Extract the original function signature to maintain compatibility
        signature_match = re.search(pattern, content, re.DOTALL)
        if signature_match:
            params = signature_match.group(1)
            
            # Create a replacement function that calls the modular version
            replacement = f"""def format_scan_results_for_client({params}):
    """Format scan results for client-friendly display using the modular processor"""
    try:
        # Use the modular implementation, ignoring any connection parameters
        return process_scan_data(scan_data)
    except Exception as e:
        logging.error(f"Error formatting scan results: {{e}}")
        return scan_data
"""
            
            # Replace the function
            content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    with open('client_db.py', 'w') as f:
        f.write(content)
    
    print("✅ Updated client_db.py to use the modular scan data processor")
    return True

def update_init_py():
    """Update scanner/__init__.py to expose the data_processor functions"""
    with open('scanner/__init__.py', 'w') as f:
        f.write("""# Scanner package
# This file imports and exposes the scanner data processor

from .data_processor import process_scan_data, detect_os_and_browser
from .data_processor import get_risk_level, get_color_for_score
from .data_processor import enhance_report_view

# Tell users this is the new implementation
print("Using enhanced modular scanner data processing")
""")
    
    print("✅ Updated scanner/__init__.py")

def main():
    """Main function to integrate the scan data processor"""
    print("=== Integrating Enhanced Scan Data Processor ===\n")
    
    # Create backups
    backup_files()
    
    # Ensure directory structure
    ensure_directory_structure()
    
    # Update client.py
    update_client_py()
    
    # Update client_db.py
    update_client_db_py()
    
    # Update scanner/__init__.py
    update_init_py()
    
    print("\n=== Integration Complete ===")
    print("""
The enhanced scan data processor has been integrated into the codebase.
This ensures that scan reports will continue to display port scan results
and OS information correctly, even when the codebase is restructured.

To verify the integration:
1. Run the test script: ./test_scan_processor.py
2. If everything passes, the integration was successful
3. Test actual scan reports by running the application

If you encounter any issues, restore from the backups created during this process.
""")

if __name__ == "__main__":
    main()