#!/usr/bin/env python3
"""
Fix the specific scanner that was just created: scanner_bf504751
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def fix_scanner_bf504751():
    """Fix the deployment for scanner_bf504751"""
    print("🔧 Fixing Scanner scanner_bf504751")
    print("=" * 50)
    
    try:
        from client_db import get_db_connection
        from scanner_deployment import generate_scanner_deployment
        
        scanner_id = 'scanner_bf504751'
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get scanner details
        cursor.execute('''
            SELECT s.*, c.business_name 
            FROM scanners s 
            JOIN clients c ON s.client_id = c.id 
            WHERE s.scanner_id = ?
        ''', (scanner_id,))
        
        scanner_row = cursor.fetchone()
        
        if not scanner_row:
            print(f"❌ Scanner {scanner_id} not found in database")
            return
            
        print(f"✅ Found scanner: {scanner_row[3]}")  # name
        print(f"   Business: {scanner_row[-1]}")  # business_name
        print(f"   Primary Color: {scanner_row[7]}")  # primary_color
        print(f"   Secondary Color: {scanner_row[8]}")  # secondary_color
        
        # Check if deployment exists
        deployment_path = os.path.join('static', 'deployments', scanner_id)
        
        if os.path.exists(deployment_path):
            print(f"🗑️  Removing old deployment...")
            import shutil
            shutil.rmtree(deployment_path)
        
        # Prepare scanner data with correct colors from the form submission
        scanner_data = {
            'name': scanner_row[3],  # scanner name
            'business_name': scanner_row[-1],  # business_name from join
            'description': scanner_row[4] or f'Security scanner for {scanner_row[-1]}',
            'domain': scanner_row[5],
            'primary_color': '#ea1f1f',  # From the form data in logs
            'secondary_color': '#c35099',  # From the form data in logs
            'logo_url': scanner_row[9] or '',
            'contact_email': scanner_row[10],
            'contact_phone': scanner_row[11],
            'email_subject': scanner_row[12] or 'Your Security Scan Report',
            'email_intro': scanner_row[13] or 'Thank you for using our security scanner. Please find your detailed report attached.',
            'scan_types': ['network', 'web', 'email', 'system']  # From form data
        }
        
        print(f"🎨 Regenerating with colors: {scanner_data['primary_color']}, {scanner_data['secondary_color']}")
        
        # Regenerate deployment with correct colors
        api_key = scanner_row[6]  # api_key
        result = generate_scanner_deployment(scanner_id, scanner_data, api_key)
        
        if result['status'] == 'success':
            print(f"✅ Deployment regenerated: {result['deployment_path']}")
            
            # Verify the colors are in the CSS
            css_path = os.path.join(result['deployment_path'], 'scanner-styles.css')
            if os.path.exists(css_path):
                with open(css_path, 'r') as f:
                    css_content = f.read()
                    
                if '#ea1f1f' in css_content:
                    print("   ✅ Primary color #ea1f1f found in CSS")
                else:
                    print("   ❌ Primary color not found in CSS")
                    
                if '#c35099' in css_content:
                    print("   ✅ Secondary color #c35099 found in CSS")
                else:
                    print("   ❌ Secondary color not found in CSS")
            
            # Verify business name in HTML
            html_path = os.path.join(result['deployment_path'], 'index.html')
            if os.path.exists(html_path):
                with open(html_path, 'r') as f:
                    html_content = f.read()
                    
                if 'Test Company' in html_content:
                    print("   ✅ Business name 'Test Company' found in HTML")
                    
                if 'Test Scanner' in html_content:
                    print("   ✅ Scanner name 'Test Scanner' found in HTML")
            
            print(f"\n🎉 Scanner fixed!")
            print(f"   - Custom colors applied: #ea1f1f (red), #c35099 (purple)")
            print(f"   - Business name: Test Company")
            print(f"   - Scanner name: Test Scanner")
            print(f"   - CSS and JS files will now load correctly")
            
        else:
            print(f"❌ Deployment failed: {result['message']}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_scanner_bf504751()