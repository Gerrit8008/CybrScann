#!/usr/bin/env python3
"""
Check for duplicate routes in app.py
"""

import re

def check_for_duplicate_routes():
    """Check for duplicate @app.route definitions"""
    print("🔍 Checking for duplicate routes in app.py...")
    
    with open('/home/ggrun/CybrScan_1/app.py', 'r') as f:
        content = f.read()
    
    # Find all @app.route definitions
    route_pattern = r'@app\.route\([\'"]([^\'"]+)[\'"]'
    routes = re.findall(route_pattern, content)
    
    print(f"📊 Found {len(routes)} @app.route definitions:")
    
    route_counts = {}
    for route in routes:
        route_counts[route] = route_counts.get(route, 0) + 1
    
    duplicates_found = False
    for route, count in route_counts.items():
        if count > 1:
            print(f"❌ DUPLICATE: {route} appears {count} times")
            duplicates_found = True
        else:
            print(f"✅ {route}")
    
    if not duplicates_found:
        print("\n🎉 No duplicate routes found!")
        return True
    else:
        print(f"\n⚠️  Found {sum(1 for c in route_counts.values() if c > 1)} duplicate routes")
        return False

if __name__ == '__main__':
    check_for_duplicate_routes()