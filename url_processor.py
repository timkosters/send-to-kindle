#!/usr/bin/env python3
"""
URL-Based Kindle Newsletter Processor

Send newsletter URLs via email to yourself, and this script will:
1. Check Gmail for emails containing URLs
2. Fetch newsletter content from URLs
3. Convert to EPUB
4. Send to Kindle

USAGE:
1. Send yourself an email with a newsletter URL in the body
2. Run: python url_processor.py
3. Article appears on your Kindle!

This is simpler than forwarding full newsletters.
"""

import os
import re
import imaplib
import email
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from urllib.parse import urljoin
from datetime import datetime
from io import BytesIO

from readability import Document
from bs4 import BeautifulSoup
import ebooklib
from ebooklib import epub
from PIL import Image
import requests

from config import (
    GMAIL_USER, GMAIL_APP_PASSWORD, KINDLE_EMAIL,
    IMAP_HOST, SMTP_HOST, SMTP_PORT, OUTPUT_DIR,
    MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT, IMAGE_QUALITY
)

class URLNewsletterProcessor:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        os.makedirs(OUTPUT_DIR, exist_ok=True)

    def connect_gmail(self):
        """Connect to Gmail IMAP"""
        print("🔗 Connecting to Gmail...")
        try:
            self.mail = imaplib.IMAP4_SSL(IMAP_HOST)
            self.mail.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            self.mail.select('inbox')
            print("✅ Connected successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to connect: {e}")
            print("💡 Check your Gmail credentials in config.py")
            return False

    def extract_urls_from_emails(self):
        """Extract URLs from unread emails"""
        try:
            status, messages = self.mail.search(None, 'UNSEEN')
            if status != 'OK':
                print("❌ Failed to search emails")
                return []

            email_ids = messages[0].split()
            urls = []

            for email_id in email_ids:
                try:
                    # Fetch email
                    status, msg_data = self.mail.fetch(email_id, '(RFC822)')
                    if status != 'OK':
                        continue

                    email_body = msg_data[0][1]
                    email_message = email.message_from_bytes(email_body)

                    # Extract URLs from email body
                    email_urls = self.extract_urls_from_email(email_message)
                    urls.extend(email_urls)

                    print(f"📧 Found {len(email_urls)} URLs in email {email_id.decode()}")

                except Exception as e:
                    print(f"❌ Error processing email {email_id}: {e}")
                    continue

            return urls
        except Exception as e:
            print(f"❌ Error searching emails: {e}")
            return []

    def extract_urls_from_email(self, email_message):
        """Extract URLs from email content"""
        urls = []

        # Get text content from email
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                if content_type == 'text/plain':
                    try:
                        text_content = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        urls.extend(self.find_urls_in_text(text_content))
                    except:
                        continue
                elif content_type == 'text/html':
                    try:
                        html_content = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        urls.extend(self.find_urls_in_text(html_content))
                    except:
                        continue
        else:
            content_type = email_message.get_content_type()
            try:
                content = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
                urls.extend(self.find_urls_in_text(content))
            except:
                pass

        return urls

    def find_urls_in_text(self, text):
        """Find all URLs in text using regex"""
        # Regex pattern for URLs
        url_pattern = r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w)*)?)?'
        urls = re.findall(url_pattern, text)
        return [url for url in urls if self.is_newsletter_url(url)]

    def is_newsletter_url(self, url):
        """Check if URL looks like a newsletter/article"""
        # Basic filtering - avoid social media, ads, etc.
        exclude_patterns = [
            'facebook.com', 'twitter.com', 'instagram.com', 'linkedin.com',
            'google.com', 'youtube.com', 'amazon.com', 'ebay.com',
            'doubleclick', 'googlesyndication', 'adsystem'
        ]

        url_lower = url.lower()
        return not any(pattern in url_lower for pattern in exclude_patterns)

    def fetch_newsletter_content(self, url):
        """Fetch and extract content from newsletter URL"""
        try:
            print(f"🌐 Fetching: {url}")
            response = self.session.get(url, timeout=15)
            response.raise_for_status()

            # Extract content using readability
            doc = Document(response.text)
            title = doc.title() or "Newsletter Article"

            # Get clean HTML
            soup = BeautifulSoup(doc.summary(), 'html.parser')

            # Process images
            images = []
            for i, img in enumerate(soup.find_all('img')):
                img_url = img.get('src') or img.get('data-src')
                if img_url:
                    # Convert relative URLs to absolute
                    if not img_url.startswith('http'):
                        img_url = urljoin(url, img_url)

                    try:
                        # Download and optimize image
                        img_data = self.download_image(img_url)
                        if img_data:
                            filename = f"image_{i}.jpg"
                            img['src'] = filename
                            images.append({
                                'filename': filename,
                                'data': img_data
                            })
                            print(f"🖼️  Downloaded image: {img_url}")
                    except Exception as e:
                        print(f"⚠️  Failed to download image {img_url}: {e}")
                        img.decompose()  # Remove broken images

            return {
                'title': title.strip(),
                'content': str(soup),
                'images': images,
                'url': url
            }
        except Exception as e:
            print(f"❌ Error fetching {url}: {e}")
            return None

    def download_image(self, url):
        """Download and optimize image for Kindle"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            # Open image
            img = Image.open(BytesIO(response.content))

            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background

            # Resize if too large
            if img.width > MAX_IMAGE_WIDTH or img.height > MAX_IMAGE_HEIGHT:
                img.thumbnail((MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT), Image.Resampling.LANCZOS)

            # Save to bytes
            output = BytesIO()
            img.save(output, format='JPEG', quality=IMAGE_QUALITY, optimize=True)
            return output.getvalue()
        except Exception as e:
            print(f"❌ Error processing image {url}: {e}")
            return None

    def create_epub(self, title, content, images, source_url):
        """Create EPUB file from content"""
        try:
            # Create book
            book = epub.EpubBook()
            book.set_identifier(f'url_newsletter_{datetime.now().timestamp()}')
            book.set_title(title)
            book.set_language('en')

            # Add images
            for img in images:
                img_item = epub.EpubItem(
                    uid=f'img_{img["filename"]}',
                    file_name=f'images/{img["filename"]}',
                    media_type='image/jpeg',
                    content=img['data']
                )
                book.add_item(img_item)

            # Create chapter with content and source URL
            chapter = epub.EpubHtml(
                title=title,
                file_name='content.xhtml',
                lang='en'
            )

            # Add CSS and content
            chapter.content = f'''
            <html>
            <head>
                <style>
                    body {{
                        font-family: Georgia, serif;
                        line-height: 1.6;
                        max-width: 100%;
                        padding: 1em;
                    }}
                    .source-url {{
                        font-size: 0.8em;
                        color: #666;
                        margin-bottom: 2em;
                        padding: 1em;
                        background: #f5f5f5;
                        border-left: 4px solid #ccc;
                    }}
                    img {{
                        max-width: 100%;
                        height: auto;
                        display: block;
                        margin: 1em auto;
                    }}
                    h1, h2, h3 {{
                        margin-top: 1.5em;
                        margin-bottom: 0.5em;
                    }}
                    p {{
                        margin-bottom: 1em;
                        text-align: justify;
                    }}
                </style>
            </head>
            <body>
                <div class="source-url">
                    <strong>Source:</strong> <a href="{source_url}">{source_url}</a>
                </div>
                {content}
            </body>
            </html>
            '''

            book.add_item(chapter)

            # Add navigation
            book.toc = [chapter]
            book.add_item(epub.EpubNcx())
            book.add_item(epub.EpubNav())
            book.spine = ['nav', chapter]

            # Generate filename
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_title = safe_title[:30]  # Limit length
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{safe_title}_{timestamp}.epub"
            filepath = os.path.join(OUTPUT_DIR, filename)

            # Write EPUB
            epub.write_epub(filepath, book)
            print(f"📖 Created EPUB: {filename}")
            return filepath
        except Exception as e:
            print(f"❌ Error creating EPUB: {e}")
            return None

    def send_to_kindle(self, epub_path):
        """Send EPUB file to Kindle email"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = GMAIL_USER
            msg['To'] = KINDLE_EMAIL
            msg['Subject'] = 'Convert'

            # Attach EPUB
            with open(epub_path, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename="{os.path.basename(epub_path)}"'
                )
                msg.attach(part)

            # Send email
            server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
            server.starttls()
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.send_message(msg)
            server.quit()

            print(f"📤 Sent to Kindle: {KINDLE_EMAIL}")
            return True
        except Exception as e:
            print(f"❌ Error sending to Kindle: {e}")
            return False

    def process_urls(self):
        """Main processing function"""
        print("🚀 Starting URL Newsletter Processor")
        print(f"📧 Gmail: {GMAIL_USER}")
        print(f"📖 Kindle: {KINDLE_EMAIL}")
        print()

        # Connect to Gmail
        if not self.connect_gmail():
            return

        # Extract URLs from emails
        urls = self.extract_urls_from_emails()
        if not urls:
            print("📭 No URLs found in unread emails")
            self.mail.close()
            self.mail.logout()
            return

        print(f"🔗 Found {len(urls)} URLs to process:")
        for url in urls:
            print(f"  • {url}")
        print()

        # Process each URL
        processed_count = 0
        for url in urls:
            print(f"\n🔗 Processing: {url}")

            # Fetch newsletter content
            content_data = self.fetch_newsletter_content(url)
            if not content_data:
                continue

            print(f"📄 Title: {content_data['title']}")
            print(f"🖼️  Images: {len(content_data['images'])}")

            # Create EPUB
            epub_path = self.create_epub(
                content_data['title'],
                content_data['content'],
                content_data['images'],
                content_data['url']
            )
            if not epub_path:
                continue

            # Send to Kindle
            if self.send_to_kindle(epub_path):
                processed_count += 1
                print("✅ Successfully processed and sent to Kindle")
            else:
                print("❌ Failed to send to Kindle")

        # Cleanup
        self.mail.close()
        self.mail.logout()

        print(f"\n🎉 Processing complete! Sent {processed_count} articles to your Kindle")
        print("📖 Check your Kindle in a few minutes")

def main():
    """Main entry point"""
    # Check configuration
    if GMAIL_USER == 'your-gmail@gmail.com':
        print("❌ Please configure your Gmail address in config.py")
        print("   Set the GMAIL_USER environment variable or edit config.py")
        return

    if GMAIL_APP_PASSWORD == 'your-app-password':
        print("❌ Please configure your Gmail App Password in config.py")
        print("   Set the GMAIL_APP_PASSWORD environment variable or edit config.py")
        return

    if KINDLE_EMAIL == 'your-kindle@kindle.com':
        print("❌ Please configure your Kindle email in config.py")
        print("   Set the KINDLE_EMAIL environment variable or edit config.py")
        return

    # Run processor
    processor = URLNewsletterProcessor()
    processor.process_urls()

if __name__ == '__main__':
    main()
