#!/usr/bin/env python3
"""
Add Favicon to All HTML Templates
==================================
This script adds favicon links to all HTML templates in the project.
"""

import os
import re
from datetime import datetime

def get_favicon_html():
    """Generate the favicon HTML snippet"""
    return '''    <!-- Favicon -->
    <link rel="icon" type="image/png" sizes="32x32" href="/static/images/favicon.png.png">
    <link rel="icon" type="image/png" sizes="16x16" href="/static/images/favicon.png.png">
    <link rel="shortcut icon" href="/static/images/favicon.png.png">'''

def add_favicon_to_file(file_path):
    """Add favicon to a single HTML file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if favicon is already present
        if 'favicon' in content.lower() or 'shortcut icon' in content.lower():
            return f"⏭️  {file_path}: Favicon already present"
        
        # Find the <head> section and add favicon after <title> or <meta> tags
        favicon_html = get_favicon_html()
        
        # Pattern to match after title tag or last meta tag in head
        patterns = [
            (r'(<title>.*?</title>)', r'\1\n' + favicon_html),
            (r'(<meta[^>]*>)(?=\s*<link)', r'\1\n' + favicon_html),
            (r'(<meta[^>]*>)(?=\s*<style)', r'\1\n' + favicon_html),
            (r'(<meta[^>]*viewport[^>]*>)', r'\1\n' + favicon_html),
        ]
        
        updated = False
        for pattern, replacement in patterns:
            if re.search(pattern, content, re.IGNORECASE | re.DOTALL):
                content = re.sub(pattern, replacement, content, count=1, flags=re.IGNORECASE | re.DOTALL)
                updated = True
                break
        
        # Fallback: add after <head> tag
        if not updated:
            head_pattern = r'(<head[^>]*>)'
            if re.search(head_pattern, content, re.IGNORECASE):
                content = re.sub(head_pattern, r'\1\n' + favicon_html, content, count=1, flags=re.IGNORECASE)
                updated = True
        
        if updated:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"✅ {file_path}: Favicon added successfully"
        else:
            return f"❌ {file_path}: Could not find suitable location for favicon"
            
    except Exception as e:
        return f"❌ {file_path}: Error - {str(e)}"

def find_html_templates():
    """Find all HTML templates in the project"""
    html_files = []
    
    # Search in templates directory
    templates_dir = "templates"
    if os.path.exists(templates_dir):
        for root, dirs, files in os.walk(templates_dir):
            for file in files:
                if file.endswith('.html'):
                    html_files.append(os.path.join(root, file))
    
    # Search in static deployments (scanner templates)
    static_dir = "static/deployments"
    if os.path.exists(static_dir):
        for root, dirs, files in os.walk(static_dir):
            for file in files:
                if file.endswith('.html'):
                    html_files.append(os.path.join(root, file))
    
    # Search for any other HTML files in root
    for file in os.listdir('.'):
        if file.endswith('.html'):
            html_files.append(file)
    
    return sorted(html_files)

def verify_favicon_file():
    """Verify that the favicon file exists"""
    favicon_path = "static/images/favicon.png.png"
    if os.path.exists(favicon_path):
        file_size = os.path.getsize(favicon_path)
        return True, f"✅ Favicon file exists ({file_size:,} bytes)"
    else:
        return False, "❌ Favicon file not found at static/images/favicon.png.png"

def main():
    """Main function to add favicon to all templates"""
    print("🎯 Adding Favicon to All HTML Templates")
    print("=" * 50)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Verify favicon file exists
    favicon_exists, favicon_message = verify_favicon_file()
    print("🔍 Checking Favicon File")
    print("-" * 30)
    print(favicon_message)
    
    if not favicon_exists:
        print("\n❌ Cannot proceed without favicon file. Please ensure favicon.png.png exists in static/images/")
        return
    
    # Find all HTML files
    print("\n🔍 Finding HTML Templates")
    print("-" * 30)
    html_files = find_html_templates()
    print(f"Found {len(html_files)} HTML files")
    
    if not html_files:
        print("❌ No HTML files found")
        return
    
    # Process each file
    print("\n🔧 Adding Favicon to Templates")
    print("-" * 30)
    
    results = []
    for file_path in html_files:
        result = add_favicon_to_file(file_path)
        results.append(result)
        print(result)
    
    # Summary
    print(f"\n📊 Summary")
    print("=" * 30)
    
    success_count = len([r for r in results if r.startswith("✅")])
    skip_count = len([r for r in results if r.startswith("⏭️")])
    error_count = len([r for r in results if r.startswith("❌")])
    
    print(f"✅ Successfully updated: {success_count}")
    print(f"⏭️  Already had favicon: {skip_count}")
    print(f"❌ Errors: {error_count}")
    print(f"📁 Total files processed: {len(results)}")
    
    if success_count > 0:
        print(f"\n🎉 Favicon successfully added to {success_count} templates!")
        print("💡 The favicon will now appear in browser tabs for all pages")
    
    if error_count > 0:
        print(f"\n⚠️  {error_count} files had errors - check the output above")
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Process interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")