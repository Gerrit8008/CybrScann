# CybrScan Email Troubleshooting Guide

## 🚀 Quick Setup (Recommended)

### Step 1: Configure Email Settings
```bash
python3 simple_email_setup.py
```
This script will guide you through email configuration without requiring additional dependencies.

### Step 2: Test Email Functionality
```bash
python3 test_email_debug.py
```

---

## 🔧 Manual Setup

### 1. Create `.env` File
Copy the template and configure your settings:
```bash
cp env.template .env
```

Edit `.env` with your email settings:
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
ADMIN_EMAIL=your-email@gmail.com
```

### 2. Provider-Specific Settings

#### Gmail
- **Server**: smtp.gmail.com:587
- **Security**: Use App Password (not regular password)
- **Setup**: Google Account > Security > 2-Step Verification > App passwords

#### Outlook/Hotmail
- **Server**: smtp-mail.outlook.com:587
- **Security**: May require App Password
- **Setup**: Microsoft Account > Security > App passwords

#### Yahoo
- **Server**: smtp.mail.yahoo.com:587
- **Security**: Use App Password
- **Setup**: Yahoo Account > Account Security > Generate app password

#### Custom/Business Email
- **Server**: Contact your email provider
- **Port**: Usually 587 (STARTTLS) or 465 (SSL)
- **Auth**: Use your regular email credentials

---

## 🔍 Troubleshooting Steps

### 1. Check Configuration
```bash
python3 fix_email_issues.py
```

### 2. Test Connection
```bash
python3 test_email_debug.py
```

### 3. Common Issues & Solutions

#### ❌ "SMTP credentials not found"
**Cause**: No .env file or missing SMTP_USER/SMTP_PASSWORD
**Solution**: 
```bash
python3 simple_email_setup.py
```

#### ❌ "Authentication failed"
**Causes**: 
- Using regular password instead of App Password
- Incorrect credentials
- Account security settings

**Solutions**:
- Gmail/Yahoo: Generate and use App Password
- Outlook: Enable app access or use App Password
- Verify email and password are correct

#### ❌ "Connection timeout" or "Connection refused"
**Causes**:
- Wrong SMTP server or port
- Firewall blocking outbound connections
- Network issues

**Solutions**:
- Verify SMTP server and port
- Try alternative ports: 587 (TLS), 465 (SSL), 25 (unencrypted)
- Check firewall settings
- Test from different network

#### ❌ "SSL/TLS errors"
**Causes**:
- Mismatched encryption settings
- Outdated TLS version

**Solutions**:
- Use port 587 with STARTTLS
- Try port 465 with SSL
- Update Python if very old

#### ❌ "Email not received"
**Causes**:
- Email in spam folder
- Provider blocks/delays emails
- Recipient email incorrect

**Solutions**:
- Check spam/junk folders
- Verify recipient email address
- Wait a few minutes (some providers delay)
- Check sender reputation

---

## 🛠️ Advanced Troubleshooting

### Check Email Handler
```python
# Test import
from email_handler import send_email_report
print("✅ Email handler working")
```

### Debug SMTP Connection
```python
import smtplib
import os

# Load settings
smtp_server = os.environ.get('SMTP_SERVER')
smtp_port = int(os.environ.get('SMTP_PORT', 587))
smtp_user = os.environ.get('SMTP_USER')
smtp_password = os.environ.get('SMTP_PASSWORD')

# Test connection
with smtplib.SMTP(smtp_server, smtp_port) as server:
    server.ehlo()
    server.starttls()
    server.login(smtp_user, smtp_password)
    print("✅ SMTP connection successful")
```

### Check Application Integration
1. Verify `/api/email_report` route exists in app.py
2. Check email_handler import in app.py
3. Ensure send_email_report is called correctly

---

## 📧 Email Provider Setup Guides

### Gmail Setup
1. Enable 2-Step Verification
2. Go to Google Account > Security > App passwords
3. Select "Mail" and generate password
4. Use generated password in SMTP_PASSWORD

### Outlook Setup
1. Sign in to Microsoft Account
2. Go to Security > Advanced security options
3. Create app password for "Mail"
4. Use app password in SMTP_PASSWORD

### Yahoo Setup
1. Sign in to Yahoo Account
2. Go to Account Info > Account Security
3. Turn on 2-step verification
4. Generate app password for "Mail"
5. Use generated password in SMTP_PASSWORD

---

## 🚨 Security Best Practices

### Environment Variables
- Never commit `.env` file to version control
- Use strong, unique passwords
- Regularly rotate credentials
- Limit SMTP account permissions

### App Passwords
- Use app passwords instead of regular passwords
- Generate separate passwords for different applications
- Delete unused app passwords
- Monitor account access logs

### Network Security
- Use encrypted connections (TLS/SSL)
- Restrict SMTP access by IP if possible
- Monitor email sending patterns
- Set up alerts for unusual activity

---

## 📁 File Structure

```
CybrScan/
├── .env                    # Email configuration (create this)
├── env.template           # Configuration template
├── email_handler.py       # Email sending functions
├── config.py             # Application configuration
├── simple_email_setup.py # Setup wizard
├── test_email_debug.py   # Email testing
├── fix_email_issues.py   # Issue diagnosis
└── EMAIL_TROUBLESHOOTING.md # This guide
```

---

## 🔗 Useful Commands

```bash
# Setup email configuration
python3 simple_email_setup.py

# Test email functionality
python3 test_email_debug.py

# Diagnose email issues
python3 fix_email_issues.py

# View application logs
tail -f scanner_platform.log

# Start application
python3 app.py
```

---

## 📞 Getting Help

If you're still having issues:

1. **Check logs**: Look for error messages in console output
2. **Test basics**: Verify you can send email from your provider's web interface
3. **Network test**: Try from different network/computer
4. **Provider support**: Contact your email provider for SMTP settings
5. **Documentation**: Check your email provider's SMTP documentation

## 🎯 Success Indicators

You'll know email is working when:
- ✅ `python3 test_email_debug.py` shows all tests passing
- ✅ Test email is received (check spam folder)
- ✅ "Email Report" button in results page works
- ✅ No SMTP errors in application logs

---

*Last updated: 2025-05-23*