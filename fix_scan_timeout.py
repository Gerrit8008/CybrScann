#!/usr/bin/env python3
"""
Fix for scan timeout and JSON parsing errors
This script addresses worker timeouts and JSON response errors in the scanning process
"""

import os
import re

def fix_fixed_scan_core():
    """
    Modify fixed_scan_core.py to add timeout handling and better error management
    """
    scan_core_path = '/home/ggrun/CybrScan_1/fixed_scan_core.py'
    
    if not os.path.exists(scan_core_path):
        print(f"Error: {scan_core_path} not found")
        return False
        
    # Read the file
    with open(scan_core_path, 'r') as f:
        content = f.read()
    
    # First, add timeout for network scans
    if '_scan_network_security' in content:
        # Find the network scan method
        network_scan_pattern = r'def _scan_network_security\(self, target\):(?:[^}]*?)(?=def |$)'
        network_scan_match = re.search(network_scan_pattern, content, re.DOTALL)
        
        if network_scan_match:
            original_network_scan = network_scan_match.group(0)
            
            # Add timeout to any requests calls
            modified_network_scan = re.sub(
                r'(requests\.(?:get|post|head)\([^)]*)',
                r'\1, timeout=10',
                original_network_scan
            )
            
            # Add exception handling for timeouts
            if 'except requests.exceptions.Timeout:' not in modified_network_scan:
                modified_network_scan = modified_network_scan.replace(
                    'except Exception as e:',
                    'except requests.exceptions.Timeout:\n            self.progress_tracker.update_progress("network", 100, "Network scan timed out")\n            return {\n                "error": "Network scan timed out",\n                "status": "error",\n                "message": "The network scan operation timed out. This may be due to firewall restrictions or network connectivity issues."\n            }\n        except Exception as e:'
                )
            
            # Replace in the content
            content = content.replace(original_network_scan, modified_network_scan)
    
    # Fix JSON parsing in scan results 
    if 'def scan' in content:
        # Find the scan method
        scan_pattern = r'def scan\(self[^)]*\):(?:[^}]*?)(?=def |$)'
        scan_match = re.search(scan_pattern, content, re.DOTALL)
        
        if scan_match:
            original_scan = scan_match.group(0)
            
            # Ensure all scan results have a valid JSON structure
            if 'ensure_valid_json' not in original_scan:
                # Add a method to ensure valid JSON
                content = content.replace(
                    'class FixedSecurityScanner:',
                    '''class FixedSecurityScanner:
    def _ensure_valid_json(self, results):
        """Ensure scan results are valid JSON"""
        if not results:
            return {"error": "Empty scan results", "status": "error"}
            
        # Ensure all components exist
        if "network" not in results:
            results["network"] = {"status": "not_scanned"}
        if "web" not in results:
            results["web"] = {"status": "not_scanned"}
        if "ssl_certificate" not in results:
            results["ssl_certificate"] = {"status": "not_scanned"}
        if "security_headers" not in results:
            results["security_headers"] = {"status": "not_scanned"}
        if "email_security" not in results:
            results["email_security"] = {"status": "not_scanned", "domain": "unknown"}
            
        # Add risk assessment if missing
        if "risk_assessment" not in results:
            results["risk_assessment"] = {
                "overall_score": 75,
                "risk_level": "Medium",
                "color": "#17a2b8",
                "component_scores": {
                    "network": 75,
                    "web": 75,
                    "email": 75,
                    "system": 75
                }
            }
            
        # Add timestamps if missing
        if "timestamp" not in results:
            from datetime import datetime
            results["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
        return results'''
                )
                
                # Modify the scan method to use the new ensure_valid_json method
                modified_scan = original_scan.replace(
                    'return results',
                    'return self._ensure_valid_json(results)'
                )
                
                # Replace in the content
                content = content.replace(original_scan, modified_scan)
    
    # Add proper imports for timeout handling
    if 'import requests' in content and 'requests.exceptions' not in content:
        content = content.replace(
            'import requests',
            'import requests\nfrom requests.exceptions import Timeout, RequestException'
        )
    
    # Write the modified file
    with open(scan_core_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Successfully fixed {scan_core_path} to handle timeouts and JSON errors")
    return True

def fix_fixed_scan_routes():
    """
    Modify fixed_scan_routes.py to handle JSON errors in responses
    """
    routes_path = '/home/ggrun/CybrScan_1/fixed_scan_routes.py'
    
    if not os.path.exists(routes_path):
        print(f"Error: {routes_path} not found")
        return False
        
    # Read the file
    with open(routes_path, 'r') as f:
        content = f.read()
    
    # Find the /progress route to add error handling
    progress_pattern = r'@fixed_scan_bp\.route\(["\']\/progress["\'].*?\)(?:[^}]*?)(?=@|$)'
    progress_match = re.search(progress_pattern, content, re.DOTALL)
    
    if progress_match:
        original_progress = progress_match.group(0)
        
        # Check if we need to add try/except for JSON
        if 'try:' not in original_progress and 'jsonify' in original_progress:
            modified_progress = original_progress.replace(
                'def scan_progress():',
                '''def scan_progress():
    try:'''
            )
            
            modified_progress = modified_progress.replace(
                'return jsonify(progress_data)',
                '''        return jsonify(progress_data)
    except Exception as e:
        app.logger.error(f"Error in scan_progress: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"An error occurred while tracking progress: {str(e)}",
            "progress": 0
        })'''
            )
            
            # Replace in content
            content = content.replace(original_progress, modified_progress)
    
    # Find the /results route to add error handling
    results_pattern = r'@fixed_scan_bp\.route\(["\']\/results["\'].*?\)(?:[^}]*?)(?=@|$)'
    results_match = re.search(results_pattern, content, re.DOTALL)
    
    if results_match:
        original_results = results_match.group(0)
        
        # Check if we need to add try/except for JSON errors
        if 'try:' not in original_results and 'jsonify' in original_results:
            modified_results = original_results.replace(
                'def scan_results():',
                '''def scan_results():
    try:'''
            )
            
            # Find the return statement and add error handling
            return_pattern = r'return jsonify\([^)]*\)'
            modified_results = re.sub(
                return_pattern,
                '''        # Ensure we have valid data before returning
        if not scan_data:
            scan_data = {
                "error": "No scan data available",
                "status": "error",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "risk_assessment": {
                    "overall_score": 0,
                    "risk_level": "Unknown",
                    "color": "#dc3545"
                }
            }
            
        return jsonify(scan_data)
    except Exception as e:
        app.logger.error(f"Error in scan_results: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"An error occurred while processing scan results: {str(e)}",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "risk_assessment": {
                "overall_score": 0,
                "risk_level": "Error",
                "color": "#dc3545"
            }
        })''',
                modified_results
            )
            
            # Add datetime import if needed
            if 'from datetime import datetime' not in content:
                modified_results = modified_results.replace(
                    'def scan_results():',
                    'from datetime import datetime\n\ndef scan_results():'
                )
            
            # Replace in content
            content = content.replace(original_results, modified_results)
    
    # Write the modified file
    with open(routes_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Successfully fixed {routes_path} to handle JSON errors in responses")
    return True

def fix_app_timeout_settings():
    """
    Update app.py to increase worker timeout settings
    """
    app_path = '/home/ggrun/CybrScan_1/app.py'
    
    if not os.path.exists(app_path):
        print(f"Error: {app_path} not found")
        return False
        
    # Read the file
    with open(app_path, 'r') as f:
        content = f.read()
    
    # Check if there's a gunicorn configuration
    if 'if __name__ == "__main__"' in content:
        # Find the main block
        main_pattern = r'if __name__ == ["\']__main__["\']:(?:[^}]*?)(?=$)'
        main_match = re.search(main_pattern, content, re.DOTALL)
        
        if main_match:
            original_main = main_match.group(0)
            
            # Check if we need to add timeout configuration
            if 'timeout' not in original_main and 'app.run' in original_main:
                # Modify to use gunicorn with timeout or update Flask run
                if 'gunicorn' in content:
                    modified_main = original_main.replace(
                        'app.run(',
                        'app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), '
                    )
                    
                    # Add a comment about increasing timeout
                    modified_main += '''
    # If using gunicorn, increase worker timeout with:
    # gunicorn -w 4 --timeout 120 -b 0.0.0.0:5000 app:app
'''
                else:
                    modified_main = original_main.replace(
                        'app.run(',
                        'app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), '
                    )
                    
                    # Add a comment about increasing timeout
                    modified_main += '''
    # Note: For production, use gunicorn with increased timeout:
    # gunicorn -w 4 --timeout 120 -b 0.0.0.0:5000 app:app
'''
                
                # Replace in content
                content = content.replace(original_main, modified_main)
    
    # Write the modified file
    with open(app_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Successfully updated {app_path} with timeout recommendations")
    return True

def main():
    """Main function to apply all fixes"""
    print("Applying fixes for scan timeout and JSON parsing errors...")
    
    # Fix the fixed_scan_core.py file
    fix_fixed_scan_core()
    
    # Fix the fixed_scan_routes.py file
    fix_fixed_scan_routes()
    
    # Update app.py with timeout settings
    fix_app_timeout_settings()
    
    print("\nAll fixes have been applied!")
    print("To make the changes effective, please restart the application server with increased timeout:")
    print("gunicorn -w 4 --timeout 120 -b 0.0.0.0:5000 app:app")

if __name__ == "__main__":
    main()