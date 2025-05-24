#!/usr/bin/env python3
"""
Landing Page Test
================
Simple test to verify the new landing page works correctly.
"""

import os
import sys
from datetime import datetime

def test_template_exists():
    """Test if the landing page template exists"""
    print("🔍 Testing Landing Page Setup")
    print("=" * 40)
    
    # Check if logo file exists
    logo_path = "static/images/logo.png"
    if os.path.exists(logo_path):
        print("✅ Logo file exists")
    else:
        print("❌ Logo file not found")
        return False
    
    template_path = "templates/index.html"
    
    if os.path.exists(template_path):
        print("✅ Landing page template exists")
        
        # Check file size
        file_size = os.path.getsize(template_path)
        print(f"📄 Template size: {file_size:,} bytes")
        
        # Check for key content
        try:
            with open(template_path, 'r') as f:
                content = f.read()
            
            checks = [
                ("CybrScan brand name", "CybrScan" in content),
                ("Logo implementation", "/static/images/logo.png" in content),
                ("Favicon implementation", "favicon" in content.lower()),
                ("Primary color", "#02054c" in content),
                ("Secondary color", "#61c608" in content),
                ("Client login link", "/auth/login?type=client" in content),
                ("Admin login link", "/auth/login?type=admin" in content),
                ("Free scan CTA", "/scan" in content),
                ("Bootstrap CSS", "bootstrap" in content),
                ("Bootstrap Icons", "bootstrap-icons" in content),
                ("Responsive design", "viewport" in content),
                ("Modern features", "Inter" in content)  # Google Fonts
            ]
            
            all_passed = True
            for check_name, passed in checks:
                status = "✅" if passed else "❌"
                print(f"{status} {check_name}")
                if not passed:
                    all_passed = False
            
            return all_passed
            
        except Exception as e:
            print(f"❌ Error reading template: {e}")
            return False
    else:
        print("❌ Landing page template not found")
        return False

def test_app_route():
    """Test if the app route is configured"""
    print("\n🔍 Testing App Route Configuration")
    print("=" * 40)
    
    app_path = "app.py"
    
    if os.path.exists(app_path):
        try:
            with open(app_path, 'r') as f:
                content = f.read()
            
            checks = [
                ("Root route defined", "@app.route('/')" in content),
                ("Index function", "def index():" in content),
                ("Template rendering", "render_template('index.html')" in content)
            ]
            
            all_passed = True
            for check_name, passed in checks:
                status = "✅" if passed else "❌"
                print(f"{status} {check_name}")
                if not passed:
                    all_passed = False
            
            return all_passed
            
        except Exception as e:
            print(f"❌ Error reading app.py: {e}")
            return False
    else:
        print("❌ app.py not found")
        return False

def test_color_scheme():
    """Test if the color scheme is correctly implemented"""
    print("\n🎨 Testing Color Scheme")
    print("=" * 40)
    
    expected_colors = {
        "Primary (Dark Blue)": "#02054c",
        "Secondary (Green)": "#61c608"
    }
    
    template_path = "templates/index.html"
    css_path = "static/css/styles.css"
    
    files_to_check = []
    if os.path.exists(template_path):
        files_to_check.append(("Landing Page", template_path))
    if os.path.exists(css_path):
        files_to_check.append(("CSS Styles", css_path))
    
    all_passed = True
    
    for file_name, file_path in files_to_check:
        print(f"\n📄 Checking {file_name}:")
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            for color_name, color_code in expected_colors.items():
                if color_code in content:
                    print(f"  ✅ {color_name}: {color_code}")
                else:
                    print(f"  ❌ {color_name}: {color_code} not found")
                    all_passed = False
                    
        except Exception as e:
            print(f"  ❌ Error reading {file_path}: {e}")
            all_passed = False
    
    return all_passed

def test_responsive_features():
    """Test if responsive and modern features are present"""
    print("\n📱 Testing Modern Features")
    print("=" * 40)
    
    template_path = "templates/index.html"
    
    if not os.path.exists(template_path):
        print("❌ Template not found for testing")
        return False
    
    try:
        with open(template_path, 'r') as f:
            content = f.read()
        
        modern_features = [
            ("Responsive viewport", 'name="viewport"'),
            ("CSS Grid/Flexbox", 'display: flex'),
            ("Modern animations", 'transition:'),
            ("CSS variables", '--primary-color'),
            ("Bootstrap 5", 'bootstrap@5.3'),
            ("Modern icons", 'bootstrap-icons'),
            ("Google Fonts", 'fonts.googleapis.com'),
            ("Semantic HTML5", '<section'),
            ("ARIA accessibility", 'aria-'),
            ("Modern JS", 'addEventListener')
        ]
        
        all_passed = True
        for feature_name, pattern in modern_features:
            if pattern in content:
                print(f"✅ {feature_name}")
            else:
                print(f"❌ {feature_name}")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Error testing features: {e}")
        return False

def show_next_steps():
    """Show next steps for using the landing page"""
    print("\n🚀 Next Steps")
    print("=" * 40)
    print("""
✅ Landing page is ready!

🔧 To start the application:
   python3 app.py

🌐 To view the landing page:
   http://localhost:5000/

📝 Landing page features:
   • Modern, responsive design
   • CybrScan branding with specified colors
   • Client and Admin login sections
   • Free scan call-to-action
   • Feature showcase
   • Statistics section
   • Professional footer

🎨 Color scheme:
   • Primary: #02054c (Dark Blue)
   • Secondary: #61c608 (Green)

🔗 Login links:
   • Client: /auth/login?type=client
   • Admin: /auth/login?type=admin
   • Free scan: /scan
""")

def main():
    """Main test function"""
    print("🎨 CybrScan Landing Page Verification")
    print("=" * 50)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    tests = [
        ("Template Exists", test_template_exists),
        ("App Route", test_app_route),
        ("Color Scheme", test_color_scheme),
        ("Modern Features", test_responsive_features)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ Error in {test_name}: {e}")
            results[test_name] = False
    
    # Summary
    print(f"\n📊 Test Summary")
    print("=" * 30)
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print(f"\n🎉 All tests passed! Landing page is ready.")
        show_next_steps()
    else:
        print(f"\n⚠️  Some tests failed. Check the issues above.")
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")