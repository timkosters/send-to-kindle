"""
Configuration for Kindle Newsletter Prototype

WHY GMAIL APP PASSWORD?
Google requires "App Passwords" for apps that access Gmail programmatically.
This is NOT your regular Gmail password - it's a special password generated just for this script.
You need 2-Step Verification enabled on your Google account to create App Passwords.

SETUP INSTRUCTIONS:
1. Gmail App Password Setup:
   - Go to https://myaccount.google.com/security
   - Enable 2-Step Verification if not already enabled
   - Go to App Passwords → Select App → Mail → Other (custom name)
   - Enter "Kindle Newsletter" → Generate
   - Copy the 16-character password (no spaces!)

2. Find Your Kindle Email:
   - Go to https://www.amazon.com/myk (Manage Your Kindle)
   - Select your device → Email address shows as "your-kindle@kindle.com"
   - Copy this email address

3. Approve Sender Email:
   - Go to https://www.amazon.com/gp/digital/fiona/manage
   - Add your Gmail address to "Approved Personal Document E-mail List"
   - CRITICAL: Without this, emails to Kindle will be rejected!

4. Environment Variables (recommended):
   - Set these in your terminal or create a .env file:
   export GMAIL_USER='your-gmail@gmail.com'
   export GMAIL_APP_PASSWORD='abcdefghijklmnop'  # 16-char app password
   export KINDLE_EMAIL='your-kindle@kindle.com'
"""

import os

# Email Configuration (for receiving forwarded emails)
GMAIL_USER = os.getenv('GMAIL_USER', 'your-gmail@gmail.com')
GMAIL_APP_PASSWORD = os.getenv('GMAIL_APP_PASSWORD', 'your-app-password')

# Kindle Configuration (for sending converted articles)
KINDLE_EMAIL = os.getenv('KINDLE_EMAIL', 'your-kindle@kindle.com')

# SMTP Configuration (OPTIONAL - only needed for automated email sending)
# Leave empty if using simple_web_app.py (manual download)
#
# Popular options:
# Gmail: smtp.gmail.com:587 (needs App Password)
# Outlook: smtp-mail.outlook.com:587 (regular password)
# Yahoo: smtp.mail.yahoo.com:587 (regular password)
# iCloud: smtp.mail.me.com:587 (App-Specific Password)
#
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp-mail.outlook.com')  # Default to Outlook
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USER = os.getenv('SMTP_USER', '')  # Your email address (optional)
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')  # Email password (optional)

# Legacy Gmail settings (for email-based methods)
IMAP_HOST = 'imap.gmail.com'

# File Storage
OUTPUT_DIR = './epub_files'

# Processing Settings
MAX_IMAGE_WIDTH = 800
MAX_IMAGE_HEIGHT = 1200
IMAGE_QUALITY = 85
