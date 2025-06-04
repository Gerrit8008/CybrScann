#!/usr/bin/env python3
"""
Email Setup Script
==================
This script helps configure email settings for CybrScan.
"""

import os
import sys
import secrets
import string
from datetime import datetime

def generate_secret_key():
    """Generate a secure secret key"""
    alphabet = string.ascii_letters + string.digits + '!@#$%^&*'
    return ''.join(secrets.choice(alphabet) for _ in range(32))

def setup_email_config():
    """Interactive email configuration setup"""
    print("🔧 CybrScan Email Setup")
    print("=" * 40)
    print("This script will help you configure email settings.\n")
    
    # Check if .env already exists
    env_path = '.env'
    if os.path.exists(env_path):
        print("⚠️  .env file already exists!")
        overwrite = input("Do you want to overwrite it? (y/N): ").strip().lower()
        if overwrite != 'y':
            print("❌ Setup cancelled.")
            return False
        
        # Backup existing .env
        backup_path = f'.env.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        os.rename(env_path, backup_path)
        print(f"📁 Existing .env backed up to {backup_path}")
    
    print("\n📧 Email Provider Configuration")
    print("Select your email provider:")
    print("1. Gmail (gmail.com)")
    print("2. Outlook (outlook.com/hotmail.com)")
    print("3. Yahoo (yahoo.com)")
    print("4. PrivateEmail (privateemail.com)")
    print("5. Custom SMTP server")
    
    provider_choice = input("\nEnter choice (1-5): ").strip()
    
    # Provider configurations
    providers = {
        '1': {'name': 'Gmail', 'server': 'smtp.gmail.com', 'port': 587, 'notes': 'Use app password, not regular password'},
        '2': {'name': 'Outlook', 'server': 'smtp-mail.outlook.com', 'port': 587, 'notes': 'May require app password'},
        '3': {'name': 'Yahoo', 'server': 'smtp.mail.yahoo.com', 'port': 587, 'notes': 'Use app password'},
        '4': {'name': 'PrivateEmail', 'server': 'mail.privateemail.com', 'port': 587, 'notes': 'Use regular email password'},
        '5': {'name': 'Custom', 'server': '', 'port': 587, 'notes': 'Enter your custom SMTP settings'}
    }
    
    if provider_choice not in providers:
        print("❌ Invalid choice. Using PrivateEmail as default.")
        provider_choice = '4'
    
    provider = providers[provider_choice]
    print(f"\n✅ Selected: {provider['name']}")
    if provider['notes']:
        print(f"📝 Note: {provider['notes']}")
    
    # Get SMTP settings
    if provider_choice == '5':  # Custom
        smtp_server = input("SMTP Server: ").strip()
        smtp_port = input("SMTP Port (default 587): ").strip() or '587'
    else:
        smtp_server = provider['server']
        smtp_port = str(provider['port'])
    
    print(f"\n📡 SMTP Server: {smtp_server}:{smtp_port}")
    
    # Get email credentials
    print("\n🔑 Email Credentials")
    smtp_user = input("Email Address: ").strip()
    
    if not smtp_user or '@' not in smtp_user:
        print("❌ Invalid email address.")
        return False
    
    smtp_password = input("Email Password (or App Password): ").strip()
    
    if not smtp_password:
        print("❌ Password cannot be empty.")
        return False
    
    # Admin email (optional)
    admin_email = input(f"Admin Email (default: {smtp_user}): ").strip() or smtp_user
    
    # Generate secret key
    secret_key = generate_secret_key()
    
    # Environment selection
    print("\n🏗️  Environment Configuration")
    print("1. Development (debug enabled)")
    print("2. Production (debug disabled)")
    
    env_choice = input("Select environment (1-2): ").strip()
    if env_choice == '2':
        flask_env = 'production'
        flask_debug = 'False'
    else:
        flask_env = 'development'
        flask_debug = 'True'
    
    # Create .env file
    env_content = f'''# CybrScan Configuration
# Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

# Flask Configuration
SECRET_KEY={secret_key}
FLASK_ENV={flask_env}
FLASK_DEBUG={flask_debug}

# Email Configuration
SMTP_SERVER={smtp_server}
SMTP_PORT={smtp_port}
SMTP_USER={smtp_user}
SMTP_PASSWORD={smtp_password}
ADMIN_EMAIL={admin_email}

# Feature Flags
ENABLE_AUTO_EMAIL=True
FULL_SCAN_ENABLED=True

# Rate Limiting
RATE_LIMIT_PER_DAY=200
RATE_LIMIT_PER_HOUR=50
'''
    
    try:
        with open(env_path, 'w') as f:
            f.write(env_content)
        
        print(f"\n✅ Configuration saved to {env_path}")
        print("\n🔒 Security Notes:")
        print("- Keep your .env file secure and never commit it to version control")
        print("- Use app passwords for Gmail, Yahoo, and some Outlook accounts")
        print("- Test email functionality before deploying to production")
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving configuration: {e}")
        return False

def test_email_after_setup():
    """Test email configuration after setup"""
    print("\n🧪 Testing Email Configuration")
    print("=" * 40)
    
    test_now = input("Would you like to test the email configuration now? (Y/n): ").strip().lower()
    if test_now == 'n':
        print("⏭️  Email test skipped. You can test later with: python3 test_email_debug.py")
        return
    
    print("Running email diagnostics...")
    try:
        os.system("python3 test_email_debug.py")
    except Exception as e:
        print(f"❌ Error running email test: {e}")
        print("You can manually test with: python3 test_email_debug.py")

def show_next_steps():
    """Show next steps after configuration"""
    print("\n🎯 Next Steps")
    print("=" * 40)
    print("1. Test email functionality: python3 test_email_debug.py")
    print("2. Start the application: python3 app.py")
    print("3. Visit the scan page and try sending a report")
    print("\n📚 Troubleshooting:")
    print("- If Gmail: Enable 2FA and use App Password")
    print("- If authentication fails: Check email provider's SMTP settings")
    print("- For custom domains: Verify SMTP server and port")
    print("- Check firewall/network settings if connection fails")

def main():
    """Main setup function"""
    try:
        print("🚀 Welcome to CybrScan Email Setup!")
        print("This wizard will help you configure email functionality.\n")
        
        if setup_email_config():
            test_email_after_setup()
            show_next_steps()
            print("\n🎉 Email setup completed successfully!")
        else:
            print("\n❌ Email setup failed. Please try again.")
            
    except KeyboardInterrupt:
        print("\n\n🛑 Setup interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()