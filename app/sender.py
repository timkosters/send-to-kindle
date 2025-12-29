import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.utils import formataddr
import os
from .config import SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, KINDLE_EMAIL, GMAIL_USER

class KindleSender:
    def __init__(self):
        pass

    def send_epub(self, epub_path):
        """Send EPUB file to Kindle email"""
        if not SMTP_USER or not SMTP_PASSWORD:
            print("ℹ️  SMTP credentials not configured. Skipping email.")
            return False

        if not KINDLE_EMAIL:
            print("ℹ️  Kindle email not configured. Skipping email.")
            return False

        try:
            print(f"📤 Sending {os.path.basename(epub_path)} to {KINDLE_EMAIL}...")
            
            msg = MIMEMultipart()
            msg['From'] = formataddr(('Send to Kindle', SMTP_USER))
            msg['To'] = KINDLE_EMAIL
            msg['Subject'] = 'Convert'  # Magic subject for Amazon

            with open(epub_path, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename="{os.path.basename(epub_path)}"'
                )
                msg.attach(part)

            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
            server.quit()

            print(f"✅ Successfully sent to Kindle!")
            return True
        except Exception as e:
            print(f"❌ Error sending to Kindle: {e}")
            return False
