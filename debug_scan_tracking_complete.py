#!/usr/bin/env python3

import os
import sys
import uuid
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_complete_scan_flow():
    """Test the complete scan flow from submission to dashboard display"""
    print("🔍 COMPREHENSIVE SCAN TRACKING DEBUG")
    print("=" * 60)
    
    # Step 1: Check current state
    print("\n📊 STEP 1: Current Dashboard State")
    try:
        from client_db import get_client_dashboard_data
        dashboard_data = get_client_dashboard_data(2)  # Acme Security Corp
        
        if dashboard_data:
            print(f"✅ Dashboard data retrieved")
            print(f"   Stats: {dashboard_data['stats']}")
            print(f"   Scan history count: {len(dashboard_data.get('scan_history', []))}")
            
            if dashboard_data.get('scan_history'):
                print("   Recent scans:")
                for i, scan in enumerate(dashboard_data['scan_history'][:3], 1):
                    print(f"     {i}. ID: {scan.get('scan_id', 'N/A')[:8]}...")
                    print(f"        Lead: {scan.get('lead_name', 'NO LEAD NAME')}")
                    print(f"        Email: {scan.get('lead_email', 'NO EMAIL')}")
                    print(f"        Target: {scan.get('target', 'NO TARGET')}")
                    print(f"        Score: {scan.get('security_score', 'NO SCORE')}")
                    print(f"        All fields: {list(scan.keys())}")
            else:
                print("   ❌ No scan history found in dashboard")
        else:
            print("❌ Dashboard data is None")
    except Exception as e:
        print(f"❌ Error getting dashboard data: {e}")
        import traceback
        traceback.print_exc()
    
    # Step 2: Check client-specific database directly
    print("\n💾 STEP 2: Client-Specific Database Check")
    try:
        from client_database_manager import get_client_scan_reports, get_client_scan_statistics
        
        reports, pagination = get_client_scan_reports(2, page=1, per_page=5)
        stats = get_client_scan_statistics(2)
        
        print(f"✅ Direct database query results:")
        print(f"   Reports count: {len(reports)}")
        print(f"   Pagination: {pagination}")
        print(f"   Statistics: {stats}")
        
        if reports:
            print("   Sample reports:")
            for i, report in enumerate(reports[:2], 1):
                print(f"     {i}. ID: {report.get('scan_id', 'N/A')[:8]}...")
                print(f"        Lead Name: {report.get('lead_name', 'MISSING')}")
                print(f"        Lead Email: {report.get('lead_email', 'MISSING')}")
                print(f"        Company: {report.get('lead_company', 'MISSING')}")
                print(f"        Target: {report.get('target_domain', 'MISSING')}")
                print(f"        Score: {report.get('security_score', 'MISSING')}")
                print(f"        All fields: {list(report.keys())}")
        else:
            print("   ❌ No reports found in client database")
            
    except Exception as e:
        print(f"❌ Error checking client database: {e}")
        import traceback
        traceback.print_exc()
    
    # Step 3: Test new scan submission
    print("\n🆕 STEP 3: Testing New Scan Submission")
    try:
        # Simulate a new scan
        lead_data = {
            'name': 'Debug Test Lead',
            'email': 'debug@testcompany.com',
            'company': 'Debug Test Company',
            'phone': '555-DEBUG',
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'client_os': 'Windows',
            'client_browser': 'Chrome',
            'target': 'testcompany.com'
        }
        
        scan_results = {
            'scan_id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat(),
            'target': lead_data['target'],
            'email': lead_data['email'],
            'client_id': 2,
            'scanner_id': 'scanner_919391f3',
            'risk_assessment': {
                'overall_score': 85
            }
        }
        scan_results.update(lead_data)
        
        print(f"📝 Submitting test scan:")
        print(f"   Scan ID: {scan_results['scan_id']}")
        print(f"   Client ID: {scan_results['client_id']}")
        print(f"   Lead Name: {scan_results['name']}")
        print(f"   Lead Email: {scan_results['email']}")
        
        # Save to client-specific database
        from client_database_manager import save_scan_to_client_db
        save_result = save_scan_to_client_db(2, scan_results)
        print(f"✅ Save result: {save_result}")
        
        # Check immediate retrieval
        reports_after, _ = get_client_scan_reports(2, page=1, per_page=1)
        if reports_after:
            latest = reports_after[0]
            print(f"✅ Latest scan after save:")
            print(f"   ID: {latest.get('scan_id', 'N/A')}")
            print(f"   Lead Name: {latest.get('lead_name', 'MISSING')}")
            print(f"   Lead Email: {latest.get('lead_email', 'MISSING')}")
        else:
            print(f"❌ No scans found after save")
            
    except Exception as e:
        print(f"❌ Error testing scan submission: {e}")
        import traceback
        traceback.print_exc()
    
    # Step 4: Check dashboard after new scan
    print("\n📊 STEP 4: Dashboard After New Scan")
    try:
        dashboard_data_after = get_client_dashboard_data(2)
        
        if dashboard_data_after:
            print(f"✅ Updated dashboard data:")
            print(f"   Stats: {dashboard_data_after['stats']}")
            print(f"   Scan history count: {len(dashboard_data_after.get('scan_history', []))}")
            
            if dashboard_data_after.get('scan_history'):
                latest_scan = dashboard_data_after['scan_history'][0]
                print(f"   Latest scan in dashboard:")
                print(f"     ID: {latest_scan.get('scan_id', 'N/A')[:8]}...")
                print(f"     Lead: {latest_scan.get('lead_name', 'NO LEAD NAME')}")
                print(f"     Email: {latest_scan.get('lead_email', 'NO EMAIL')}")
                print(f"     Has lead data: {bool(latest_scan.get('lead_name'))}")
        else:
            print("❌ Dashboard data still None")
            
    except Exception as e:
        print(f"❌ Error checking updated dashboard: {e}")
    
    # Step 5: Check data conversion process
    print("\n🔄 STEP 5: Data Conversion Debug")
    try:
        # Test the conversion process manually
        from client_database_manager import get_client_scan_reports
        raw_scans, _ = get_client_scan_reports(2, page=1, per_page=3)
        
        print(f"Raw scans from database: {len(raw_scans)}")
        
        if raw_scans:
            print("Converting to dashboard format...")
            converted_scans = []
            for scan in raw_scans:
                converted_scan = {
                    'scan_id': scan.get('scan_id', ''),
                    'timestamp': scan.get('timestamp', scan.get('created_at', '')),
                    'scanner_name': scan.get('scanner_name', 'Web Interface'),
                    'target': scan.get('target_domain', scan.get('target_url', '')),
                    'status': scan.get('status', 'completed'),
                    'security_score': scan.get('security_score', 0),
                    'issues_found': scan.get('vulnerabilities_found', scan.get('issues_count', 0)),
                    # CRITICAL: Include lead information for client tracking
                    'lead_name': scan.get('lead_name', ''),
                    'lead_email': scan.get('lead_email', ''),
                    'lead_phone': scan.get('lead_phone', ''),
                    'lead_company': scan.get('lead_company', ''),
                    'company_size': scan.get('company_size', ''),
                    'risk_level': scan.get('risk_level', '')
                }
                converted_scans.append(converted_scan)
                
                print(f"   Converted scan:")
                print(f"     Original lead_name: {scan.get('lead_name', 'MISSING')}")
                print(f"     Converted lead_name: {converted_scan['lead_name']}")
                print(f"     Has lead data: {bool(converted_scan['lead_name'])}")
                break  # Just show first one
                
    except Exception as e:
        print(f"❌ Error in conversion debug: {e}")

if __name__ == "__main__":
    test_complete_scan_flow()