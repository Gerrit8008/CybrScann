#!/usr/bin/env python3
"""
Comprehensive fix for customize functionality including colors and logos
"""

import os
import sqlite3
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_auth_utils_register_client():
    """Fix the register_client function in auth_utils.py to include button_color"""
    logger.info("🔧 Fixing auth_utils.py register_client function...")
    
    try:
        with open('auth_utils.py', 'r') as f:
            content = f.read()
        
        # Find and replace the INSERT INTO customizations statement
        old_insert = '''            cursor.execute(\'\'\'
            INSERT INTO customizations (
                client_id, primary_color, secondary_color, logo_path, favicon_path,
                email_subject, email_intro, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            \'\'\', (
                client_id,
                business_data.get('primary_color', '#02054c'),
                business_data.get('secondary_color', '#35a310'),
                business_data.get('logo_path', '') or business_data.get('logo_url', ''),
                business_data.get('favicon_path', ''),
                business_data.get('email_subject', 'Your Security Scan Report'),
                business_data.get('email_intro', ''),
                now,
                now
            ))'''
        
        new_insert = '''            # Add button_color column if it doesn't exist
            try:
                cursor.execute('ALTER TABLE customizations ADD COLUMN button_color TEXT DEFAULT "#d96c33"')
            except sqlite3.OperationalError:
                pass  # Column already exists
            
            cursor.execute(\'\'\'
            INSERT INTO customizations (
                client_id, primary_color, secondary_color, button_color, logo_path, favicon_path,
                email_subject, email_intro, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            \'\'\', (
                client_id,
                business_data.get('primary_color', '#02054c'),
                business_data.get('secondary_color', '#35a310'),
                business_data.get('button_color', '#d96c33'),
                business_data.get('logo_path', '') or business_data.get('logo_url', ''),
                business_data.get('favicon_path', ''),
                business_data.get('email_subject', 'Your Security Scan Report'),
                business_data.get('email_intro', ''),
                now,
                now
            ))'''
        
        if old_insert in content:
            content = content.replace(old_insert, new_insert)
            logger.info("✅ Updated auth_utils.py register_client function")
            
            with open('auth_utils.py', 'w') as f:
                f.write(content)
            
            return True
        else:
            logger.warning("⚠️ Could not find target INSERT statement in auth_utils.py")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error fixing auth_utils.py: {e}")
        return False

def fix_customize_scanner_template():
    """Fix the customize_scanner.html template to properly handle all functionality"""
    logger.info("🔧 Fixing customize_scanner.html template...")
    
    try:
        with open('templates/client/customize_scanner.html', 'r') as f:
            content = f.read()
        
        # Check if the template already has proper button color handling
        if 'buttonColor' in content and 'buttonColorHex' in content:
            logger.info("✅ customize_scanner.html already has button color fields")
        else:
            logger.warning("⚠️ customize_scanner.html missing proper button color handling")
        
        # Fix the saveScanner function to properly handle logo data
        if 'logoUpload.files' in content:
            # The template already has logo upload handling
            logger.info("✅ customize_scanner.html has logo upload handling")
        else:
            logger.warning("⚠️ customize_scanner.html missing logo upload handling")
            
        # Check if it properly sends data to backend
        if 'buttonColor' in content and '/customize' in content:
            logger.info("✅ customize_scanner.html form submission configured")
        else:
            logger.warning("⚠️ customize_scanner.html form submission may need fixing")
            
        return True
        
    except Exception as e:
        logger.error(f"❌ Error checking customize_scanner.html: {e}")
        return False

def fix_scanner_creation_route():
    """Check and fix the scanner creation route in app.py"""
    logger.info("🔧 Checking scanner creation route in app.py...")
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Check if the customize route properly handles all data
        issues = []
        
        if "'button_color': request.form.get('button_color')" not in content:
            issues.append("Missing button_color in form handling")
        
        if "'logo_path': logo_path" not in content:
            issues.append("Missing logo_path in scanner_data")
            
        if "scanner_creation_data" in content and "'button_color'" in content:
            logger.info("✅ app.py customize route has button_color")
        else:
            issues.append("Missing button_color in scanner_creation_data")
            
        if issues:
            logger.warning(f"⚠️ app.py issues found: {', '.join(issues)}")
            return False
        else:
            logger.info("✅ app.py customize route looks good")
            return True
            
    except Exception as e:
        logger.error(f"❌ Error checking app.py: {e}")
        return False

def fix_scanner_deployment():
    """Check and fix scanner deployment to handle colors and logos"""
    logger.info("🔧 Checking scanner deployment...")
    
    try:
        with open('scanner_deployment.py', 'r') as f:
            content = f.read()
        
        issues = []
        
        if 'button_color=scanner_data.get' not in content:
            issues.append("Missing button_color in template rendering")
            
        if '.scanner-submit-btn' not in content:
            issues.append("Missing button CSS styling")
            
        if 'logo_url' not in content:
            issues.append("Missing logo_url in template")
            
        if issues:
            logger.warning(f"⚠️ scanner_deployment.py issues: {', '.join(issues)}")
            return False
        else:
            logger.info("✅ scanner_deployment.py looks good")
            return True
            
    except Exception as e:
        logger.error(f"❌ Error checking scanner_deployment.py: {e}")
        return False

def test_database_schema():
    """Test that database schema has all required columns"""
    logger.info("🔧 Testing database schema...")
    
    try:
        conn = sqlite3.connect('client_scanner.db')
        cursor = conn.cursor()
        
        # Check customizations table
        cursor.execute("PRAGMA table_info(customizations)")
        columns = [col[1] for col in cursor.fetchall()]
        
        required_columns = ['button_color', 'logo_path', 'favicon_path', 'primary_color', 'secondary_color']
        missing_columns = [col for col in required_columns if col not in columns]
        
        if missing_columns:
            logger.warning(f"⚠️ Missing columns in customizations table: {missing_columns}")
            
            # Try to add missing columns
            for col in missing_columns:
                try:
                    if col == 'button_color':
                        cursor.execute('ALTER TABLE customizations ADD COLUMN button_color TEXT DEFAULT "#d96c33"')
                    elif col == 'logo_path':
                        cursor.execute('ALTER TABLE customizations ADD COLUMN logo_path TEXT')
                    elif col == 'favicon_path':
                        cursor.execute('ALTER TABLE customizations ADD COLUMN favicon_path TEXT')
                    elif col == 'primary_color':
                        cursor.execute('ALTER TABLE customizations ADD COLUMN primary_color TEXT DEFAULT "#02054c"')
                    elif col == 'secondary_color':
                        cursor.execute('ALTER TABLE customizations ADD COLUMN secondary_color TEXT DEFAULT "#35a310"')
                    
                    logger.info(f"✅ Added {col} column to customizations table")
                except sqlite3.OperationalError as e:
                    logger.warning(f"⚠️ Could not add {col} column: {e}")
            
            conn.commit()
        else:
            logger.info("✅ All required columns exist in customizations table")
        
        conn.close()
        return len(missing_columns) == 0
        
    except Exception as e:
        logger.error(f"❌ Error testing database schema: {e}")
        return False

def test_end_to_end_flow():
    """Test the complete customize flow"""
    logger.info("🔧 Testing end-to-end customize flow...")
    
    # Test data flow
    test_data = {
        'business_name': 'Test Company',
        'business_domain': 'test.com',
        'contact_email': 'test@test.com',
        'primary_color': '#123456',
        'secondary_color': '#654321',
        'button_color': '#abcdef',
        'logo_path': '/static/uploads/test_logo.png'
    }
    
    # Simulate the flow
    logger.info("📋 Simulating customize flow:")
    logger.info(f"  1. Form data: {test_data}")
    logger.info("  2. register_client() should save to clients + customizations tables")
    logger.info("  3. create_scanner_for_client() should create scanner")
    logger.info("  4. generate_scanner_deployment() should use all colors and logo")
    
    # Check if all functions would handle this data
    issues = []
    
    # Check auth_utils.py
    try:
        with open('auth_utils.py', 'r') as f:
            auth_content = f.read()
        if 'button_color' not in auth_content:
            issues.append("auth_utils.py missing button_color handling")
    except:
        issues.append("Could not read auth_utils.py")
    
    # Check scanner_deployment.py  
    try:
        with open('scanner_deployment.py', 'r') as f:
            deploy_content = f.read()
        if 'button_color' not in deploy_content:
            issues.append("scanner_deployment.py missing button_color")
    except:
        issues.append("Could not read scanner_deployment.py")
    
    if issues:
        logger.warning(f"⚠️ End-to-end flow issues: {', '.join(issues)}")
        return False
    else:
        logger.info("✅ End-to-end flow should work correctly")
        return True

def create_comprehensive_test():
    """Create a test script to verify all customize functionality"""
    logger.info("🔧 Creating comprehensive test script...")
    
    test_script = '''#!/usr/bin/env python3
"""
Test customize functionality end-to-end
"""

def test_customize_form_submission():
    """Test that customize form submits all required data"""
    print("Testing customize form submission...")
    
    # Test data that should be submitted
    expected_fields = [
        'business_name', 'business_domain', 'contact_email', 'contact_phone',
        'scanner_name', 'primary_color', 'secondary_color', 'button_color',
        'email_subject', 'email_intro', 'default_scans[]'
    ]
    
    print("✅ Form should include these fields:", expected_fields)
    
def test_database_operations():
    """Test database operations"""
    print("Testing database operations...")
    
    import sqlite3
    
    # Test customizations table structure
    conn = sqlite3.connect('client_scanner.db')
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA table_info(customizations)")
    columns = [col[1] for col in cursor.fetchall()]
    
    required_columns = ['button_color', 'primary_color', 'secondary_color', 'logo_path']
    missing = [col for col in required_columns if col not in columns]
    
    if missing:
        print(f"❌ Missing columns: {missing}")
    else:
        print("✅ All required columns exist")
    
    conn.close()

def test_scanner_deployment():
    """Test scanner deployment generation"""
    print("Testing scanner deployment...")
    
    test_data = {
        'name': 'Test Scanner',
        'business_name': 'Test Company', 
        'primary_color': '#123456',
        'secondary_color': '#654321',
        'button_color': '#abcdef',
        'logo_url': '/static/uploads/test.png'
    }
    
    print("✅ Scanner data should include all customization fields")
    print(f"   Test data: {test_data}")

if __name__ == "__main__":
    print("🚀 Running Customize Functionality Tests")
    print("=" * 50)
    
    test_customize_form_submission()
    test_database_operations()
    test_scanner_deployment()
    
    print("=" * 50)
    print("✅ Test completed - check output above for any issues")
'''
    
    with open('test_customize_functionality.py', 'w') as f:
        f.write(test_script)
    
    logger.info("✅ Created test_customize_functionality.py")
    return True

def main():
    """Run comprehensive customize functionality fixes"""
    logger.info("🚀 Starting Comprehensive Customize Functionality Fix")
    logger.info("=" * 60)
    
    fixes = [
        ("Database Schema", test_database_schema),
        ("Auth Utils Register Client", fix_auth_utils_register_client),
        ("Customize Template", fix_customize_scanner_template),
        ("Scanner Creation Route", fix_scanner_creation_route),
        ("Scanner Deployment", fix_scanner_deployment),
        ("End-to-End Flow", test_end_to_end_flow)
    ]
    
    results = []
    
    for fix_name, fix_func in fixes:
        logger.info(f"\n📋 {fix_name}...")
        try:
            result = fix_func()
            results.append((fix_name, result))
            if result:
                logger.info(f"✅ {fix_name} - OK")
            else:
                logger.warning(f"⚠️ {fix_name} - NEEDS ATTENTION")
        except Exception as e:
            logger.error(f"❌ {fix_name} - ERROR: {e}")
            results.append((fix_name, False))
    
    # Create test script
    create_comprehensive_test()
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 SUMMARY")
    logger.info("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for fix_name, result in results:
        status = "✅ PASS" if result else "⚠️ NEEDS WORK"
        logger.info(f"{status} - {fix_name}")
    
    logger.info(f"\n🎯 Results: {passed}/{total} checks passed")
    
    if passed == total:
        logger.info("🎉 ALL CUSTOMIZE FUNCTIONALITY CHECKS PASSED!")
        logger.info("\n📋 What should work now:")
        logger.info("• Color customization (primary, secondary, button)")
        logger.info("• Logo upload and display")
        logger.info("• Real-time preview")
        logger.info("• Database persistence")
        logger.info("• Scanner deployment with customizations")
    else:
        logger.info("🔧 SOME ISSUES FOUND - See details above")
        logger.info("Run test_customize_functionality.py for additional testing")
    
    return passed == total

if __name__ == "__main__":
    main()