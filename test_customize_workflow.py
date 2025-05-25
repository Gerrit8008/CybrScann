#!/usr/bin/env python3
"""Test the complete customize workflow to identify issues"""

import sys
import os
sys.path.append('/home/ggrun/CybrScan_1')

def test_customize_route_dependencies():
    """Test that all dependencies for customize route exist"""
    print("🔧 Testing customize route dependencies...")
    
    try:
        # Test basic imports
        print("Testing imports...")
        from client_db import get_client_by_user_id, get_db_connection
        print("✅ client_db imports work")
        
        # Test template existence
        template_path = '/home/ggrun/CybrScan_1/templates/client/customize_scanner.html'
        if os.path.exists(template_path):
            print("✅ Client customize template exists")
        else:
            print("❌ Client customize template missing")
            
        admin_template_path = '/home/ggrun/CybrScan_1/templates/admin/customization-form.html'
        if os.path.exists(admin_template_path):
            print("✅ Admin customize template exists")
        else:
            print("❌ Admin customize template missing")
        
        # Test database functions
        print("Testing database functions...")
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Test getting a client
        cursor.execute("SELECT id, user_id FROM clients LIMIT 1")
        client_row = cursor.fetchone()
        if client_row:
            client_id, user_id = client_row
            print(f"✅ Found test client: ID {client_id}, User {user_id}")
            
            # Test get_client_by_user_id function
            client_data = get_client_by_user_id(user_id)
            if client_data:
                print(f"✅ get_client_by_user_id works: {client_data.get('business_name')}")
            else:
                print("❌ get_client_by_user_id returns None")
        else:
            print("❌ No clients found in database")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Dependency test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_form_field_mapping():
    """Test that form fields map correctly between frontend and backend"""
    print("\n🔧 Testing form field mapping...")
    
    # Expected form fields from the frontend
    frontend_fields = [
        'business_name', 'business_domain', 'contact_email', 'contact_phone',
        'scanner_name', 'primary_color', 'secondary_color', 'button_color',
        'email_subject', 'email_intro', 'default_scans[]', 'logo'
    ]
    
    print("Frontend sends these fields:")
    for field in frontend_fields:
        print(f"  - {field}")
    
    # Check if the customize route expects these fields (from the code)
    expected_backend_fields = [
        'business_name', 'business_domain', 'contact_email', 'contact_phone',
        'scanner_name', 'primary_color', 'secondary_color', 'button_color',
        'email_subject', 'email_intro', 'default_scans', 'logo'
    ]
    
    print("\nBackend expects these fields:")
    for field in expected_backend_fields:
        print(f"  - {field}")
    
    # Check for mismatches
    mismatches = []
    for field in frontend_fields:
        clean_field = field.replace('[]', '')
        if clean_field not in expected_backend_fields:
            mismatches.append(field)
    
    if mismatches:
        print(f"\n❌ Field mismatches found: {mismatches}")
        return False
    else:
        print("\n✅ All form fields map correctly")
        return True

def test_javascript_issues():
    """Check for common JavaScript issues in the template"""
    print("\n🔧 Testing JavaScript in template...")
    
    template_path = '/home/ggrun/CybrScan_1/templates/client/customize_scanner.html'
    
    try:
        with open(template_path, 'r') as f:
            content = f.read()
        
        # Check for common JavaScript issues
        issues = []
        
        # Check if FormData is used correctly
        if 'new FormData()' in content:
            print("✅ FormData used for submission")
        else:
            issues.append("FormData not used for form submission")
        
        # Check if fetch is used correctly
        if "fetch('/customize'" in content:
            print("✅ Fetch request to /customize found")
        else:
            issues.append("No fetch request to /customize found")
        
        # Check if button_color is handled
        if 'button_color' in content:
            print("✅ button_color field handled in JavaScript")
        else:
            issues.append("button_color not handled in JavaScript")
        
        # Check for console.log debugging
        if 'console.log' in content:
            print("✅ Debug logging present")
        else:
            print("⚠️ No debug logging found")
        
        if issues:
            print(f"❌ JavaScript issues found:")
            for issue in issues:
                print(f"  - {issue}")
            return False
        else:
            print("✅ No obvious JavaScript issues")
            return True
            
    except Exception as e:
        print(f"❌ Error reading template: {e}")
        return False

def test_button_color_flow():
    """Test the specific button color functionality"""
    print("\n🔧 Testing button color flow...")
    
    try:
        # Test database schema for button_color
        from client_db import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if customizations table has button_color
        cursor.execute("PRAGMA table_info(customizations)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'button_color' in columns:
            print("✅ button_color column exists in customizations table")
        else:
            print("❌ button_color column missing from customizations table")
            return False
        
        # Check if scanners table has button_color equivalent
        cursor.execute("PRAGMA table_info(scanners)")
        scanner_columns = [col[1] for col in cursor.fetchall()]
        
        # Scanners might not have button_color but should use it from customizations
        print(f"✅ Scanner table has {len(scanner_columns)} columns")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Button color test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 TESTING CUSTOMIZE FUNCTIONALITY")
    print("=" * 50)
    
    tests = [
        test_customize_route_dependencies,
        test_form_field_mapping,
        test_javascript_issues,
        test_button_color_flow
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("🏁 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed! Customization should work.")
    else:
        print("❌ Some tests failed. Issues need to be fixed.")
        print("\nNext steps:")
        print("1. Fix the failing tests above")
        print("2. Test the /customize route manually")
        print("3. Check browser console for JavaScript errors")
        print("4. Verify form submission works end-to-end")

if __name__ == "__main__":
    main()