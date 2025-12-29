#!/usr/bin/env python3
"""
Launcher for Kindle Newsletter Web App

This script checks your configuration and starts the web app.
"""

import os
import sys
import subprocess

def check_config():
    """Check if required configuration is set"""
    print("🔧 Checking configuration...")

    issues = []

    # Check Kindle email
    kindle_email = os.getenv('KINDLE_EMAIL', 'your-kindle@kindle.com')
    if kindle_email == 'your-kindle@kindle.com':
        issues.append("❌ KINDLE_EMAIL not set. Find your Kindle email at https://www.amazon.com/myk")

    # Check SMTP settings
    smtp_user = os.getenv('SMTP_USER', '')
    smtp_password = os.getenv('SMTP_PASSWORD', '')

    if not smtp_user:
        issues.append("❌ SMTP_USER not set. Set to your email address")
    if not smtp_password:
        issues.append("❌ SMTP_PASSWORD not set. Use Gmail App Password or regular password")

    if issues:
        print("\n❌ Configuration Issues Found:")
        for issue in issues:
            print(f"   {issue}")
        print("\n💡 Set environment variables like this:")
        print("   export KINDLE_EMAIL='your-kindle@kindle.com'")
        print("   export SMTP_USER='your-email@gmail.com'")
        print("   export SMTP_PASSWORD='your-app-password'")
        print("\n   Or create a .env file with these variables")
        return False

    print("✅ Configuration looks good!")
    return True

def start_web_app():
    """Start the Flask web application"""
    port = 8000
    print("\n🚀 Starting Kindle Newsletter Web App...")
    print(f"📱 Open your browser to: http://localhost:{port}")
    print("❌ Press Ctrl+C to stop the server")
    print("=" * 50)

    try:
        # Run the web app
        subprocess.run([sys.executable, 'web_app.py'], cwd=os.path.dirname(__file__))
    except KeyboardInterrupt:
        print("\n👋 Web app stopped")
    except Exception as e:
        print(f"\n❌ Error starting web app: {e}")

if __name__ == '__main__':
    print("📖 Kindle Newsletter Web App Launcher")
    print("=" * 40)

    if check_config():
        start_web_app()
    else:
        print("\n❌ Please fix configuration issues above, then run this script again.")
        sys.exit(1)
