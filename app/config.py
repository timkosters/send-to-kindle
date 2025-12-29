import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / 'epub_files'
OUTPUT_DIR.mkdir(exist_ok=True)

# Email Configuration
GMAIL_USER = os.getenv('GMAIL_USER')
GMAIL_APP_PASSWORD = os.getenv('GMAIL_APP_PASSWORD')
IMAP_HOST = 'imap.gmail.com'

# Kindle Configuration
KINDLE_EMAIL = os.getenv('KINDLE_EMAIL')

# SMTP Configuration
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp-mail.outlook.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USER = os.getenv('SMTP_USER')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')

# Processing Settings
MAX_IMAGE_WIDTH = 800
MAX_IMAGE_HEIGHT = 1200
IMAGE_QUALITY = 85
