#!/usr/bin/env python3
"""Fix client 6 database schema issues"""

import sqlite3
import os
import sys
sys.path.append('/home/ggrun/CybrScan_1')

def fix_client_6_database():
    print("🔧 FIXING CLIENT 6 DATABASE SCHEMA")
    print("=" * 45)
    
    try:
        # Check for client 6 database
        client_db_dir = '/home/ggrun/CybrScan_1/client_databases'
        client_6_db_path = os.path.join(client_db_dir, 'client_6_scans.db')
        
        print(f"📂 Looking for client 6 database: {client_6_db_path}")
        
        if not os.path.exists(client_6_db_path):
            print("❌ Client 6 database doesn't exist, creating it...")
            
            # Create the database directory if it doesn't exist
            os.makedirs(client_db_dir, exist_ok=True)
            
            # Create database with proper schema
            conn = sqlite3.connect(client_6_db_path)
            cursor = conn.cursor()
            
            # Create scan_reports table with proper schema
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scan_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_id TEXT UNIQUE NOT NULL,
                    client_id INTEGER NOT NULL,
                    scanner_id INTEGER,
                    timestamp TEXT,
                    lead_name TEXT,
                    lead_email TEXT,
                    lead_phone TEXT,
                    lead_company TEXT,
                    company_size TEXT,
                    target_domain TEXT,
                    security_score REAL,
                    vulnerabilities_found INTEGER DEFAULT 0,
                    risk_level TEXT,
                    scan_type TEXT DEFAULT 'standard',
                    status TEXT DEFAULT 'completed',
                    created_at TEXT,
                    updated_at TEXT
                )
            ''')
            
            print("✅ Created client 6 database with proper schema")
            conn.commit()
            conn.close()
            
        else:
            print("✅ Client 6 database exists, checking schema...")
            
            # Check existing schema
            conn = sqlite3.connect(client_6_db_path)
            cursor = conn.cursor()
            
            # Get table info
            cursor.execute("PRAGMA table_info(scan_reports)")
            columns = cursor.fetchall()
            
            column_names = [col[1] for col in columns]
            print(f"   Current columns: {column_names}")
            
            # Check if client_id column exists
            if 'client_id' not in column_names:
                print("❌ Missing client_id column, adding it...")
                cursor.execute("ALTER TABLE scan_reports ADD COLUMN client_id INTEGER")
                
                # Set client_id to 6 for all existing records
                cursor.execute("UPDATE scan_reports SET client_id = 6 WHERE client_id IS NULL")
                print("✅ Added client_id column and set to 6 for existing records")
            else:
                print("✅ client_id column exists")
            
            # Ensure other required columns exist
            required_columns = [
                ('scanner_id', 'INTEGER'),
                ('lead_name', 'TEXT'),
                ('lead_email', 'TEXT'), 
                ('lead_phone', 'TEXT'),
                ('lead_company', 'TEXT'),
                ('company_size', 'TEXT'),
                ('target_domain', 'TEXT'),
                ('security_score', 'REAL'),
                ('vulnerabilities_found', 'INTEGER DEFAULT 0'),
                ('risk_level', 'TEXT'),
                ('scan_type', 'TEXT DEFAULT "standard"'),
                ('status', 'TEXT DEFAULT "completed"'),
                ('created_at', 'TEXT'),
                ('updated_at', 'TEXT')
            ]
            
            for col_name, col_type in required_columns:
                if col_name not in column_names:
                    print(f"   Adding missing column: {col_name}")
                    try:
                        cursor.execute(f"ALTER TABLE scan_reports ADD COLUMN {col_name} {col_type}")
                    except sqlite3.OperationalError as e:
                        print(f"   ⚠️ Could not add {col_name}: {e}")
            
            conn.commit()
            conn.close()
        
        # Test the database
        print("\n🧪 Testing client 6 database...")
        conn = sqlite3.connect(client_6_db_path)
        cursor = conn.cursor()
        
        # Check if we can query with client_id
        cursor.execute("SELECT COUNT(*) FROM scan_reports WHERE client_id = 6")
        count = cursor.fetchone()[0]
        print(f"   Records for client 6: {count}")
        
        # Check recent scans
        cursor.execute("SELECT scan_id, lead_name, lead_email, target_domain FROM scan_reports ORDER BY timestamp DESC LIMIT 5")
        recent_scans = cursor.fetchall()
        
        if recent_scans:
            print(f"   Recent scans:")
            for scan in recent_scans:
                print(f"     - {scan[0][:8]}... | {scan[1]} | {scan[2]} | {scan[3]}")
        else:
            print("   No scans found")
        
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing client 6 database: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_latest_scan():
    """Check if the latest scan from the logs is properly stored"""
    print("\n🔍 CHECKING LATEST SCAN STORAGE")
    print("=" * 35)
    
    try:
        # The scan ID from the logs
        latest_scan_id = "f7daa05c-0e7b-4195-bfdc-a0e7b0ed4868"
        
        # Check main database
        main_db_path = '/home/ggrun/CybrScan_1/cybrscan.db'
        if os.path.exists(main_db_path):
            conn = sqlite3.connect(main_db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM scan_results WHERE scan_id = ?", (latest_scan_id,))
            main_result = cursor.fetchone()
            
            if main_result:
                print(f"✅ Found scan in main database: {latest_scan_id[:8]}...")
                print(f"   Target: {main_result[2] if len(main_result) > 2 else 'Unknown'}")
            else:
                print(f"❌ Scan not found in main database")
            
            conn.close()
        
        # Check leads database
        leads_db_path = '/home/ggrun/CybrScan_1/leads.db'
        if os.path.exists(leads_db_path):
            conn = sqlite3.connect(leads_db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM leads ORDER BY id DESC LIMIT 1")
            latest_lead = cursor.fetchone()
            
            if latest_lead:
                print(f"✅ Latest lead: {latest_lead[1]} | {latest_lead[2]}")
            else:
                print(f"❌ No leads found")
            
            conn.close()
        
        # Check if scan should be in client 6 database
        client_6_db_path = '/home/ggrun/CybrScan_1/client_databases/client_6_scans.db'
        if os.path.exists(client_6_db_path):
            conn = sqlite3.connect(client_6_db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM scan_reports WHERE scan_id = ?", (latest_scan_id,))
            client_result = cursor.fetchone()
            
            if client_result:
                print(f"✅ Found scan in client 6 database")
            else:
                print(f"❌ Scan not found in client 6 database")
                
                # Try to find it by lead email
                cursor.execute("SELECT * FROM scan_reports WHERE lead_email = 'gerrit.grundling@gmail.com'")
                email_result = cursor.fetchone()
                
                if email_result:
                    print(f"✅ Found scan by email: {email_result[1]}")
                else:
                    print(f"❌ No scan found for gerrit.grundling@gmail.com")
            
            conn.close()
            
    except Exception as e:
        print(f"❌ Error checking latest scan: {e}")

def save_scan_to_client_6():
    """Save the latest scan to client 6 database"""
    print("\n💾 SAVING LATEST SCAN TO CLIENT 6 DATABASE")
    print("=" * 45)
    
    try:
        # Get scan data from main database
        main_db_path = '/home/ggrun/CybrScan_1/cybrscan.db'
        leads_db_path = '/home/ggrun/CybrScan_1/leads.db'
        
        scan_data = {}
        
        # Get scan results
        if os.path.exists(main_db_path):
            conn = sqlite3.connect(main_db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT scan_id, target_domain, security_score, timestamp, vulnerabilities_found 
                FROM scan_results 
                ORDER BY timestamp DESC 
                LIMIT 1
            """)
            scan_result = cursor.fetchone()
            
            if scan_result:
                scan_data.update({
                    'scan_id': scan_result[0],
                    'target_domain': scan_result[1],
                    'security_score': scan_result[2],
                    'timestamp': scan_result[3],
                    'vulnerabilities_found': scan_result[4] or 0
                })
                print(f"✅ Got scan data: {scan_result[0][:8]}...")
            
            conn.close()
        
        # Get lead data
        if os.path.exists(leads_db_path):
            conn = sqlite3.connect(leads_db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT name, email, phone, company, company_size 
                FROM leads 
                ORDER BY id DESC 
                LIMIT 1
            """)
            lead_result = cursor.fetchone()
            
            if lead_result:
                scan_data.update({
                    'lead_name': lead_result[0],
                    'lead_email': lead_result[1],
                    'lead_phone': lead_result[2],
                    'lead_company': lead_result[3],
                    'company_size': lead_result[4]
                })
                print(f"✅ Got lead data: {lead_result[0]} | {lead_result[1]}")
            
            conn.close()
        
        # Save to client 6 database
        if scan_data:
            client_6_db_path = '/home/ggrun/CybrScan_1/client_databases/client_6_scans.db'
            conn = sqlite3.connect(client_6_db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO scan_reports (
                    scan_id, client_id, timestamp, lead_name, lead_email, lead_phone,
                    lead_company, company_size, target_domain, security_score,
                    vulnerabilities_found, risk_level, status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                scan_data.get('scan_id'),
                6,  # client_id
                scan_data.get('timestamp'),
                scan_data.get('lead_name'),
                scan_data.get('lead_email'),
                scan_data.get('lead_phone'),
                scan_data.get('lead_company'),
                scan_data.get('company_size'),
                scan_data.get('target_domain'),
                scan_data.get('security_score'),
                scan_data.get('vulnerabilities_found', 0),
                'Medium' if scan_data.get('security_score', 0) < 80 else 'Low',
                'completed',
                scan_data.get('timestamp')
            ))
            
            conn.commit()
            conn.close()
            
            print(f"✅ Saved scan to client 6 database")
            
            # Verify it was saved
            conn = sqlite3.connect(client_6_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM scan_reports WHERE client_id = 6")
            count = cursor.fetchone()[0]
            print(f"   Client 6 now has {count} scan(s)")
            conn.close()
            
        else:
            print("❌ No scan data found to save")
            
    except Exception as e:
        print(f"❌ Error saving scan to client 6: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🔧 CLIENT 6 DATABASE REPAIR")
    print("=" * 30)
    
    success1 = fix_client_6_database()
    check_latest_scan()
    save_scan_to_client_6()
    
    if success1:
        print("\n🎉 CLIENT 6 DATABASE FIXED!")
        print("✅ Schema corrected with client_id column")
        print("✅ Latest scan data should now be visible")
        print("✅ Dashboard should show scan history")
        print("\n🔄 Refresh your dashboard to see the changes!")
    else:
        print("\n❌ Some issues remain. Check errors above.")