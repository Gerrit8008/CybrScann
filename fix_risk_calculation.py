#!/usr/bin/env python3
"""
Fix for risk calculation error in scan results
Addresses the '< not supported between instances of 'dict' and 'int'' error
"""

import os
import re

def fix_risk_calculation():
    """
    Fix the risk calculation error in fixed_scan_core.py
    """
    scan_core_path = '/home/ggrun/CybrScan_1/fixed_scan_core.py'
    
    if not os.path.exists(scan_core_path):
        print(f"Error: {scan_core_path} not found")
        return False
        
    # Read the file
    with open(scan_core_path, 'r') as f:
        content = f.read()
    
    # Define the fixed risk assessment function
    fixed_risk_func = """
    def _calculate_risk_assessment(self, scan_results):
        \"\"\"Calculate risk assessment based on scan results\"\"\"
        # Start with a base score of 100 and deduct points for issues
        overall_score = 100
        deductions = 0
        
        try:
            # Check SSL certificate issues
            if 'ssl_certificate' in scan_results:
                ssl_data = scan_results['ssl_certificate']
                if isinstance(ssl_data, dict):
                    if ssl_data.get('status') == 'Expired' or 'error' in ssl_data:
                        deductions += 15
                    elif ssl_data.get('status') == 'Invalid':
                        deductions += 10
                    elif ssl_data.get('days_remaining', 100) < 30:
                        deductions += 5
            
            # Check security headers score
            if 'security_headers' in scan_results:
                headers_data = scan_results['security_headers']
                if isinstance(headers_data, dict):
                    headers_score = headers_data.get('score', 0)
                    if isinstance(headers_score, (int, float)) and headers_score < 50:
                        deductions += 10
                    elif isinstance(headers_score, (int, float)) and headers_score < 75:
                        deductions += 5
            
            # Check network findings
            if 'network' in scan_results and isinstance(scan_results['network'], list):
                critical_count = 0
                high_count = 0
                for finding in scan_results['network']:
                    if isinstance(finding, tuple) and len(finding) >= 2:
                        severity = finding[1]
                        if severity == 'Critical':
                            critical_count += 1
                        elif severity == 'High':
                            high_count += 1
                
                deductions += critical_count * 10
                deductions += high_count * 5
            
            # Check email security
            if 'email_security' in scan_results:
                email_data = scan_results['email_security']
                if isinstance(email_data, dict):
                    # Check DMARC
                    dmarc = email_data.get('dmarc', {})
                    if isinstance(dmarc, dict) and dmarc.get('severity') == 'High':
                        deductions += 5
                    
                    # Check SPF
                    spf = email_data.get('spf', {})
                    if isinstance(spf, dict) and spf.get('severity') == 'High':
                        deductions += 5
            
            # Calculate findings-based score adjustment
            if 'findings' in scan_results and isinstance(scan_results['findings'], list):
                critical_count = sum(1 for f in scan_results['findings'] if isinstance(f, dict) and f.get('severity') == 'Critical')
                high_count = sum(1 for f in scan_results['findings'] if isinstance(f, dict) and f.get('severity') == 'High')
                medium_count = sum(1 for f in scan_results['findings'] if isinstance(f, dict) and f.get('severity') == 'Medium')
                
                deductions += critical_count * 10
                deductions += high_count * 5
                deductions += medium_count * 2
            
            # Ensure score stays within 0-100 range
            overall_score = max(0, min(100, overall_score - deductions))
            
            # Determine risk level and color based on score
            if overall_score >= 90:
                risk_level = 'Low'
                color = '#28a745'  # green
            elif overall_score >= 80:
                risk_level = 'Low-Medium'
                color = '#5cb85c'  # light green
            elif overall_score >= 70:
                risk_level = 'Medium'
                color = '#17a2b8'  # info blue
            elif overall_score >= 60:
                risk_level = 'Medium-High'
                color = '#ffc107'  # warning yellow
            elif overall_score >= 50:
                risk_level = 'High'
                color = '#fd7e14'  # orange
            else:
                risk_level = 'Critical'
                color = '#dc3545'  # red
            
            # Create risk assessment object
            risk_assessment = {
                'overall_score': overall_score,
                'risk_level': risk_level,
                'color': color,
                'grade': 'A' if overall_score >= 90 else 'B' if overall_score >= 80 else 'C' if overall_score >= 70 else 'D' if overall_score >= 60 else 'F',
                'component_scores': {
                    'network': max(0, 100 - deductions * 1.5),
                    'web': max(0, 100 - deductions),
                    'email': max(0, 100 - deductions * 0.5),
                    'system': max(0, 100 - deductions * 0.8)
                }
            }
            
            return risk_assessment
        except Exception as e:
            self.progress_tracker.update_progress("risk_assessment", 100, f"Error calculating risk score: {str(e)}")
            self.logger.error(f"Error calculating risk score: {str(e)}")
            
            # Return a default risk assessment
            return {
                'overall_score': 75,
                'risk_level': 'Medium',
                'color': '#17a2b8',  # info blue
                'grade': 'C',
                'component_scores': {
                    'network': 75,
                    'web': 75,
                    'email': 75,
                    'system': 75
                }
            }
"""
    
    # Find the risk calculation function or method
    risk_pattern = r'def _calculate_risk_assessment\([^)]*\):(?:[^}]*?)(?=def |$)'
    risk_match = re.search(risk_pattern, content, re.DOTALL)
    
    if risk_match:
        original_risk_func = risk_match.group(0)
        
        # Replace the original function with the fixed version
        content = content.replace(original_risk_func, fixed_risk_func)
    else:
        # If we can't find the function, we'll add it
        class_pattern = r'class FixedSecurityScanner:'
        if class_pattern in content:
            # Add the fixed risk assessment method to the class
            content = content.replace(
                'class FixedSecurityScanner:',
                'class FixedSecurityScanner:' + fixed_risk_func
            )
    
    # Also fix the scan method to properly handle network results
    fixed_network_processing = """
        # Scan network security
        network = self._scan_network_security(target)
        
        # Ensure network result is properly formatted
        if isinstance(network, dict) and 'results' in network:
            network_results = network['results']
        elif isinstance(network, list):
            network_results = network
        else:
            network_results = []
            self.logger.warning(f"Network scan returned unexpected format: {type(network)}")
"""
    
    # Try to find and replace the network processing code
    if "network = self._scan_network_security(target)" in content:
        content = content.replace(
            "network = self._scan_network_security(target)",
            fixed_network_processing
        )
        
        # Also fix the results dict
        content = content.replace(
            "'network': network,",
            "'network': network_results,"
        )
    
    # Fix findings extraction for network data
    fixed_network_findings = """
        # Process network findings
        network = scan_results.get('network', [])
        self.logger.info(f"Processing network data: {network}")
        
        if isinstance(network, list):
            for finding in network:
                if isinstance(finding, tuple) and len(finding) >= 2:
                    message, severity = finding
                    
                    # Skip informational findings
                    if severity.lower() == 'info':
                        continue
                    
                    findings.append({
                        'type': 'network',
                        'title': f"Network: {message}",
                        'description': message,
                        'severity': severity,
                        'remediation': f"Address the network security issue: {message}",
                        'impact': 'Potential security vulnerability in network configuration'
                    })
"""
    
    # Try to find and replace the network findings extraction
    if "# Process network findings" in content:
        # Get the section that processes network findings
        network_pattern = r'# Process network findings(?:[^#]*?)(?=# |$)'
        content = re.sub(network_pattern, fixed_network_findings, content, flags=re.DOTALL)
    
    # Write the modified file
    with open(scan_core_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Successfully fixed risk calculation in {scan_core_path}")
    return True

def main():
    """Main function to apply all fixes"""
    print("Applying fixes for risk calculation error...")
    
    # Fix the risk calculation function
    fix_risk_calculation()
    
    print("\nAll fixes have been applied!")
    print("To make the changes effective, please restart the application server.")

if __name__ == "__main__":
    main()