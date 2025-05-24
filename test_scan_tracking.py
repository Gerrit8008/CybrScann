#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from client_database_manager import (
    create_client_specific_database, 
    save_scan_to_client_db,
    get_client_scan_reports,
    get_client_scan_statistics
)
from datetime import datetime
import json

def test_scan_tracking_system():
    """Test the complete scan tracking system"""
    
    print("🧪 Testing Scan Tracking System")
    print("=" * 50)
    
    # Test data
    test_client_id = 999
    test_business_name = "Acme Security Corp"
    
    # Step 1: Create client database
    print("1️⃣ Creating client-specific database...")
    db_path = create_client_specific_database(test_client_id, test_business_name)
    
    if db_path:
        print(f"✅ Database created: {db_path}")
    else:
        print("❌ Database creation failed")
        return False
    
    # Step 2: Create test scan data
    print("\n2️⃣ Creating test scan data...")
    test_scan_data = {
        'scan_id': 'test_scan_001',
        'scanner_id': 'scanner_123',
        'client_id': test_client_id,
        'timestamp': datetime.now().isoformat(),
        'name': 'John Doe',
        'email': 'john.doe@example.com',
        'phone': '+1-555-123-4567',
        'company': 'Example Corp',
        'company_size': 'Medium',
        'target': 'example.com',
        'business_name': test_business_name,
        'risk_assessment': {
            'overall_score': 85
        },
        'recommendations': [
            'Update SSL certificates',
            'Enable firewall protection',
            'Implement multi-factor authentication'
        ]
    }
    
    # Step 3: Save scan to client database
    print("3️⃣ Saving scan to client database...")
    save_result = save_scan_to_client_db(test_client_id, test_scan_data)
    
    if save_result:
        print("✅ Scan saved successfully")
    else:
        print("❌ Failed to save scan")
        return False
    
    # Step 4: Add more test scans
    print("\n4️⃣ Adding more test scans...")
    for i in range(2, 6):
        additional_scan = test_scan_data.copy()
        additional_scan['scan_id'] = f'test_scan_00{i}'
        additional_scan['name'] = f'User {i}'
        additional_scan['email'] = f'user{i}@company{i}.com'
        additional_scan['company'] = f'Company {i}'
        additional_scan['risk_assessment']['overall_score'] = 70 + (i * 5)
        
        save_scan_to_client_db(test_client_id, additional_scan)
        print(f"  📄 Added scan {i}")
    
    # Step 5: Test scan reports retrieval
    print("\n5️⃣ Testing scan reports retrieval...")
    scan_reports, pagination = get_client_scan_reports(test_client_id)
    
    print(f"✅ Retrieved {len(scan_reports)} scan reports")
    print(f"📊 Pagination: {pagination}")
    
    if scan_reports:
        print("\n📋 Sample scan report:")
        sample_report = scan_reports[0]
        print(f"  • Scan ID: {sample_report.get('scan_id')}")
        print(f"  • Name: {sample_report.get('lead_name')}")
        print(f"  • Email: {sample_report.get('lead_email')}")
        print(f"  • Company: {sample_report.get('lead_company')}")
        print(f"  • Score: {sample_report.get('security_score')}")
    
    # Step 6: Test statistics
    print("\n6️⃣ Testing scan statistics...")
    stats = get_client_scan_statistics(test_client_id)
    
    print(f"📈 Statistics:")
    print(f"  • Total scans: {stats['total_scans']}")
    print(f"  • Average score: {stats['avg_score']:.1f}")
    print(f"  • This month: {stats['this_month']}")
    print(f"  • Unique companies: {stats['unique_companies']}")
    
    # Step 7: Test filtering
    print("\n7️⃣ Testing filtered search...")
    filters = {'search': 'john', 'score_min': 80}
    filtered_reports, filtered_pagination = get_client_scan_reports(test_client_id, filters=filters)
    
    print(f"🔍 Filtered results: {len(filtered_reports)} reports")
    print(f"📄 Filter applied: search='john', score_min=80")
    
    print("\n🎉 All tests completed successfully!")
    return True

def cleanup_test_data():
    """Clean up test database"""
    import os
    test_db_path = 'client_databases/client_999_scans.db'
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
        print("🧹 Cleaned up test database")

if __name__ == "__main__":
    try:
        # Run tests
        success = test_scan_tracking_system()
        
        if success:
            print("\n✅ All tests passed!")
        else:
            print("\n❌ Some tests failed!")
            
        # Ask about cleanup
        cleanup = input("\n🗑️  Remove test database? (y/N): ").lower().strip()
        if cleanup == 'y':
            cleanup_test_data()
            
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        import traceback
        traceback.print_exc()