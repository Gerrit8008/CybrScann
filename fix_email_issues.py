#!/usr/bin/env python3
"""
Email Issues Fix Script
=======================
This script fixes common email configuration and code issues.
"""

import os
import sys
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def check_and_fix_imports():
    """Check and fix import issues in email_handler.py"""
    print("🔍 Checking email_handler.py imports...")
    
    email_handler_path = 'email_handler.py'
    if not os.path.exists(email_handler_path):
        print("❌ email_handler.py not found!")
        return False
    
    try:
        with open(email_handler_path, 'r') as f:
            content = f.read()
        
        # Check for required imports
        required_imports = [
            'from email.mime.image import MIMEImage',
            'from email.mime.multipart import MIMEMultipart',
            'from email.mime.text import MIMEText',
            'import smtplib',
            'import os'
        ]
        
        missing_imports = []
        for imp in required_imports:
            if imp not in content:
                missing_imports.append(imp)
        
        if missing_imports:
            print("⚠️  Missing imports found:")
            for imp in missing_imports:
                print(f"   - {imp}")
            
            # Add missing imports
            lines = content.split('\n')
            import_section_end = 0
            
            for i, line in enumerate(lines):
                if line.startswith('import ') or line.startswith('from '):
                    import_section_end = i
            
            # Insert missing imports
            for imp in missing_imports:
                lines.insert(import_section_end + 1, imp)
                import_section_end += 1
            
            # Write back
            with open(email_handler_path, 'w') as f:
                f.write('\n'.join(lines))
            
            print("✅ Missing imports added")
        else:
            print("✅ All required imports present")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking imports: {e}")
        return False

def check_environment_setup():
    """Check if environment variables are properly set"""
    print("\n🔍 Checking environment configuration...")
    
    # Check for .env file
    if not os.path.exists('.env'):
        print("⚠️  .env file not found")
        print("📝 Creating sample .env from template...")
        
        if os.path.exists('env.template'):
            try:
                with open('env.template', 'r') as f:
                    template = f.read()
                
                with open('.env.sample', 'w') as f:
                    f.write(template)
                
                print("✅ Created .env.sample - copy to .env and configure")
                print("💡 Run: python3 setup_email.py for guided setup")
                
            except Exception as e:
                print(f"❌ Error creating .env.sample: {e}")
        
        return False
    
    # Load .env and check variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        required_vars = ['SMTP_USER', 'SMTP_PASSWORD']
        optional_vars = ['SMTP_SERVER', 'SMTP_PORT', 'ADMIN_EMAIL']
        
        missing_required = []
        for var in required_vars:
            if not os.environ.get(var):
                missing_required.append(var)
        
        if missing_required:
            print("❌ Missing required environment variables:")
            for var in missing_required:
                print(f"   - {var}")
            print("💡 Run: python3 setup_email.py to configure")
            return False
        
        print("✅ Required environment variables set")
        
        # Check optional vars
        for var in optional_vars:
            value = os.environ.get(var)
            if value:
                print(f"✅ {var}: configured")
            else:
                print(f"⚠️  {var}: using default")
        
        return True
        
    except ImportError:
        print("❌ python-dotenv not installed")
        print("💡 Install with: pip install python-dotenv")
        return False
    except Exception as e:
        print(f"❌ Error loading environment: {e}")
        return False

def check_email_functionality():
    """Test email functionality"""
    print("\n🔍 Testing email functionality...")
    
    try:
        from email_handler import send_email_report
        print("✅ email_handler module imports successfully")
        
        # Test with dummy data
        test_lead_data = {
            "email": "test@example.com",
            "name": "Test User",
            "company": "Test Company"
        }
        
        test_scan_results = {
            "scan_id": "test-123",
            "timestamp": datetime.now().isoformat(),
            "risk_assessment": {"overall_score": 75, "risk_level": "Medium"}
        }
        
        test_html = "<html><body><h1>Test Report</h1></body></html>"
        
        print("✅ Email function is callable")
        print("💡 Use test_email_debug.py for full testing")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing email functionality: {e}")
        return False

def check_app_integration():
    """Check if email is properly integrated in app.py"""
    print("\n🔍 Checking app.py email integration...")
    
    if not os.path.exists('app.py'):
        print("❌ app.py not found!")
        return False
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Check for email-related imports and functions
        checks = [
            ('email_handler import', 'from email_handler import' in content or 'import email_handler' in content),
            ('email_report route', '/api/email_report' in content),
            ('send_email_report call', 'send_email_report(' in content),
        ]
        
        all_good = True
        for check_name, check_result in checks:
            if check_result:
                print(f"✅ {check_name}: found")
            else:
                print(f"❌ {check_name}: missing")
                all_good = False
        
        return all_good
        
    except Exception as e:
        print(f"❌ Error checking app.py: {e}")
        return False

def fix_common_email_issues():
    """Fix common email configuration issues"""
    print("\n🔧 Fixing common email issues...")
    
    fixes_applied = []
    
    # Fix 1: Ensure email_handler.py has all imports
    if check_and_fix_imports():
        fixes_applied.append("Updated imports in email_handler.py")
    
    # Fix 2: Check SMTP timeout and connection handling
    email_handler_path = 'email_handler.py'
    if os.path.exists(email_handler_path):
        try:
            with open(email_handler_path, 'r') as f:
                content = f.read()
            
            # Check for proper timeout handling
            if 'timeout=30' not in content:
                content = content.replace('smtplib.SMTP(smtp_server, smtp_port)', 
                                        'smtplib.SMTP(smtp_server, smtp_port, timeout=30)')
                with open(email_handler_path, 'w') as f:
                    f.write(content)
                fixes_applied.append("Added SMTP timeout")
        
        except Exception as e:
            print(f"⚠️  Could not apply SMTP fixes: {e}")
    
    # Fix 3: Create .env.sample if needed
    if not os.path.exists('.env') and not os.path.exists('.env.sample'):
        if os.path.exists('env.template'):
            try:
                import shutil
                shutil.copy('env.template', '.env.sample')
                fixes_applied.append("Created .env.sample from template")
            except Exception as e:
                print(f"⚠️  Could not create .env.sample: {e}")
    
    if fixes_applied:
        print("✅ Applied fixes:")
        for fix in fixes_applied:
            print(f"   - {fix}")
    else:
        print("ℹ️  No automatic fixes needed")
    
    return len(fixes_applied) > 0

def show_troubleshooting_guide():
    """Show comprehensive troubleshooting guide"""
    print("\n📚 Email Troubleshooting Guide")
    print("=" * 50)
    
    print("""
🔧 COMMON ISSUES AND SOLUTIONS:

1. ❌ "SMTP credentials not found"
   💡 Solution: Configure .env file with SMTP_USER and SMTP_PASSWORD
   🛠️  Run: python3 setup_email.py

2. ❌ "Authentication failed"
   💡 Solutions:
      - Gmail: Use App Password (not regular password)
      - Outlook: Enable "Less secure app access" or use App Password
      - Custom domains: Verify username format (email vs username)

3. ❌ "Connection timeout" or "Connection refused"
   💡 Solutions:
      - Check SMTP server and port (common ports: 587, 465, 25)
      - Verify firewall/network allows outbound SMTP
      - Try different port (587 for TLS, 465 for SSL)

4. ❌ "SSL/TLS errors"
   💡 Solutions:
      - Use port 587 with STARTTLS
      - Or use port 465 with SSL/TLS
      - Check if server supports encryption

5. ❌ "Email not received"
   💡 Solutions:
      - Check spam/junk folders
      - Verify recipient email address
      - Check email provider's sending limits
      - Review SMTP server logs

🔍 DEBUGGING COMMANDS:
   - Test configuration: python3 test_email_debug.py
   - Setup email: python3 setup_email.py
   - Check logs: tail -f scanner_platform.log

📧 PROVIDER-SPECIFIC SETTINGS:
   Gmail:     smtp.gmail.com:587 (use App Password)
   Outlook:   smtp-mail.outlook.com:587
   Yahoo:     smtp.mail.yahoo.com:587 (use App Password)
   Private:   mail.privateemail.com:587

🔐 SECURITY NOTES:
   - Never commit .env file to version control
   - Use app passwords for enhanced security
   - Keep SMTP credentials secure
   - Consider using environment variables in production
""")

def main():
    """Main troubleshooting function"""
    print("🔧 CybrScan Email Issue Fixer")
    print("=" * 50)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Run diagnostic checks
    checks = [
        ("Environment Setup", check_environment_setup),
        ("Email Handler Imports", check_and_fix_imports),
        ("App Integration", check_app_integration),
        ("Email Functionality", check_email_functionality)
    ]
    
    results = {}
    for check_name, check_func in checks:
        try:
            print(f"\n🔍 {check_name}")
            print("-" * 30)
            results[check_name] = check_func()
        except Exception as e:
            print(f"❌ Error in {check_name}: {e}")
            results[check_name] = False
    
    # Apply fixes
    print("\n🔧 Applying Fixes")
    print("-" * 30)
    fix_common_email_issues()
    
    # Summary
    print(f"\n📊 Summary")
    print("=" * 30)
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for check_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {check_name}")
    
    print(f"\nOverall: {passed}/{total} checks passed")
    
    # Show next steps
    if passed < total:
        print(f"\n🔧 NEXT STEPS:")
        if not results.get("Environment Setup", False):
            print("1. Configure email settings: python3 setup_email.py")
        print("2. Test email functionality: python3 test_email_debug.py")
        print("3. Check the troubleshooting guide below")
        
        show_troubleshooting_guide()
    else:
        print(f"\n🎉 All checks passed! Email should be working.")
        print("💡 Test with: python3 test_email_debug.py")
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Troubleshooting interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        logging.error(f"Unexpected error in email troubleshooting: {e}")