#!/usr/bin/env python3
"""
Favicon Implementation Test
===========================
This script verifies that favicons are correctly implemented across all templates.
"""

import os
import re
from datetime import datetime

def check_favicon_file():
    """Check if favicon file exists and get details"""
    print("🔍 Checking Favicon File")
    print("=" * 30)
    
    favicon_path = "static/images/favicon.png.png"
    
    if os.path.exists(favicon_path):
        file_size = os.path.getsize(favicon_path)
        print(f"✅ Favicon file exists: {favicon_path}")
        print(f"📄 File size: {file_size:,} bytes")
        
        # Check if file size is reasonable for a favicon
        if file_size > 1024 * 100:  # > 100KB
            print(f"⚠️  Large file size ({file_size:,} bytes) - consider optimizing")
        elif file_size < 100:  # < 100 bytes
            print(f"⚠️  Very small file size ({file_size:,} bytes) - check if file is valid")
        else:
            print(f"✅ File size looks good")
        
        return True
    else:
        print(f"❌ Favicon file not found: {favicon_path}")
        return False

def check_template_favicon(file_path):
    """Check if a template has favicon implementation"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if it's a full HTML document
        if not re.search(r'<html[^>]*>', content, re.IGNORECASE):
            return "⏭️  Partial template (no <html> tag)"
        
        # Check if it has a <head> section
        if not re.search(r'<head[^>]*>', content, re.IGNORECASE):
            return "⏭️  No <head> section"
        
        # Check for favicon links
        favicon_patterns = [
            r'<link[^>]*rel=["\']icon["\'][^>]*>',
            r'<link[^>]*rel=["\']shortcut icon["\'][^>]*>',
            r'favicon\.png\.png'
        ]
        
        favicon_found = any(re.search(pattern, content, re.IGNORECASE) for pattern in favicon_patterns)
        
        if favicon_found:
            # Count favicon links
            favicon_links = len(re.findall(r'<link[^>]*favicon[^>]*>', content, re.IGNORECASE))
            icon_links = len(re.findall(r'<link[^>]*rel=["\']icon["\'][^>]*>', content, re.IGNORECASE))
            shortcut_links = len(re.findall(r'<link[^>]*rel=["\']shortcut icon["\'][^>]*>', content, re.IGNORECASE))
            
            total_links = favicon_links + icon_links + shortcut_links
            return f"✅ Favicon implemented ({total_links} links)"
        else:
            return "❌ No favicon links found"
            
    except Exception as e:
        return f"❌ Error reading file: {str(e)}"

def find_all_html_templates():
    """Find all HTML templates that should have favicons"""
    html_files = []
    
    # Main templates directory
    templates_dir = "templates"
    if os.path.exists(templates_dir):
        for root, dirs, files in os.walk(templates_dir):
            for file in files:
                if file.endswith('.html'):
                    html_files.append(os.path.join(root, file))
    
    # Scanner deployment templates
    static_dir = "static/deployments"
    if os.path.exists(static_dir):
        for root, dirs, files in os.walk(static_dir):
            for file in files:
                if file.endswith('.html') and file != 'embed-snippet.html':  # Skip embed snippets
                    html_files.append(os.path.join(root, file))
    
    # Root HTML files
    for file in os.listdir('.'):
        if file.endswith('.html') and not file.startswith('test_'):
            html_files.append(file)
    
    return sorted(html_files)

def generate_favicon_report():
    """Generate a comprehensive favicon implementation report"""
    print("\n📊 Favicon Implementation Report")
    print("=" * 50)
    
    html_files = find_all_html_templates()
    
    results = {
        'implemented': [],
        'missing': [],
        'partial': [],
        'errors': []
    }
    
    for file_path in html_files:
        result = check_template_favicon(file_path)
        
        if result.startswith("✅"):
            results['implemented'].append((file_path, result))
        elif result.startswith("❌"):
            results['missing'].append((file_path, result))
        elif result.startswith("⏭️"):
            results['partial'].append((file_path, result))
        else:
            results['errors'].append((file_path, result))
        
        print(f"{result}: {file_path}")
    
    return results

def show_summary(results):
    """Show summary statistics"""
    print(f"\n📈 Summary Statistics")
    print("=" * 30)
    
    implemented = len(results['implemented'])
    missing = len(results['missing'])
    partial = len(results['partial'])
    errors = len(results['errors'])
    total = implemented + missing + partial + errors
    
    print(f"✅ Favicon implemented: {implemented}")
    print(f"❌ Missing favicon: {missing}")
    print(f"⏭️  Partial/Skip: {partial}")
    print(f"🔧 Errors: {errors}")
    print(f"📁 Total files: {total}")
    
    if implemented > 0:
        coverage = (implemented / (implemented + missing)) * 100 if (implemented + missing) > 0 else 100
        print(f"📊 Coverage: {coverage:.1f}%")
    
    return implemented, missing, partial, errors

def show_next_steps(missing_count):
    """Show next steps if there are missing favicons"""
    if missing_count > 0:
        print(f"\n🔧 Next Steps")
        print("=" * 30)
        print("To add favicon to missing templates:")
        print("1. Run: python3 add_favicon_to_templates.py")
        print("2. Or manually add these lines to <head> section:")
        print('   <link rel="icon" type="image/png" sizes="32x32" href="/static/images/favicon.png.png">')
        print('   <link rel="icon" type="image/png" sizes="16x16" href="/static/images/favicon.png.png">')
        print('   <link rel="shortcut icon" href="/static/images/favicon.png.png">')
    else:
        print(f"\n🎉 All Applicable Templates Have Favicons!")
        print("=" * 40)
        print("✅ Favicon implementation is complete")
        print("💡 Favicons will appear in browser tabs")
        print("🔧 Test by starting the app: python3 app.py")

def main():
    """Main testing function"""
    print("🔍 CybrScan Favicon Implementation Test")
    print("=" * 50)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Check favicon file
    favicon_exists = check_favicon_file()
    
    if not favicon_exists:
        print("\n❌ Cannot test implementation without favicon file")
        return
    
    # Check all templates
    results = generate_favicon_report()
    
    # Show summary
    implemented, missing, partial, errors = show_summary(results)
    
    # Show next steps
    show_next_steps(missing)
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")