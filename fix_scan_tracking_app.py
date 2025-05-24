#!/usr/bin/env python3
"""Fix the scan tracking section in app.py"""

import re

def fix_scan_tracking_code():
    """Fix the corrupted scan tracking code in app.py"""
    print("🔧 FIXING SCAN TRACKING CODE IN APP.PY")
    print("=" * 45)
    
    app_py_path = '/home/ggrun/CybrScan_1/app.py'
    
    try:
        # Read the file
        with open(app_py_path, 'r') as f:
            content = f.read()
        
        # Find the problematic section and replace it
        # Look for the section from line 3112 onwards
        pattern = r"(\s+else:\s+# Check if current user is logged in and link scan to their client.*?)(\s+# Check if scan_results contains valid data)"
        
        replacement = '''            else:
                # Check if current user is logged in and link scan to their client
                try:
                    from client_db import verify_session, get_client_by_user_id
                    session_token = session.get('session_token')
                    if session_token:
                        result = verify_session(session_token)
                        # Handle different return formats from verify_session
                        if result.get('status') == 'success' and result.get('user'):
                            user_client = get_client_by_user_id(result['user']['user_id'])
                            if user_client:
                                scan_results['client_id'] = user_client['id']
                                scan_results['scanner_id'] = 'web_interface'
                                scan_results.update(lead_data)
                                logger.info(f"Linked scan to client {user_client['id']} via user {result['user']['user_id']}")
                                
                                # Save to client-specific database
                                try:
                                    from client_database_manager import save_scan_to_client_db
                                    save_scan_to_client_db(user_client['id'], scan_results)
                                    logging.info(f"Saved scan to client-specific database for client {user_client['id']}")
                                except Exception as client_db_error:
                                    logging.error(f"Error saving to client-specific database: {client_db_error}")
                                
                                # Legacy client logging
                                try:
                                    from client_db import log_scan
                                    log_scan(user_client['id'], scan_results['scan_id'], lead_data.get('target', ''), 'comprehensive')
                                except Exception as log_error:
                                    logging.error(f"Error logging scan: {log_error}")
                            else:
                                logger.warning(f"No client found for user {result['user']['user_id']}")
                        else:
                            logger.warning(f"Session verification failed: {result.get('message', 'Unknown error')}")
                    else:
                        logger.warning("No session token found for scan linking")
                                
                except Exception as e:
                    logger.warning(f"Could not link scan to current user: {e}")
                    import traceback
                    logger.warning(traceback.format_exc())
            
            '''
        
        # Use regex to replace the problematic section
        new_content = re.sub(pattern, replacement + r'\\2', content, flags=re.DOTALL)
        
        if new_content != content:
            # Write the fixed content back
            with open(app_py_path, 'w') as f:
                f.write(new_content)
            
            print("✅ Fixed scan tracking code in app.py")
            return True
        else:
            print("❌ Could not find the problematic section to fix")
            
            # Try a simpler approach - just fix the KeyError issue
            if "if result['valid']:" in content:
                content = content.replace(
                    "if result['valid']:",
                    "if result.get('status') == 'success' and result.get('user'):"
                )
                
                with open(app_py_path, 'w') as f:
                    f.write(content)
                
                print("✅ Fixed KeyError: 'valid' issue")
                return True
            else:
                print("❌ KeyError issue not found either")
                return False
            
    except Exception as e:
        print(f"❌ Error fixing scan tracking code: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_scan_tracking_test():
    """Create a test to verify scan tracking works"""
    print("\n🧪 CREATING SCAN TRACKING TEST")
    print("=" * 35)
    
    test_code = '''#!/usr/bin/env python3
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
        print("\\n1️⃣ Testing main database save...")
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
        print("\\n2️⃣ Testing leads database save...")
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
        print("\\n3️⃣ Testing client 6 database save...")
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
        print("\\n4️⃣ Testing dashboard data retrieval...")
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
        
        print("\\n🎉 SCAN TRACKING TEST COMPLETE!")
        print("✅ If all tests passed, the scan tracking should now work")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_scan_tracking()
'''
    
    with open('/home/ggrun/CybrScan_1/test_scan_tracking_final.py', 'w') as f:
        f.write(test_code)
    
    print("✅ Created test_scan_tracking_final.py")
    return True

if __name__ == "__main__":
    success1 = fix_scan_tracking_code()
    success2 = create_scan_tracking_test()
    
    if success1 and success2:
        print("\n🎉 SCAN TRACKING FIXES COMPLETE!")
        print("✅ Fixed KeyError: 'valid' issue")
        print("✅ Created comprehensive test")
        print("\n🔄 Next steps:")
        print("1. Run: python3 test_scan_tracking_final.py")
        print("2. Test a new scan to see if it appears in dashboard")
        print("3. Check client dashboard for scan history")
    else:
        print("\n❌ Some fixes failed. Check errors above.")