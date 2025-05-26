#!/usr/bin/env python3
"""
Test the scan fixes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import run_consolidated_scan, get_industry_benchmarks

def test_scan_fixes():
    """Test the scan fixes"""
    print("🧪 Testing scan fixes...")
    
    # Test 1: Check industry benchmarks have message fields
    print("\n1. Testing industry benchmarks...")
    benchmarks = get_industry_benchmarks()
    
    for industry, data in benchmarks.items():
        if 'message' in data:
            print(f"   ✅ {industry}: has message field")
        else:
            print(f"   ❌ {industry}: missing message field")
    
    # Test 2: Test domain priority logic
    print("\n2. Testing domain priority logic...")
    
    test_lead_data = {
        'name': 'Test User',
        'email': 'test@example.com',
        'company': 'Test Company',
        'company_website': 'testcompany.com',
        'phone': '555-1234',
        'industry': 'technology',
        'company_size': '11-50',
        'target': 'testcompany.com',  # This should be the prioritized domain
        'timestamp': '2025-05-26 16:00:00',
        'client_os': 'Windows 10',
        'client_browser': 'Chrome'
    }
    
    print(f"   Company website: {test_lead_data['company_website']}")
    print(f"   Email domain: example.com")
    print(f"   Target set to: {test_lead_data['target']}")
    
    try:
        scan_results = run_consolidated_scan(test_lead_data)
        if scan_results and 'target' in scan_results:
            print(f"   ✅ Scan completed with target: {scan_results['target']}")
            
            # Check if industry data is present
            if 'industry' in scan_results and 'benchmarks' in scan_results['industry']:
                if 'message' in scan_results['industry']['benchmarks']:
                    print(f"   ✅ Industry benchmarks message: {scan_results['industry']['benchmarks']['message'][:50]}...")
                else:
                    print(f"   ❌ Industry benchmarks missing message")
            
            # Check if system data is present
            if 'system' in scan_results and 'os_updates' in scan_results['system']:
                if 'message' in scan_results['system']['os_updates']:
                    print(f"   ✅ OS updates message: {scan_results['system']['os_updates']['message'][:50]}...")
                else:
                    print(f"   ❌ OS updates missing message")
            
            print(f"   ✅ Scan completed successfully")
        else:
            print(f"   ❌ Scan failed or returned invalid results")
    except Exception as e:
        print(f"   ❌ Scan error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_scan_fixes()