#!/usr/bin/env python3
"""
Favicon Optimization Script
============================
This script provides recommendations for optimizing the favicon file.
"""

import os
from datetime import datetime

def analyze_favicon():
    """Analyze the current favicon file"""
    print("🔍 Favicon Analysis")
    print("=" * 30)
    
    favicon_path = "static/images/favicon.png.png"
    
    if not os.path.exists(favicon_path):
        print("❌ Favicon file not found")
        return False
    
    file_size = os.path.getsize(favicon_path)
    print(f"📄 Current file: {favicon_path}")
    print(f"📊 Current size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
    
    # Analyze size
    if file_size > 50 * 1024:  # > 50KB
        print("⚠️  File is quite large for a favicon")
        print("💡 Recommended: < 50KB for web performance")
    elif file_size > 10 * 1024:  # > 10KB
        print("⚠️  File is moderately large")
        print("💡 Recommended: < 10KB for optimal performance")
    else:
        print("✅ File size is good for web performance")
    
    return True

def provide_optimization_recommendations():
    """Provide favicon optimization recommendations"""
    print("\n🛠️  Favicon Optimization Recommendations")
    print("=" * 50)
    
    print("""
📐 SIZE RECOMMENDATIONS:
   • 16x16 pixels: Essential for browser tabs
   • 32x32 pixels: High-DPI displays
   • 48x48 pixels: Windows taskbar
   • 64x64 pixels: High-quality display

📊 FILE SIZE RECOMMENDATIONS:
   • Target: < 10KB for optimal performance
   • Maximum: < 50KB for acceptable performance
   • Use PNG format for transparency support
   • Use ICO format for maximum compatibility

🔧 OPTIMIZATION METHODS:

1. IMAGE COMPRESSION:
   • Use online tools like TinyPNG, ImageOptim
   • Reduce color palette if possible
   • Remove unnecessary metadata

2. MULTIPLE FORMATS:
   • Create .ico file for older browsers
   • Keep .png for modern browsers
   • Generate different sizes (16x16, 32x32)

3. MANUAL OPTIMIZATION:
   • Open in image editor (GIMP, Photoshop)
   • Resize to 32x32 or 16x16 pixels
   • Save as PNG with compression
   • Export as ICO for compatibility

🌐 ONLINE TOOLS:
   • favicon.io - Generate favicon from image/text
   • TinyPNG.com - Compress PNG files
   • ImageOptim.com - Optimize images
   • RealFaviconGenerator.net - Generate all sizes

📁 RECOMMENDED FILE STRUCTURE:
   static/images/
   ├── favicon.ico        # 16x16, 32x32 (multi-size ICO)
   ├── favicon-16x16.png  # 16x16 PNG
   ├── favicon-32x32.png  # 32x32 PNG
   └── apple-touch-icon.png # 180x180 for iOS

💻 OPTIMIZATION COMMANDS:
   # If you have ImageMagick installed:
   convert favicon.png.png -resize 32x32 favicon-32x32.png
   convert favicon.png.png -resize 16x16 favicon-16x16.png
   
   # If you have OptiPNG installed:
   optipng -o7 favicon-32x32.png
   optipng -o7 favicon-16x16.png
""")

def suggest_favicon_html_update():
    """Suggest updated HTML for optimized favicons"""
    print("\n🔧 Suggested HTML Update")
    print("=" * 30)
    
    print("""
<!-- Optimized Favicon Implementation -->
<link rel="icon" type="image/x-icon" href="/static/images/favicon.ico">
<link rel="icon" type="image/png" sizes="32x32" href="/static/images/favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="/static/images/favicon-16x16.png">
<link rel="apple-touch-icon" sizes="180x180" href="/static/images/apple-touch-icon.png">
<meta name="theme-color" content="#02054c">
""")

def check_for_optimization_tools():
    """Check if optimization tools are available"""
    print("\n🔍 Available Optimization Tools")
    print("=" * 35)
    
    tools = [
        ("ImageMagick", "convert --version"),
        ("OptiPNG", "optipng --version"),
        ("Python PIL", "python3 -c 'from PIL import Image; print(\"Available\")'")
    ]
    
    for tool_name, check_command in tools:
        try:
            import subprocess
            result = subprocess.run(check_command.split(), 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=5)
            if result.returncode == 0:
                print(f"✅ {tool_name}: Available")
            else:
                print(f"❌ {tool_name}: Not available")
        except:
            print(f"❌ {tool_name}: Not available")

def main():
    """Main optimization analysis"""
    print("🎯 CybrScan Favicon Optimization")
    print("=" * 50)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Analyze current favicon
    if not analyze_favicon():
        return
    
    # Provide recommendations
    provide_optimization_recommendations()
    
    # Check available tools
    check_for_optimization_tools()
    
    # Suggest HTML updates
    suggest_favicon_html_update()
    
    print(f"\n📝 NEXT STEPS:")
    print("=" * 20)
    print("1. Create optimized favicon files using recommended tools")
    print("2. Replace current favicon.png.png with optimized versions")
    print("3. Update HTML templates with optimized favicon links")
    print("4. Test favicon display in different browsers")
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Analysis interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")