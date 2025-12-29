#!/usr/bin/env python3
"""
Test Email/SMTP Configuration

Run this to verify your email settings work before using the web app.
"""

import os
import smtplib
from email.mime.text import MIMEText

def test_smtp_connection():
    """Test SMTP connection with your settings"""

    # Get settings
    smtp_server = os.getenv('SMTP_SERVER', 'smtp-mail.outlook.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_user = os.getenv('SMTP_USER', '')
    smtp_password = os.getenv('SMTP_PASSWORD', '')
    kindle_email = os.getenv('KINDLE_EMAIL', '')

    print("🧪 Testing Email Configuration")
    print("=" * 40)

    if not smtp_user or not smtp_password:
        print("❌ SMTP_USER and/or SMTP_PASSWORD not set")
        print("💡 Set them with:")
        print("   export SMTP_USER='your-email@example.com'")
        print("   export SMTP_PASSWORD='your-password'")
        return False

    if not kindle_email:
        print("⚠️  KINDLE_EMAIL not set (optional for this test)")

    print(f"📧 Server: {smtp_server}:{smtp_port}")
    print(f"👤 User: {smtp_user}")
    print(f"📨 Kindle: {kindle_email or 'not set'}")
    print()

    try:
        print("🔗 Connecting to SMTP server...")
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()

        print("🔐 Authenticating...")
        server.login(smtp_user, smtp_password)

        print("✅ Authentication successful!")

        # Try to send a test email if Kindle email is set
        if kindle_email:
            print("📤 Sending test email...")
            msg = MIMEText("Test email from Kindle Newsletter App")
            msg['Subject'] = 'Kindle Newsletter Test'
            msg['From'] = smtp_user
            msg['To'] = kindle_email

            server.send_message(msg)
            print("✅ Test email sent successfully!")
        else:
            print("ℹ️  Skipping test email (no KINDLE_EMAIL set)")

        server.quit()
        print("\n🎉 Email configuration is working!")
        return True

    except smtplib.SMTPAuthenticationError:
        print("❌ Authentication failed - check username/password")
        print("💡 For Gmail: Use App Password, not regular password")
        print("💡 For Outlook/Yahoo: Use regular password")
        return False

    except smtplib.SMTPConnectError:
        print("❌ Connection failed - check server and port")
        return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    success = test_smtp_connection()

    if success:
        print("\n🚀 Ready to use the web app with email!")
        print("   python simple_web_app.py")
    else:
        print("\n📖 Check EMAIL_SETUP_GUIDE.md for help")
        print("📧 Popular working configurations:")
        print("   Outlook: SMTP_USER='you@outlook.com' SMTP_PASSWORD='regular-password'")
        print("   Yahoo:   SMTP_USER='you@yahoo.com' SMTP_PASSWORD='regular-password'")
        print("   Gmail:   SMTP_USER='you@gmail.com' SMTP_PASSWORD='app-password'")
