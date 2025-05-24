#!/usr/bin/env python3
"""Test scan tracking functionality"""

import sys
import os
import sqlite3
import uuid
from datetime import datetime

sys.path.append('/home/ggrun/CybrScan_1')

def test_scan_tracking():
    """Test the scan tracking pipeline"""
    print("🧪 TESTING SCAN TRACKING PIPELINE")
    print("=" * 40)
    
    try:
        # Create test data
        scan_id = str(uuid.uuid4())
        test_lead_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'phone': '+1234567890',
            'company': 'Test Company',
            'company_size': 'Medium',
            'target': 'example.com'
        }
        
        test_scan_results = {
            'scan_id': scan_id,
            'target_domain': 'example.com',
            'security_score': 85,
            'vulnerabilities_found': 2,
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"📝 Test scan ID: {scan_id[:8]}...")
        
        # Test 1: Save to main database
        print("\n1️⃣ Testing main database save...")
        main_db_path = '/home/ggrun/CybrScan_1/cybrscan.db'
        
        if os.path.exists(main_db_path):
            conn = sqlite3.connect(main_db_path)
            cursor = conn.cursor()
            
            # Check if scan_results table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='scan_results'")
            if cursor.fetchone():
                print("   ✅ scan_results table exists")
                
                # Insert test scan
                cursor.execute("""
                    INSERT OR REPLACE INTO scan_results 
                    (scan_id, target_domain, security_score, vulnerabilities_found, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    test_scan_results['scan_id'],
                    test_scan_results['target_domain'],
                    test_scan_results['security_score'],
                    test_scan_results['vulnerabilities_found'],
                    test_scan_results['timestamp']
                ))
                conn.commit()
                print(f"   ✅ Saved test scan to main database")
            else:
                print("   ❌ scan_results table doesn't exist")
            
            conn.close()
        
        # Test 2: Save to leads database
        print("\n2️⃣ Testing leads database save...")
        leads_db_path = '/home/ggrun/CybrScan_1/leads.db'
        
        if os.path.exists(leads_db_path):
            conn = sqlite3.connect(leads_db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO leads 
                (name, email, phone, company, company_size, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                test_lead_data['name'],
                test_lead_data['email'],
                test_lead_data['phone'],
                test_lead_data['company'],
                test_lead_data['company_size'],
                datetime.now().isoformat()
            ))
            conn.commit()
            print(f"   ✅ Saved test lead to leads database")
            conn.close()
        else:
            # Create leads database
            conn = sqlite3.connect(leads_db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS leads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT,
                    phone TEXT,
                    company TEXT,
                    company_size TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            """)
            
            cursor.execute("""
                INSERT INTO leads 
                (name, email, phone, company, company_size, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                test_lead_data['name'],
                test_lead_data['email'],
                test_lead_data['phone'],
                test_lead_data['company'],
                test_lead_data['company_size'],
                datetime.now().isoformat()
            ))
            conn.commit()
            print(f"   ✅ Created leads database and saved test lead")
            conn.close()
        
        # Test 3: Save to client 6 database
        print("\n3️⃣ Testing client 6 database save...")
        client_6_db_path = '/home/ggrun/CybrScan_1/client_databases/client_6_scans.db'
        
        if os.path.exists(client_6_db_path):
            conn = sqlite3.connect(client_6_db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO scan_reports (
                    scan_id, client_id, timestamp, lead_name, lead_email, lead_phone,
                    lead_company, company_size, target_domain, security_score,
                    vulnerabilities_found, risk_level, status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                scan_id,
                6,  # client_id
                test_scan_results['timestamp'],
                test_lead_data['name'],
                test_lead_data['email'],
                test_lead_data['phone'],
                test_lead_data['company'],
                test_lead_data['company_size'],
                test_scan_results['target_domain'],
                test_scan_results['security_score'],
                test_scan_results['vulnerabilities_found'],
                'Medium',
                'completed',
                datetime.now().isoformat()
            ))
            
            conn.commit()
            
            # Verify save
            cursor.execute("SELECT COUNT(*) FROM scan_reports WHERE client_id = 6")
            count = cursor.fetchone()[0]
            print(f"   ✅ Saved to client 6 database. Total scans: {count}")
            
            conn.close()
        
        # Test 4: Verify client dashboard can read the data
        print("\n4️⃣ Testing dashboard data retrieval...")
        try:
            from client_db import get_client_dashboard_data
            dashboard_data = get_client_dashboard_data(6)
            
            if dashboard_data:
                scan_count = len(dashboard_data['scan_history'])
                total_scans = dashboard_data['stats']['total_scans']
                print(f"   ✅ Dashboard data retrieved: {scan_count} in history, {total_scans} total")
                
                if scan_count > 0:
                    latest = dashboard_data['scan_history'][0]
                    print(f"   📋 Latest scan: {latest.get('lead_name')} | {latest.get('lead_email')}")
                else:
                    print(f"   ⚠️ No scans in history")
            else:
                print(f"   ❌ No dashboard data returned")
                
        except Exception as e:
            print(f"   ❌ Dashboard test failed: {e}")
        
        print("\n🎉 SCAN TRACKING TEST COMPLETE!")
        print("✅ If all tests passed, the scan tracking should now work")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_scan_tracking()
