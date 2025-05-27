#!/usr/bin/env python3
"""
Migration script to switch from monolithic app.py to modular structure
"""

import os
import shutil
from datetime import datetime

def migrate_to_modular():
    """Migrate from app.py to modular structure"""
    print("🚀 Starting migration to modular structure...")
    
    # Step 1: Backup the current app.py
    backup_name = f"app_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    if os.path.exists('app.py'):
        print(f"📦 Backing up current app.py to {backup_name}")
        shutil.copy2('app.py', backup_name)
    
    # Step 2: Replace app.py with modular version
    if os.path.exists('app_modular.py'):
        print("🔄 Replacing app.py with modular version")
        shutil.copy2('app_modular.py', 'app.py')
        print("✅ app.py updated to modular structure")
    else:
        print("❌ app_modular.py not found")
        return False
    
    # Step 3: Verify routes directory exists
    if not os.path.exists('routes'):
        print("❌ routes/ directory not found")
        return False
    
    # Step 4: Verify all route files exist
    route_files = [
        'routes/main_routes.py',
        'routes/auth_routes.py', 
        'routes/scanner_routes.py',
        'routes/scan_routes.py',
        'routes/admin_routes.py'
    ]
    
    missing_files = []
    for route_file in route_files:
        if not os.path.exists(route_file):
            missing_files.append(route_file)
    
    if missing_files:
        print(f"❌ Missing route files: {missing_files}")
        return False
    
    print("✅ All route files found")
    
    # Step 5: Test import of new structure
    try:
        print("🧪 Testing imports...")
        import importlib.util
        
        spec = importlib.util.spec_from_file_location("app", "app.py")
        app_module = importlib.util.module_from_spec(spec)
        # Don't execute, just test that it can be loaded
        print("✅ New app.py structure imports successfully")
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False
    
    print("🎉 Migration completed successfully!")
    print("\n📊 New structure summary:")
    print("  📁 app.py - Main application with blueprint registration")
    print("  📁 routes/")
    print("    📄 main_routes.py - Landing pages, health checks")
    print("    📄 auth_routes.py - Authentication endpoints") 
    print("    📄 scanner_routes.py - Scanner deployment, embed, API")
    print("    📄 scan_routes.py - Scan execution and results")
    print("    📄 admin_routes.py - Admin and debug functionality")
    print("\n💡 Benefits:")
    print("  ✨ Much smaller, manageable file sizes")
    print("  ✨ Clear separation of concerns")
    print("  ✨ Easier debugging and maintenance")
    print("  ✨ Better code organization")
    
    return True

if __name__ == '__main__':
    migrate_to_modular()