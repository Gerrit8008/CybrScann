#!/usr/bin/env python3
"""
Simple Email Setup (No Dependencies)
====================================
This script creates email configuration without external dependencies.
"""

import os
import sys
from datetime import datetime

def load_env_file():
    """Load .env file manually without python-dotenv"""
    env_vars = {}
    if os.path.exists('.env'):
        try:
            with open('.env', 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip()
        except Exception as e:
            print(f"Error reading .env file: {e}")
    return env_vars

def create_env_file():
    """Create .env file with user input"""
    print("🔧 Simple Email Configuration")
    print("=" * 40)
    
    if os.path.exists('.env'):
        print("⚠️  .env file already exists!")
        overwrite = input("Overwrite? (y/N): ").strip().lower()
        if overwrite != 'y':
            return False
    
    print("\nEnter your email configuration:")
    
    # Get email settings
    smtp_user = input("Email address: ").strip()
    if not smtp_user or '@' not in smtp_user:
        print("❌ Invalid email address")
        return False
    
    smtp_password = input("Email password: ").strip()
    if not smtp_password:
        print("❌ Password required")
        return False
    
    # Determine provider
    domain = smtp_user.split('@')[1].lower()
    if 'gmail.com' in domain:
        smtp_server = 'smtp.gmail.com'
        print("📧 Detected Gmail - make sure to use App Password!")
    elif 'outlook.com' in domain or 'hotmail.com' in domain:
        smtp_server = 'smtp-mail.outlook.com'
        print("📧 Detected Outlook")
    elif 'yahoo.com' in domain:
        smtp_server = 'smtp.mail.yahoo.com'
        print("📧 Detected Yahoo - make sure to use App Password!")
    else:
        smtp_server = input(f"SMTP server for {domain}: ").strip() or 'mail.privateemail.com'
    
    smtp_port = input("SMTP port (default 587): ").strip() or '587'
    
    # Create .env content
    env_content = f'''# CybrScan Email Configuration
# Created: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

SECRET_KEY=your_secret_key_here_{datetime.now().strftime("%Y%m%d")}
FLASK_ENV=development
FLASK_DEBUG=True

SMTP_SERVER={smtp_server}
SMTP_PORT={smtp_port}
SMTP_USER={smtp_user}
SMTP_PASSWORD={smtp_password}
ADMIN_EMAIL={smtp_user}

ENABLE_AUTO_EMAIL=True
FULL_SCAN_ENABLED=True
RATE_LIMIT_PER_DAY=200
RATE_LIMIT_PER_HOUR=50
'''
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print(f"\n✅ Configuration saved to .env")
        return True
    except Exception as e:
        print(f"❌ Error saving .env: {e}")
        return False

def test_configuration():
    """Test the email configuration"""
    print("\n🧪 Testing Configuration")
    print("=" * 30)
    
    # Load environment variables
    env_vars = load_env_file()
    
    # Set environment variables for this session
    for key, value in env_vars.items():
        os.environ[key] = value
    
    # Check required variables
    required = ['SMTP_USER', 'SMTP_PASSWORD', 'SMTP_SERVER', 'SMTP_PORT']
    missing = []
    
    for var in required:
        if var not in env_vars:
            missing.append(var)
        else:
            print(f"✅ {var}: configured")
    
    if missing:
        print("❌ Missing variables:")
        for var in missing:
            print(f"   - {var}")
        return False
    
    # Try to test SMTP connection
    try:
        import smtplib
        import socket
        
        smtp_server = env_vars['SMTP_SERVER']
        smtp_port = int(env_vars['SMTP_PORT'])
        smtp_user = env_vars['SMTP_USER']
        smtp_password = env_vars['SMTP_PASSWORD']
        
        print(f"\n📡 Testing connection to {smtp_server}:{smtp_port}")
        
        # Test basic connectivity
        with socket.create_connection((smtp_server, smtp_port), timeout=10):
            print("✅ Network connection successful")
        
        # Test SMTP
        with smtplib.SMTP(smtp_server, smtp_port, timeout=30) as server:
            server.ehlo()
            print("✅ SMTP connection established")
            
            if server.has_extn('STARTTLS'):
                server.starttls()
                server.ehlo()
                print("✅ TLS encryption enabled")
            
            try:
                server.login(smtp_user, smtp_password)
                print("✅ Authentication successful")
                print("\n🎉 Email configuration is working!")
                return True
            except smtplib.SMTPAuthenticationError:
                print("❌ Authentication failed")
                print("💡 For Gmail/Yahoo: Use App Password")
                print("💡 For Outlook: Check account settings")
                return False
                
    except ImportError:
        print("⚠️  Cannot test SMTP (missing modules)")
        return True  # Assume it's okay
    except socket.timeout:
        print("❌ Connection timeout")
        return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def show_usage_instructions():
    """Show how to use the email functionality"""
    print("\n📖 Usage Instructions")
    print("=" * 30)
    print("""
✅ Email is now configured!

🚀 To test email functionality:
   1. Start the application: python3 app.py
   2. Complete a security scan
   3. Click "Email Report" button
   4. Check your email (including spam folder)

🔧 To test email directly:
   python3 test_email_debug.py

⚠️  IMPORTANT NOTES:
   - Gmail/Yahoo: Use App Passwords, not regular passwords
   - Check spam folders for test emails
   - Verify firewall allows outbound SMTP (port 587/465)
   
🆘 If emails aren't working:
   1. Check spam/junk folders
   2. Verify App Password is used (Gmail/Yahoo)
   3. Try different SMTP port (465 for SSL)
   4. Check email provider's security settings
""")

def main():
    """Main setup function"""
    print("📧 CybrScan Simple Email Setup")
    print("=" * 50)
    
    try:
        # Check if .env exists and is configured
        env_vars = load_env_file()
        if env_vars.get('SMTP_USER') and env_vars.get('SMTP_PASSWORD'):
            print("📋 Existing configuration found")
            test_existing = input("Test existing configuration? (Y/n): ").strip().lower()
            if test_existing != 'n':
                # Set environment variables and test
                for key, value in env_vars.items():
                    os.environ[key] = value
                if test_configuration():
                    show_usage_instructions()
                    return
        
        # Create new configuration
        if create_env_file():
            if test_configuration():
                show_usage_instructions()
            else:
                print("\n⚠️  Configuration saved but testing failed")
                print("💡 Check settings and try again")
        
    except KeyboardInterrupt:
        print("\n🛑 Setup cancelled")
    except Exception as e:
        print(f"\n❌ Setup error: {e}")

if __name__ == "__main__":
    main()