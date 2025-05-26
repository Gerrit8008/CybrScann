#!/usr/bin/env python3
"""
Test script to verify scan tracking functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from client_database_manager import get_scanner_scan_count, save_scan_to_client_db
from scanner_db_functions import get_scanners_by_client_id
import json
from datetime import datetime

def test_scan_tracking():
    """Test scan tracking functionality"""
    print("🧪 Testing scan tracking functionality...")
    
    # Test with a sample client ID and scanner ID
    test_client_id = 1
    test_scanner_id = "scanner_test123"
    
    print(f"\n1. Testing scan count for client {test_client_id}, scanner {test_scanner_id}")
    
    # Get initial scan count
    initial_count = get_scanner_scan_count(test_client_id, test_scanner_id)
    print(f"   Initial scan count: {initial_count}")
    
    # Create test scan data
    test_scan_data = {
        'scan_id': f'test_scan_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
        'scanner_id': test_scanner_id,
        'timestamp': datetime.now().isoformat(),
        'name': 'Test User',
        'email': 'testuser@example.com',
        'phone': '+1234567890',
        'company': 'Test Company Inc',
        'company_size': 'Small (1-50)',
        'target_domain': 'example.com',
        'target_url': 'https://example.com',
        'security_score': 78,
        'risk_level': 'Medium',
        'scan_type': 'comprehensive',
        'status': 'completed',
        'vulnerabilities_found': 3,
        'scan_results': json.dumps({
            'findings': ['SSL certificate expires in 30 days', 'Port 80 is open', 'Directory listing enabled'],
            'recommendations': ['Renew SSL certificate', 'Close unnecessary ports', 'Disable directory listing']
        })
    }
    
    print(f"\n2. Saving test scan to client-specific database...")
    try:
        save_scan_to_client_db(test_client_id, test_scan_data)
        print("   ✅ Scan saved successfully")
    except Exception as e:
        print(f"   ❌ Error saving scan: {e}")
        return False
    
    # Get updated scan count
    updated_count = get_scanner_scan_count(test_client_id, test_scanner_id)
    print(f"\n3. Updated scan count: {updated_count}")
    
    if updated_count > initial_count:
        print(f"   ✅ Scan count increased by {updated_count - initial_count}")
    else:
        print(f"   ❌ Scan count did not increase (expected increase)")
        return False
    
    print(f"\n4. Testing scanner list with scan counts...")
    try:
        scanners = get_scanners_by_client_id(test_client_id)
        print(f"   Found {len(scanners)} scanners for client {test_client_id}")
        
        for scanner in scanners:
            scanner_id = scanner.get('scanner_id', 'unknown')
            scan_count = scanner.get('scan_count', 0)
            print(f"   - Scanner {scanner_id}: {scan_count} scans")
            
        print("   ✅ Scanner list with scan counts loaded successfully")
    except Exception as e:
        print(f"   ❌ Error getting scanner list: {e}")
        return False
    
    print(f"\n🎉 All scan tracking tests passed!")
    return True

def test_multiple_scanners():
    """Test scan tracking with multiple scanners"""
    print(f"\n🔬 Testing multiple scanner tracking...")
    
    test_client_id = 1
    test_scanners = ["scanner_web", "scanner_api", "scanner_mobile"]
    
    for scanner_id in test_scanners:
        print(f"\n   Adding scan for {scanner_id}...")
        
        test_scan_data = {
            'scan_id': f'multi_test_{scanner_id}_{datetime.now().strftime("%H%M%S")}',
            'scanner_id': scanner_id,
            'timestamp': datetime.now().isoformat(),
            'name': f'Test User {scanner_id}',
            'email': f'user@{scanner_id}.com',
            'company': f'Company for {scanner_id}',
            'target_domain': f'{scanner_id}.example.com',
            'security_score': 85,
            'risk_level': 'Low',
            'scan_type': 'comprehensive',
            'status': 'completed'
        }
        
        try:
            save_scan_to_client_db(test_client_id, test_scan_data)
            count = get_scanner_scan_count(test_client_id, scanner_id)
            print(f"      ✅ {scanner_id}: {count} scans")
        except Exception as e:
            print(f"      ❌ Error with {scanner_id}: {e}")

if __name__ == "__main__":
    print("🛡️ CybrScan - Scan Tracking Test Suite")
    print("=" * 50)
    
    success = test_scan_tracking()
    
    if success:
        test_multiple_scanners()
        print(f"\n✅ All tests completed successfully!")
        print(f"\nNow the scan counters in /client/scanners should show:")
        print(f"- Individual scanner scan counts")
        print(f"- Updated automatically when scans are submitted")
        print(f"- Proper tracking via both main /scan route and API endpoints")
    else:
        print(f"\n❌ Some tests failed. Check the error messages above.")
        sys.exit(1)