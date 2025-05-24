#!/usr/bin/env python3
"""Test what data is actually being passed to dashboard template"""

import sys
import os
sys.path.append('/home/ggrun/CybrScan_1')

from client_db import get_client_dashboard_data

def test_dashboard_data():
    print("🔍 TESTING DASHBOARD DATA FLOW")
    print("=" * 50)
    
    # Test client 2 (as shown in debug output)
    client_id = 2
    
    print(f"📊 Getting dashboard data for client {client_id}...")
    data = get_client_dashboard_data(client_id)
    
    if data:
        print(f"✅ Dashboard data retrieved successfully")
        print(f"   - Stats: {data['stats']}")
        print(f"   - Scan history count: {len(data['scan_history'])}")
        
        if data['scan_history']:
            print("\n📋 Scan History Details:")
            for i, scan in enumerate(data['scan_history'][:3]):
                print(f"   {i+1}. Scan ID: {scan.get('scan_id', 'N/A')[:8]}...")
                print(f"      Lead Name: '{scan.get('lead_name', 'N/A')}'")
                print(f"      Lead Email: '{scan.get('lead_email', 'N/A')}'")
                print(f"      Company: '{scan.get('lead_company', 'N/A')}'")
                print(f"      Target: '{scan.get('target', 'N/A')}'")
                print(f"      Security Score: {scan.get('security_score', 'N/A')}")
                print(f"      Timestamp: '{scan.get('timestamp', 'N/A')}'")
                print()
        else:
            print("❌ No scan history found!")
    else:
        print("❌ No dashboard data returned!")
    
    # Test template variables 
    print("\n🎯 TEMPLATE VARIABLE TEST")
    print("=" * 30)
    
    # Simulate what gets passed to template
    if data and data['scan_history']:
        scan_history = data['scan_history']
        print(f"scan_history variable: {len(scan_history)} items")
        print(f"scan_history[:5]: {len(scan_history[:5])} items for template")
        
        # Test the template logic
        first_scan = scan_history[0] if scan_history else None
        if first_scan:
            print("\n📝 First scan template fields:")
            print(f"   scan.get('timestamp', '')[:10]: '{first_scan.get('timestamp', '')[:10]}'")
            print(f"   scan.get('lead_name', 'Anonymous'): '{first_scan.get('lead_name', 'Anonymous')}'")
            print(f"   scan.get('lead_email'): '{first_scan.get('lead_email')}'")
            print(f"   scan.get('lead_company', 'Unknown'): '{first_scan.get('lead_company', 'Unknown')}'")
            print(f"   scan.get('target', ''): '{first_scan.get('target', '')}'")
            print(f"   scan.get('security_score', 0): {first_scan.get('security_score', 0)}")

if __name__ == "__main__":
    test_dashboard_data()