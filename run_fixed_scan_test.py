#!/usr/bin/env python3
"""
Test script to run the fixed security scanner directly
This allows testing the scan functionality without the web interface
"""

import os
import sys
import json
import time
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_scan_test(target_domain="example.com"):
    """Run a test scan against the specified domain"""
    try:
        # Import the fixed scan core
        from fixed_scan_core import run_fixed_scan
        
        # Progress callback for real-time updates
        def progress_callback(data):
            logger.info(f"Progress: {data['progress']}% - {data['task']}")
        
        # Test client info
        client_info = {
            'name': 'Test User',
            'email': 'test@example.com',
            'company': 'Test Company',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Run the scan
        logger.info(f"Starting test scan against {target_domain}")
        start_time = time.time()
        
        scan_results = run_fixed_scan(
            target_domain=target_domain,
            client_info=client_info,
            progress_callback=progress_callback
        )
        
        # Calculate scan duration
        duration = time.time() - start_time
        logger.info(f"Scan completed in {duration:.2f} seconds")
        
        # Save results to file for analysis
        output_dir = "scan_results"
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(output_dir, f"scan_{target_domain.replace('.', '_')}_{timestamp}.json")
        
        with open(output_file, 'w') as f:
            json.dump(scan_results, f, indent=2)
        
        logger.info(f"Scan results saved to {output_file}")
        
        # Print summary
        print("\n" + "="*50)
        print(f"SCAN SUMMARY FOR {target_domain}")
        print("="*50)
        
        # Print risk assessment
        if 'risk_assessment' in scan_results:
            risk = scan_results['risk_assessment']
            print(f"\nRisk Assessment:")
            print(f"  Overall Score: {risk.get('overall_score', 'N/A')}/100")
            print(f"  Risk Level: {risk.get('risk_level', 'N/A')}")
            print(f"  Grade: {risk.get('grade', 'N/A')}")
        
        # Print network findings
        if 'network' in scan_results and 'open_ports' in scan_results['network']:
            ports = scan_results['network']['open_ports']
            print(f"\nNetwork Security:")
            print(f"  Open Ports: {ports.get('count', 0)}")
            if ports.get('list'):
                print(f"  Ports Found: {', '.join(map(str, ports.get('list', [])))}")
        
        # Print web security
        if 'security_headers' in scan_results:
            headers = scan_results['security_headers']
            print(f"\nWeb Security:")
            print(f"  Security Headers Score: {headers.get('score', 'N/A')}/100")
            print(f"  Severity: {headers.get('severity', 'N/A')}")
        
        # Print SSL certificate
        if 'ssl_certificate' in scan_results and 'error' not in scan_results['ssl_certificate']:
            cert = scan_results['ssl_certificate']
            print(f"\nSSL Certificate:")
            print(f"  Status: {cert.get('status', 'N/A')}")
            print(f"  Issuer: {cert.get('issuer', 'N/A')}")
            print(f"  Expires in: {cert.get('days_remaining', 'N/A')} days")
        
        # Print email security
        if 'email_security' in scan_results:
            email = scan_results['email_security']
            print(f"\nEmail Security:")
            for protocol in ['spf', 'dkim', 'dmarc']:
                if protocol in email:
                    print(f"  {protocol.upper()}: {email[protocol].get('status', 'N/A')}")
        
        # Print recommendations
        if 'recommendations' in scan_results and scan_results['recommendations']:
            print(f"\nTop Recommendations:")
            for i, rec in enumerate(scan_results['recommendations'][:3], 1):
                print(f"  {i}. {rec}")
        
        print("\nFor full results, see the JSON file at:")
        print(output_file)
        print("="*50)
        
        return scan_results
        
    except Exception as e:
        logger.error(f"Error running test scan: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main function to run the test scan"""
    # Get target domain from command line if provided
    target_domain = sys.argv[1] if len(sys.argv) > 1 else "example.com"
    
    # Run the scan
    scan_results = run_scan_test(target_domain)
    
    if scan_results:
        logger.info("Test scan completed successfully")
        return 0
    else:
        logger.error("Test scan failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())