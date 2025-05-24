#!/usr/bin/env python3
"""Debug why scans aren't being tracked for client 6"""

import sqlite3
import os
import sys
from datetime import datetime
sys.path.append('/home/ggrun/CybrScan_1')

def debug_scan_tracking():
    print("🔍 DEBUGGING SCAN TRACKING FOR CLIENT 6")
    print("=" * 50)
    
    # Check all databases for the latest scan
    scan_id = "f7daa05c-0e7b-4195-bfdc-a0e7b0ed4868"
    email = "gerrit.grundling@gmail.com"
    
    print(f"🎯 Looking for scan: {scan_id[:12]}...")
    print(f"📧 Email: {email}")
    
    # 1. Check main cybrscan.db
    print(f"\n📊 Checking main database...")
    main_db = '/home/ggrun/CybrScan_1/cybrscan.db'
    if os.path.exists(main_db):
        conn = sqlite3.connect(main_db)
        cursor = conn.cursor()
        
        # Check scan_results table
        cursor.execute("SELECT * FROM scan_results WHERE scan_id = ?", (scan_id,))
        result = cursor.fetchone()
        if result:
            print(f"✅ Found in scan_results: {result[:3]}")
        else:
            print(f"❌ Not found in scan_results")
            
        # Check for any recent scans
        cursor.execute("SELECT scan_id, target_domain, timestamp FROM scan_results ORDER BY timestamp DESC LIMIT 3")
        recent = cursor.fetchall()
        print(f"   Recent scans: {len(recent)}")
        for scan in recent:
            print(f"     {scan[0][:8]}... | {scan[1]} | {scan[2]}")
        
        conn.close()
    
    # 2. Check leads.db
    print(f"\n👥 Checking leads database...")
    leads_db = '/home/ggrun/CybrScan_1/leads.db'
    if os.path.exists(leads_db):
        conn = sqlite3.connect(leads_db)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM leads WHERE email = ?", (email,))
        lead = cursor.fetchone()
        if lead:
            print(f"✅ Found lead: {lead[1]} | {lead[2]} | {lead[4]}")
        else:
            print(f"❌ Lead not found")
            
        # Check recent leads
        cursor.execute("SELECT id, name, email, company FROM leads ORDER BY id DESC LIMIT 3")
        recent_leads = cursor.fetchall()
        print(f"   Recent leads: {len(recent_leads)}")
        for lead in recent_leads:
            print(f"     {lead[0]} | {lead[1]} | {lead[2]} | {lead[3]}")
        
        conn.close()
    
    # 3. Check if scan got saved to wrong client database
    print(f"\n🗃️ Checking all client databases...")
    client_db_dir = '/home/ggrun/CybrScan_1/client_databases'
    if os.path.exists(client_db_dir):
        for filename in os.listdir(client_db_dir):
            if filename.endswith('.db'):
                db_path = os.path.join(client_db_dir, filename)
                try:
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    
                    cursor.execute("SELECT COUNT(*) FROM scan_reports")
                    count = cursor.fetchone()[0]
                    
                    if count > 0:
                        cursor.execute("SELECT scan_id, lead_email, client_id FROM scan_reports LIMIT 3")
                        scans = cursor.fetchall()
                        print(f"   {filename}: {count} scans")
                        for scan in scans:
                            print(f"     {scan[0][:8]}... | {scan[1]} | Client {scan[2]}")
                    
                    conn.close()
                except Exception as e:
                    print(f"   {filename}: Error - {e}")
    
    # 4. Check session/user mapping
    print(f"\n👤 Checking user/client mapping...")
    main_db = '/home/ggrun/CybrScan_1/cybrscan.db'
    if os.path.exists(main_db):
        conn = sqlite3.connect(main_db)
        cursor = conn.cursor()
        
        # Find user 7 (from logs)
        cursor.execute("SELECT * FROM users WHERE id = 7")
        user = cursor.fetchone()
        if user:
            print(f"   User 7: {user[1]} | {user[3]}")
            
        # Find client 6
        cursor.execute("SELECT * FROM clients WHERE id = 6")
        client = cursor.fetchone()
        if client:
            print(f"   Client 6: {client[2]} | User ID: {client[1]}")
            
        # Check if user 7 is linked to client 6
        cursor.execute("SELECT * FROM clients WHERE user_id = 7")
        user_client = cursor.fetchone()
        if user_client:
            print(f"   User 7 -> Client {user_client[0]}: {user_client[2]}")
        else:
            print(f"   ❌ User 7 not linked to any client")
        
        conn.close()

def fix_scan_tracking():
    """Fix the scan tracking by manually linking the scan"""
    print(f"\n🔧 FIXING SCAN TRACKING")
    print("=" * 25)
    
    try:
        # Get the scan and lead data
        scan_id = "f7daa05c-0e7b-4195-bfdc-a0e7b0ed4868"
        
        # Get scan data from main database
        main_db = '/home/ggrun/CybrScan_1/cybrscan.db'
        scan_data = None
        
        if os.path.exists(main_db):
            conn = sqlite3.connect(main_db)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT scan_id, target_domain, security_score, timestamp, vulnerabilities_found
                FROM scan_results WHERE scan_id = ?
            """, (scan_id,))
            result = cursor.fetchone()
            
            if result:
                scan_data = {
                    'scan_id': result[0],
                    'target_domain': result[1],
                    'security_score': result[2],
                    'timestamp': result[3],
                    'vulnerabilities_found': result[4] or 0
                }
                print(f"✅ Found scan data")
            
            conn.close()
        
        # Get lead data
        leads_db = '/home/ggrun/CybrScan_1/leads.db'
        lead_data = None
        
        if os.path.exists(leads_db):
            conn = sqlite3.connect(leads_db)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT name, email, phone, company, company_size
                FROM leads ORDER BY id DESC LIMIT 1
            """)
            result = cursor.fetchone()
            
            if result:
                lead_data = {
                    'name': result[0],
                    'email': result[1],
                    'phone': result[2],
                    'company': result[3],
                    'company_size': result[4]
                }
                print(f"✅ Found lead data: {result[0]} | {result[1]}")
            
            conn.close()
        
        # Save to client 6 database
        if scan_data and lead_data:
            client_6_db = '/home/ggrun/CybrScan_1/client_databases/client_6_scans.db'
            
            conn = sqlite3.connect(client_6_db)
            cursor = conn.cursor()
            
            # Calculate risk level
            score = scan_data['security_score']
            if score >= 90:
                risk_level = 'Low'
            elif score >= 70:
                risk_level = 'Medium'
            else:
                risk_level = 'High'
            
            cursor.execute("""
                INSERT OR REPLACE INTO scan_reports (
                    scan_id, client_id, timestamp, lead_name, lead_email, lead_phone,
                    lead_company, company_size, target_domain, security_score,
                    vulnerabilities_found, risk_level, status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                scan_data['scan_id'],
                6,  # client_id
                scan_data['timestamp'],
                lead_data['name'],
                lead_data['email'],
                lead_data['phone'],
                lead_data['company'],
                lead_data['company_size'],
                scan_data['target_domain'],
                scan_data['security_score'],
                scan_data['vulnerabilities_found'],
                risk_level,
                'completed',
                datetime.now().isoformat()
            ))
            
            conn.commit()
            
            # Verify
            cursor.execute("SELECT COUNT(*) FROM scan_reports WHERE client_id = 6")
            count = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT scan_id, lead_name, lead_email, target_domain, security_score 
                FROM scan_reports WHERE client_id = 6 ORDER BY timestamp DESC LIMIT 1
            """)
            latest = cursor.fetchone()
            
            conn.close()
            
            print(f"✅ Successfully saved scan to client 6 database")
            print(f"   Total scans for client 6: {count}")
            print(f"   Latest: {latest[1]} | {latest[2]} | {latest[3]} | {latest[4]}%")
            
            return True
        else:
            print(f"❌ Missing scan or lead data")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing scan tracking: {e}")
        import traceback
        traceback.print_exc()
        return False

def fix_user_client_mapping():
    """Fix the user-client mapping if needed"""
    print(f"\n🔗 CHECKING USER-CLIENT MAPPING")
    print("=" * 35)
    
    try:
        main_db = '/home/ggrun/CybrScan_1/cybrscan.db'
        
        if os.path.exists(main_db):
            conn = sqlite3.connect(main_db)
            cursor = conn.cursor()
            
            # Check if user 7 has a client
            cursor.execute("SELECT * FROM clients WHERE user_id = 7")
            result = cursor.fetchone()
            
            if result:
                print(f"✅ User 7 is linked to client {result[0]}: {result[2]}")
            else:
                print(f"❌ User 7 is not linked to any client")
                
                # Check if client 6 exists and what user it's linked to
                cursor.execute("SELECT * FROM clients WHERE id = 6")
                client_6 = cursor.fetchone()
                
                if client_6:
                    print(f"   Client 6 exists: {client_6[2]} (User ID: {client_6[1]})")
                    
                    # Link user 7 to client 6 if client 6 has no user
                    if client_6[1] is None:
                        cursor.execute("UPDATE clients SET user_id = 7 WHERE id = 6")
                        conn.commit()
                        print(f"✅ Linked user 7 to client 6")
                else:
                    print(f"   Client 6 doesn't exist")
            
            conn.close()
            
    except Exception as e:
        print(f"❌ Error checking user-client mapping: {e}")

if __name__ == "__main__":
    debug_scan_tracking()
    fix_scan_tracking()
    fix_user_client_mapping()
    
    print(f"\n🎯 NEXT STEPS:")
    print("1. Refresh the client dashboard")
    print("2. Check if the scan now appears")
    print("3. The scan should show: gerrit.grundling@gmail.com scanning gmail.com")