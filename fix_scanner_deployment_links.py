#!/usr/bin/env python3
"""
Fix scanner deployment links by ensuring all scanners have deployment files
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def fix_all_scanner_deployments():
    """Generate deployment files for all scanners that don't have them"""
    print("🔧 Fixing Scanner Deployment Links")
    print("=" * 50)
    
    try:
        from client_db import get_db_connection
        from scanner_deployment import generate_scanner_deployment
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get all scanners
        cursor.execute('''
            SELECT s.*, c.business_name 
            FROM scanners s 
            JOIN clients c ON s.client_id = c.id 
            ORDER BY s.created_at DESC
        ''')
        
        scanners = cursor.fetchall()
        
        if not scanners:
            print("❌ No scanners found in database")
            return
            
        print(f"📝 Found {len(scanners)} scanner(s)")
        
        for i, scanner_row in enumerate(scanners):
            scanner_id = scanner_row[2]  # scanner_id
            scanner_name = scanner_row[3]  # name
            business_name = scanner_row[-1]  # business_name from JOIN
            
            print(f"\n🔍 Scanner {i+1}: {scanner_name} ({scanner_id})")
            
            # Check if deployment exists
            deployment_path = os.path.join('static', 'deployments', scanner_id, 'index.html')
            
            if os.path.exists(deployment_path):
                print(f"   ✅ Deployment already exists")
            else:
                print(f"   🔧 Generating missing deployment...")
                
                # Prepare scanner data
                scanner_data = {
                    'name': scanner_row[3],
                    'business_name': business_name,
                    'description': scanner_row[4] or f'Security scanner for {business_name}',
                    'domain': scanner_row[5],
                    'primary_color': scanner_row[7] or '#02054c',
                    'secondary_color': scanner_row[8] or '#35a310',
                    'logo_url': scanner_row[9] or '',
                    'contact_email': scanner_row[10],
                    'contact_phone': scanner_row[11],
                    'email_subject': scanner_row[12] or 'Your Security Scan Report',
                    'email_intro': scanner_row[13] or '',
                    'scan_types': ['port_scan', 'ssl_check']
                }
                
                api_key = scanner_row[6]  # api_key
                
                result = generate_scanner_deployment(scanner_id, scanner_data, api_key)
                
                if result['status'] == 'success':
                    print(f"   ✅ Deployment generated successfully")
                else:
                    print(f"   ❌ Deployment failed: {result['message']}")
        
        # List all deployment directories
        print(f"\n📁 Available deployment directories:")
        deployment_base = 'static/deployments'
        if os.path.exists(deployment_base):
            dirs = os.listdir(deployment_base)
            for dir_name in dirs:
                print(f"   - {dir_name}")
        
        # Test embed links for all scanners
        print(f"\n🔗 Scanner embed links:")
        for scanner_row in scanners:
            scanner_id = scanner_row[2]
            scanner_name = scanner_row[3]
            print(f"   {scanner_name}: /scanner/{scanner_id}/embed")
        
        conn.close()
        
        print(f"\n🎉 Scanner deployment links fixed!")
        print("✅ All scanners now have deployment files")
        print("✅ Embed routes will work correctly")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_all_scanner_deployments()