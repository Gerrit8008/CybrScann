#!/usr/bin/env python3
"""
Add test scans to existing scanners to test scan counting
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from client_db import get_db_connection
from client_database_manager import save_scan_to_client_db, ensure_client_database
from datetime import datetime
import json

def add_test_scans():
    """Add test scans to existing scanners"""
    print("🧪 Adding test scans to existing scanners...")
    
    # Get existing scanners from main database
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT scanner_id, client_id, name FROM scanners WHERE status != 'deleted'")
        scanners = cursor.fetchall()
        conn.close()
        
        print(f"Found {len(scanners)} active scanners")
        
        for scanner_id, client_id, name in scanners:
            print(f"\nAdding test scans for {name} (ID: {scanner_id}, Client: {client_id})")
            
            # Ensure client database exists
            ensure_client_database(client_id, f"Client {client_id}")
            
            # Add 3-5 test scans for each scanner
            for i in range(3):
                test_scan_data = {
                    'scan_id': f'test_{scanner_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}_{i}',
                    'scanner_id': scanner_id,
                    'timestamp': datetime.now().isoformat(),
                    'name': f'Test User {i+1}',
                    'email': f'testuser{i+1}@{scanner_id}.com',
                    'phone': f'+123456789{i}',
                    'company': f'Test Company {i+1}',
                    'company_size': ['Small (1-50)', 'Medium (51-200)', 'Large (201+)'][i % 3],
                    'industry': ['Technology', 'Finance', 'Healthcare'][i % 3],
                    'target_domain': f'testdomain{i+1}.com',
                    'target_url': f'https://testdomain{i+1}.com',
                    'security_score': [85, 72, 91][i % 3],
                    'risk_level': ['Low', 'Medium', 'High'][i % 3],
                    'scan_type': 'comprehensive',
                    'status': 'completed',
                    'vulnerabilities_found': [2, 5, 1][i % 3],
                    'scan_results': json.dumps({
                        'findings': [
                            f'Finding {i+1} for {scanner_id}',
                            f'Security issue {i+1}',
                            f'Vulnerability {i+1}'
                        ],
                        'recommendations': [
                            f'Fix recommendation {i+1}',
                            f'Security improvement {i+1}'
                        ]
                    })
                }
                
                try:
                    save_scan_to_client_db(client_id, test_scan_data)
                    print(f"   ✅ Added test scan {i+1}/3")
                except Exception as e:
                    print(f"   ❌ Error adding scan {i+1}: {e}")
        
        print(f"\n🎉 Test scans added successfully!")
        print(f"\nNow check /client/scanners to see updated scan counts!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    add_test_scans()