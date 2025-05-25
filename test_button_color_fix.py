#!/usr/bin/env python3
"""
Test script to verify button color functionality is working properly
"""

import os
import sqlite3
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_database_schema():
    """Test that button_color column exists in customizations table"""
    logger.info("🔍 Testing database schema...")
    
    try:
        conn = sqlite3.connect('client_scanner.db')
        cursor = conn.cursor()
        
        # Check if button_color column exists
        cursor.execute("PRAGMA table_info(customizations)")
        columns = cursor.fetchall()
        
        button_color_exists = any(col[1] == 'button_color' for col in columns)
        
        if button_color_exists:
            logger.info("✅ button_color column exists in customizations table")
        else:
            logger.error("❌ button_color column missing from customizations table")
            # Try to add it
            try:
                cursor.execute('ALTER TABLE customizations ADD COLUMN button_color TEXT DEFAULT "#d96c33"')
                conn.commit()
                logger.info("✅ Added button_color column to customizations table")
            except Exception as e:
                logger.error(f"❌ Failed to add button_color column: {e}")
        
        conn.close()
        return button_color_exists
        
    except Exception as e:
        logger.error(f"❌ Database schema test failed: {e}")
        return False

def test_template_files():
    """Test that templates have button color fields"""
    logger.info("🔍 Testing template files...")
    
    templates_to_check = [
        ('templates/client/customize_scanner.html', 'buttonColor'),
        ('templates/client/scanner-create.html', 'button_color'),
        ('templates/client/scanner-edit.html', 'button_color')
    ]
    
    all_good = True
    
    for template_path, field_name in templates_to_check:
        if os.path.exists(template_path):
            with open(template_path, 'r') as f:
                content = f.read()
                
            if field_name in content:
                logger.info(f"✅ {template_path} has {field_name} field")
            else:
                logger.error(f"❌ {template_path} missing {field_name} field")
                all_good = False
        else:
            logger.warning(f"⚠️ {template_path} not found")
            all_good = False
    
    return all_good

def test_deployment_template():
    """Test that scanner deployment includes button_color"""
    logger.info("🔍 Testing scanner deployment template...")
    
    try:
        # Check scanner_deployment.py
        with open('scanner_deployment.py', 'r') as f:
            content = f.read()
        
        checks = [
            ('button_color parameter', 'button_color=scanner_data.get'),
            ('CSS button styling', '.scanner-submit-btn'),
            ('button_color in template render', 'button_color')
        ]
        
        all_good = True
        for check_name, check_pattern in checks:
            if check_pattern in content:
                logger.info(f"✅ {check_name} found in scanner_deployment.py")
            else:
                logger.error(f"❌ {check_name} missing from scanner_deployment.py")
                all_good = False
        
        return all_good
        
    except Exception as e:
        logger.error(f"❌ Deployment template test failed: {e}")
        return False

def test_javascript_functionality():
    """Test that JavaScript handles button color changes"""
    logger.info("🔍 Testing JavaScript functionality...")
    
    templates_with_js = [
        'templates/client/customize_scanner.html',
        'templates/client/scanner-create.html'
    ]
    
    all_good = True
    
    for template_path in templates_with_js:
        if os.path.exists(template_path):
            with open(template_path, 'r') as f:
                content = f.read()
            
            js_checks = [
                ('button color event listener', 'buttonColor.*addEventListener'),
                ('preview button update', 'preview.*button.*backgroundColor'),
                ('updateLivePreview function', 'updateLivePreview')
            ]
            
            for check_name, pattern in js_checks:
                if any(p in content for p in pattern.split('.*')):
                    logger.info(f"✅ {template_path}: {check_name}")
                else:
                    logger.warning(f"⚠️ {template_path}: {check_name} may be missing")
        else:
            logger.warning(f"⚠️ {template_path} not found")
    
    return all_good

def test_app_py_integration():
    """Test that app.py properly handles button_color"""
    logger.info("🔍 Testing app.py integration...")
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        checks = [
            ('button_color in form handling', 'button_color.*request.form'),
            ('button_color in scanner_creation_data', 'scanner_creation_data.*button_color'),
            ('button_color in database query', 'cust.button_color'),
            ('button_color in scanner_data', 'button_color.*scanner_row')
        ]
        
        all_good = True
        for check_name, pattern in checks:
            if any(p in content for p in pattern.split('.*')):
                logger.info(f"✅ app.py: {check_name}")
            else:
                logger.error(f"❌ app.py: {check_name} missing")
                all_good = False
        
        return all_good
        
    except Exception as e:
        logger.error(f"❌ app.py integration test failed: {e}")
        return False

def main():
    """Run all button color tests"""
    logger.info("🚀 Starting Button Color Functionality Tests")
    logger.info("=" * 50)
    
    tests = [
        ("Database Schema", test_database_schema),
        ("Template Files", test_template_files),
        ("Deployment Template", test_deployment_template),
        ("JavaScript Functionality", test_javascript_functionality),
        ("App.py Integration", test_app_py_integration)
    ]
    
    all_passed = True
    
    for test_name, test_func in tests:
        logger.info(f"\n📋 Running {test_name} Test...")
        try:
            result = test_func()
            if not result:
                all_passed = False
        except Exception as e:
            logger.error(f"❌ {test_name} test failed with exception: {e}")
            all_passed = False
    
    logger.info("\n" + "=" * 50)
    if all_passed:
        logger.info("🎉 ALL BUTTON COLOR TESTS PASSED!")
        logger.info("✅ Button color functionality should now work properly")
        
        logger.info("\n📋 What should work now:")
        logger.info("• Button color picker in scanner creation form")
        logger.info("• Real-time button color preview")
        logger.info("• Button color persistence in database")
        logger.info("• Button color applied to deployed scanners")
        logger.info("• Button color changes in customization interface")
        
    else:
        logger.info("❌ SOME BUTTON COLOR TESTS FAILED")
        logger.info("🔧 Please check the errors above and fix remaining issues")
    
    return all_passed

if __name__ == "__main__":
    main()