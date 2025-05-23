#!/usr/bin/env python3
"""
Email Debugging Script
======================
This script tests the email functionality and diagnoses common issues.
"""

import os
import sys
import logging
import smtplib
import socket
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def check_environment_variables():
    """Check if required environment variables are set"""
    print("🔍 Checking Environment Variables")
    print("=" * 40)
    
    required_vars = ['SMTP_USER', 'SMTP_PASSWORD']
    optional_vars = ['SMTP_SERVER', 'SMTP_PORT']
    
    all_good = True
    
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            print(f"✅ {var}: {'*' * len(value)} (set)")
        else:
            print(f"❌ {var}: NOT SET")
            all_good = False
    
    for var in optional_vars:
        value = os.environ.get(var)
        if value:
            print(f"ℹ️  {var}: {value}")
        else:
            print(f"⚠️  {var}: Using default")
    
    return all_good

def test_smtp_connection():
    """Test SMTP server connectivity"""
    print("\n🔗 Testing SMTP Connection")
    print("=" * 40)
    
    smtp_server = os.environ.get('SMTP_SERVER', 'mail.privateemail.com')
    smtp_port = int(os.environ.get('SMTP_PORT', 587))
    smtp_user = os.environ.get('SMTP_USER')
    smtp_password = os.environ.get('SMTP_PASSWORD')
    
    if not smtp_user or not smtp_password:
        print("❌ Cannot test connection: Missing credentials")
        return False
    
    try:
        print(f"📡 Connecting to {smtp_server}:{smtp_port}")
        
        # Test basic connectivity
        with socket.create_connection((smtp_server, smtp_port), timeout=10) as sock:
            print("✅ Socket connection successful")
        
        # Test SMTP connection
        with smtplib.SMTP(smtp_server, smtp_port, timeout=30) as server:
            print("✅ SMTP connection established")
            
            # Test EHLO
            server.ehlo()
            print("✅ EHLO successful")
            
            # Test STARTTLS
            if server.has_extn('STARTTLS'):
                server.starttls()
                print("✅ STARTTLS successful")
                server.ehlo()  # Re-identify after STARTTLS
            else:
                print("⚠️  STARTTLS not supported")
            
            # Test authentication
            try:
                server.login(smtp_user, smtp_password)
                print("✅ Authentication successful")
                return True
            except smtplib.SMTPAuthenticationError as e:
                print(f"❌ Authentication failed: {e}")
                return False
            except Exception as e:
                print(f"❌ Login error: {e}")
                return False
                
    except socket.timeout:
        print("❌ Connection timeout - check server and port")
        return False
    except socket.gaierror as e:
        print(f"❌ DNS resolution failed: {e}")
        return False
    except ConnectionRefusedError:
        print("❌ Connection refused - check server and port")
        return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def send_test_email(test_email=None):
    """Send a test email"""
    print("\n📧 Sending Test Email")
    print("=" * 40)
    
    smtp_server = os.environ.get('SMTP_SERVER', 'mail.privateemail.com')
    smtp_port = int(os.environ.get('SMTP_PORT', 587))
    smtp_user = os.environ.get('SMTP_USER')
    smtp_password = os.environ.get('SMTP_PASSWORD')
    
    if not smtp_user or not smtp_password:
        print("❌ Cannot send test email: Missing credentials")
        return False
    
    # Use provided email or default to sender
    recipient = test_email or smtp_user
    print(f"📬 Sending test email to: {recipient}")
    
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'CybrScan Email Test - ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        msg['From'] = smtp_user
        msg['To'] = recipient
        
        # Create text content
        text_content = f"""
CybrScan Email Test

This is a test email sent at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

If you receive this email, the email configuration is working correctly.

SMTP Server: {smtp_server}:{smtp_port}
From: {smtp_user}
To: {recipient}
        """
        
        # Create HTML content
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #02054c; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .info {{ background-color: #f8f9fa; padding: 15px; border-left: 4px solid #02054c; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>CybrScan Email Test</h1>
            </div>
            <div class="content">
                <p>This is a test email sent at <strong>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</strong></p>
                <p>If you receive this email, the email configuration is working correctly! ✅</p>
                
                <div class="info">
                    <h3>Configuration Details:</h3>
                    <ul>
                        <li><strong>SMTP Server:</strong> {smtp_server}:{smtp_port}</li>
                        <li><strong>From:</strong> {smtp_user}</li>
                        <li><strong>To:</strong> {recipient}</li>
                    </ul>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Attach parts
        part1 = MIMEText(text_content, 'plain')
        part2 = MIMEText(html_content, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port, timeout=30) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
            
        print("✅ Test email sent successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send test email: {e}")
        logging.error(f"Test email error: {e}")
        return False

def diagnose_common_issues():
    """Diagnose common email configuration issues"""
    print("\n🔧 Diagnosing Common Issues")
    print("=" * 40)
    
    issues_found = []
    
    # Check environment variables
    smtp_user = os.environ.get('SMTP_USER')
    smtp_password = os.environ.get('SMTP_PASSWORD')
    smtp_server = os.environ.get('SMTP_SERVER', 'mail.privateemail.com')
    smtp_port = int(os.environ.get('SMTP_PORT', 587))
    
    if not smtp_user:
        issues_found.append("❌ SMTP_USER environment variable not set")
    elif '@' not in smtp_user:
        issues_found.append("⚠️  SMTP_USER should be a valid email address")
    
    if not smtp_password:
        issues_found.append("❌ SMTP_PASSWORD environment variable not set")
    elif len(smtp_password) < 8:
        issues_found.append("⚠️  SMTP_PASSWORD seems too short")
    
    # Check port
    if smtp_port not in [25, 465, 587, 2525]:
        issues_found.append(f"⚠️  Unusual SMTP port: {smtp_port} (common ports: 25, 465, 587, 2525)")
    
    # Check server
    if not smtp_server:
        issues_found.append("❌ SMTP_SERVER not set")
    
    # Common provider configurations
    provider_configs = {
        'gmail.com': {'server': 'smtp.gmail.com', 'port': 587},
        'outlook.com': {'server': 'smtp-mail.outlook.com', 'port': 587},
        'yahoo.com': {'server': 'smtp.mail.yahoo.com', 'port': 587},
        'privateemail.com': {'server': 'mail.privateemail.com', 'port': 587}
    }
    
    if smtp_user and '@' in smtp_user:
        domain = smtp_user.split('@')[1].lower()
        if domain in provider_configs:
            expected = provider_configs[domain]
            if smtp_server != expected['server']:
                issues_found.append(f"⚠️  For {domain}, expected server: {expected['server']} (got: {smtp_server})")
            if smtp_port != expected['port']:
                issues_found.append(f"⚠️  For {domain}, expected port: {expected['port']} (got: {smtp_port})")
    
    if issues_found:
        print("Found potential issues:")
        for issue in issues_found:
            print(f"  {issue}")
    else:
        print("✅ No obvious configuration issues found")
    
    return len(issues_found) == 0

def test_email_import():
    """Test if email_handler module can be imported"""
    print("\n📦 Testing Email Module Import")
    print("=" * 40)
    
    try:
        from email_handler import send_email_report, send_branded_email_report
        print("✅ email_handler module imported successfully")
        print("✅ send_email_report function available")
        print("✅ send_branded_email_report function available")
        return True
    except ImportError as e:
        print(f"❌ Failed to import email_handler: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error importing email_handler: {e}")
        return False

def main():
    """Main diagnostic function"""
    print("🔍 CybrScan Email Diagnostics")
    print("=" * 50)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all tests
    tests = [
        ("Environment Variables", check_environment_variables),
        ("Email Module Import", test_email_import),
        ("SMTP Connection", test_smtp_connection),
        ("Common Issues", diagnose_common_issues)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ Error in {test_name}: {e}")
            results[test_name] = False
    
    # Summary
    print("\n📊 Summary")
    print("=" * 40)
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    # Send test email if everything looks good
    if all(results.values()):
        print("\n🎉 All tests passed! Sending test email...")
        test_email = input("Enter email address for test (or press Enter to use SMTP_USER): ").strip()
        if not test_email:
            test_email = None
        send_test_email(test_email)
    else:
        print("\n⚠️  Some tests failed. Fix issues above before testing email sending.")
    
    print(f"\nDiagnostics completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Diagnostics interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        logging.error(f"Unexpected error in diagnostics: {e}")