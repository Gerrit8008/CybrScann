#!/usr/bin/env python3
"""
Fix any remaining route conflicts in the modular structure
"""

import os
import re

def fix_template_urls():
    """Fix url_for references in templates"""
    print("🔧 Fixing template URL references...")
    
    # Common URL fixes
    url_fixes = {
        "url_for('index')": "url_for('main.landing_page')",
        "url_for('landing_page')": "url_for('main.landing_page')",
        "url_for('scan')": "url_for('scan.scan_page')",
        "url_for('results')": "url_for('scan.results')", 
        "url_for('admin')": "url_for('admin.admin_dashboard')",
        "url_for('admin_dashboard')": "url_for('admin.admin_dashboard')",
        "url_for('pricing')": "url_for('main.pricing')",
        "url_for('about')": "url_for('main.about')",
        "url_for('contact')": "url_for('main.contact')",
        "url_for('health')": "url_for('main.health_check')",
    }
    
    templates_dir = 'templates'
    fixed_files = []
    
    for root, dirs, files in os.walk(templates_dir):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    original_content = content
                    
                    # Apply fixes
                    for old_url, new_url in url_fixes.items():
                        content = content.replace(old_url, new_url)
                    
                    # Save if changed
                    if content != original_content:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        fixed_files.append(file_path)
                        
                except Exception as e:
                    print(f"⚠️ Error processing {file_path}: {e}")
    
    if fixed_files:
        print(f"✅ Fixed URL references in {len(fixed_files)} template files:")
        for file in fixed_files:
            print(f"   📄 {file}")
    else:
        print("✅ No template files needed URL fixes")

def test_app_import():
    """Test that the app can be imported successfully"""
    print("🧪 Testing app import...")
    
    try:
        import importlib.util
        import sys
        
        # Test import
        spec = importlib.util.spec_from_file_location("app", "app.py")
        app_module = importlib.util.module_from_spec(spec)
        
        # Try to execute the module
        spec.loader.exec_module(app_module)
        
        print("✅ App imports and initializes successfully")
        
        # Test that we can get the app instance
        if hasattr(app_module, 'app'):
            app = app_module.app
            print(f"✅ Flask app created: {app}")
            
            # Test route registration
            routes = [str(rule) for rule in app.url_map.iter_rules()]
            print(f"✅ {len(routes)} routes registered")
            
            return True
        else:
            print("❌ No 'app' attribute found in module")
            return False
            
    except Exception as e:
        print(f"❌ App import failed: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

def main():
    """Run all fixes"""
    print("🚀 Fixing modular route issues...")
    
    # Fix templates
    fix_template_urls()
    
    # Test app
    success = test_app_import()
    
    if success:
        print("\n🎉 All fixes applied successfully!")
        print("✅ Modular structure is working correctly")
        print("\n📝 Summary:")
        print("  🔹 Template URL references updated")
        print("  🔹 App imports and initializes properly") 
        print("  🔹 All routes registered successfully")
        print("\n🚀 You can now run: python3 app.py")
    else:
        print("\n❌ Some issues remain. Check the error messages above.")
    
    return success

if __name__ == '__main__':
    main()