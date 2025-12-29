#!/usr/bin/env python3
"""
Email Watcher for Kindle Newsletter Service
Periodically checks Gmail for new forwarded newsletters and processes them.
"""

import time
import imaplib
import email
from email.header import decode_header
import schedule

from app.content import ContentExtractor
from app.epub import EpubBuilder
from app.sender import KindleSender
from app.config import GMAIL_USER, GMAIL_APP_PASSWORD, IMAP_HOST

class EmailWatcher:
    def __init__(self):
        self.extractor = ContentExtractor()
        self.builder = EpubBuilder()
        self.sender = KindleSender()
        self.mail = None

    def connect(self):
        """Connect to Gmail IMAP"""
        try:
            print("🔗 Connecting to Gmail...")
            self.mail = imaplib.IMAP4_SSL(IMAP_HOST)
            self.mail.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            self.mail.select('inbox')
            print("✅ Connected successfully")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False

    def process_unread_emails(self):
        """Check for and process unread emails"""
        if not self.mail:
            if not self.connect():
                return

        try:
            # Search for unread emails
            status, messages = self.mail.search(None, 'UNSEEN')
            if status != 'OK':
                return

            email_ids = messages[0].split()
            if not email_ids:
                print("📭 No new emails.")
                return

            print(f"📧 Found {len(email_ids)} unread emails.")

            for email_id in email_ids:
                self.process_email(email_id)

        except Exception as e:
            print(f"❌ Error checking emails: {e}")
            # Try to reconnect next time
            self.mail = None

    def process_email(self, email_id):
        """Process a single email"""
        try:
            _, msg_data = self.mail.fetch(email_id, '(RFC822)')
            email_body = msg_data[0][1]
            message = email.message_from_bytes(email_body)

            subject = self._get_email_subject(message)
            print(f"\nProcessing email: {subject}")

            # Extract content from email body
            # This is a bit complex because we need to parse the email structure
            # to get the HTML part.
            html_content = self._get_html_part(message)
            
            if not html_content:
                print("⚠️ No HTML content found in email.")
                return

            # Process content
            data = self.extractor.process_html(html_content, base_url="from-email")
            
            if not data:
                print("❌ Failed to process HTML content")
                return

            print(f"📄 Title: {data['title']}")
            print(f"🖼️  Images: {len(data['images'])}")

            # Create EPUB
            epub_path = self.builder.create_epub(
                data['title'],
                data['content'],
                data['images'],
                "Forwarded Email"
            )

            # Send to Kindle
            if self.sender.send_epub(epub_path):
                print("✨ Verification successful for this email.")
            else:
                print("⚠️  EPUB created but email sending failed.") 

        except Exception as e:
            print(f"❌ Error processing email {email_id}: {e}")

    def _get_email_subject(self, message):
        subject, encoding = decode_header(message["Subject"])[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding if encoding else "utf-8")
        return subject

    def _get_html_part(self, message):
        if message.is_multipart():
            for part in message.walk():
                if part.get_content_type() == "text/html":
                    return part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8', errors='ignore')
        else:
            if message.get_content_type() == "text/html":
                 return message.get_payload(decode=True).decode(message.get_content_charset() or 'utf-8', errors='ignore')
        return None
    
    def run(self):
        print("🚀 Starting Email Watcher...")
        # Check immediately
        self.process_unread_emails()
        
        # Schedule check every minute
        schedule.every(1).minutes.do(self.process_unread_emails)
        
        while True:
            schedule.run_pending()
            time.sleep(1)

if __name__ == "__main__":
    # Check config
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        print("❌ Error: GMAIL_USER and GMAIL_APP_PASSWORD must be set in config/environment.")
        exit(1)

    watcher = EmailWatcher()
    watcher.run()
