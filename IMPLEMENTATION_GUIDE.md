# Implementation Guide: Building Your Kindle Newsletter Service

## Quick Start: Minimal Viable Product

This guide walks you through building a working prototype that can:
1. Receive forwarded emails
2. Extract content and images
3. Convert to EPUB format
4. Send to your Kindle

## Project Structure

```
send-to-kindle/
├── requirements.txt
├── config.py
├── main.py
├── email_processor.py
├── content_extractor.py
├── epub_converter.py
├── kindle_sender.py
└── README.md
```

## Step-by-Step Implementation

### 1. Setup Environment

Create `requirements.txt`:
```
beautifulsoup4==4.12.2
ebooklib==0.18
feedparser==6.0.10
Pillow==10.1.0
readability-lxml==0.8.1
requests==2.31.0
lxml==4.9.3
```

### 2. Configuration (`config.py`)

```python
import os

# Email Configuration (for receiving forwarded emails)
EMAIL_HOST = os.getenv('EMAIL_HOST', 'imap.gmail.com')
EMAIL_USER = os.getenv('EMAIL_USER', 'your-email@gmail.com')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', 'your-app-password')  # Use App Password for Gmail

# Kindle Configuration
KINDLE_EMAIL = os.getenv('KINDLE_EMAIL', 'your-kindle@kindle.com')
SENDER_EMAIL = os.getenv('SENDER_EMAIL', 'your-email@gmail.com')  # Must be approved in Kindle settings

# SMTP Configuration (for sending to Kindle)
SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))

# Storage
OUTPUT_DIR = os.getenv('OUTPUT_DIR', './epub_files')
```

### 3. Content Extractor (`content_extractor.py`)

```python
from readability import Document
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin, urlparse
from io import BytesIO
from PIL import Image
import base64

class ContentExtractor:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def extract_from_html(self, html_content, base_url=None):
        """Extract main content from HTML"""
        doc = Document(html_content)
        clean_html = doc.summary()
        
        soup = BeautifulSoup(clean_html, 'html.parser')
        
        # Extract title
        title = doc.title() or soup.find('title')
        if title:
            title = title.get_text() if hasattr(title, 'get_text') else str(title)
        
        # Process images
        images = []
        for img in soup.find_all('img'):
            img_url = img.get('src') or img.get('data-src')
            if img_url:
                # Convert relative URLs to absolute
                if base_url and not img_url.startswith('http'):
                    img_url = urljoin(base_url, img_url)
                
                # Download and optimize image
                try:
                    img_data = self.download_and_optimize_image(img_url)
                    if img_data:
                        # Replace img src with data URI or local reference
                        img['src'] = f"images/{len(images)}.jpg"
                        images.append({
                            'filename': f"{len(images)}.jpg",
                            'data': img_data
                        })
                except Exception as e:
                    print(f"Failed to process image {img_url}: {e}")
                    img.decompose()  # Remove broken images
        
        return {
            'title': title.strip() if title else 'Untitled',
            'content': str(soup),
            'images': images
        }
    
    def download_and_optimize_image(self, url, max_width=800, max_height=1200, quality=85):
        """Download and optimize image for Kindle"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Open image
            img = Image.open(BytesIO(response.content))
            
            # Convert to RGB if necessary (for JPEG)
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Resize if too large
            if img.width > max_width or img.height > max_height:
                img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # Save to bytes
            output = BytesIO()
            img.save(output, format='JPEG', quality=quality, optimize=True)
            return output.getvalue()
        except Exception as e:
            print(f"Error processing image {url}: {e}")
            return None
    
    def extract_from_email(self, email_message):
        """Extract content from email message"""
        html_content = None
        text_content = None
        
        # Try to get HTML content
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                if content_type == 'text/html':
                    html_content = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                elif content_type == 'text/plain' and not text_content:
                    text_content = part.get_payload(decode=True).decode('utf-8', errors='ignore')
        else:
            content_type = email_message.get_content_type()
            if content_type == 'text/html':
                html_content = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
            elif content_type == 'text/plain':
                text_content = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
        
        # Prefer HTML, fallback to text
        if html_content:
            return self.extract_from_html(html_content)
        elif text_content:
            # Convert plain text to simple HTML
            return {
                'title': 'Email Content',
                'content': f'<html><body><pre>{text_content}</pre></body></html>',
                'images': []
            }
        
        return None
```

### 4. EPUB Converter (`epub_converter.py`)

```python
import ebooklib
from ebooklib import epub
from datetime import datetime
import os

class EPUBConverter:
    def __init__(self, output_dir='./epub_files'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def create_epub(self, title, content, images, author='Newsletter'):
        """Create EPUB file from content"""
        # Sanitize title for filename
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_title = safe_title[:50]  # Limit length
        
        # Create book
        book = epub.EpubBook()
        book.set_identifier(f'newsletter_{datetime.now().timestamp()}')
        book.set_title(title)
        book.set_language('en')
        book.add_author(author)
        
        # Add images
        image_items = {}
        for img in images:
            img_item = epub.EpubItem(
                uid=f'img_{img["filename"]}',
                file_name=f'images/{img["filename"]}',
                media_type='image/jpeg',
                content=img['data']
            )
            book.add_item(img_item)
            image_items[img['filename']] = img_item
        
        # Create chapter
        chapter = epub.EpubHtml(
            title=title,
            file_name='content.xhtml',
            lang='en'
        )
        
        # Add CSS for better formatting
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
            {content}
        </body>
        </html>
        '''
        
        book.add_item(chapter)
        
        # Add default NCX and Nav file
        book.toc = [chapter]
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())
        
        # Set spine
        book.spine = ['nav', chapter]
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{safe_title}_{timestamp}.epub"
        filepath = os.path.join(self.output_dir, filename)
        
        # Write EPUB
        epub.write_epub(filepath, book)
        
        return filepath
```

### 5. Kindle Sender (`kindle_sender.py`)

```python
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os

class KindleSender:
    def __init__(self, smtp_host, smtp_port, sender_email, sender_password):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
    
    def send_epub(self, kindle_email, epub_file_path, subject='Convert'):
        """Send EPUB file to Kindle email"""
        if not os.path.exists(epub_file_path):
            raise FileNotFoundError(f"EPUB file not found: {epub_file_path}")
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['To'] = kindle_email
        msg['Subject'] = subject
        
        # Attach EPUB file
        with open(epub_file_path, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename="{os.path.basename(epub_file_path)}"'
            )
            msg.attach(part)
        
        # Send email
        try:
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.send_message(msg)
            server.quit()
            print(f"Successfully sent {epub_file_path} to {kindle_email}")
            return True
        except Exception as e:
            print(f"Error sending to Kindle: {e}")
            return False
```

### 6. Email Processor (`email_processor.py`)

```python
import imaplib
import email
from email.header import decode_header
from content_extractor import ContentExtractor
from epub_converter import EPUBConverter
from kindle_sender import KindleSender
import config

class EmailProcessor:
    def __init__(self):
        self.extractor = ContentExtractor()
        self.converter = EPUBConverter(config.OUTPUT_DIR)
        self.sender = KindleSender(
            config.SMTP_HOST,
            config.SMTP_PORT,
            config.SENDER_EMAIL,
            config.EMAIL_PASSWORD
        )
        self.processed_uids = set()  # Track processed emails
    
    def connect(self):
        """Connect to email server"""
        self.mail = imaplib.IMAP4_SSL(config.EMAIL_HOST)
        self.mail.login(config.EMAIL_USER, config.EMAIL_PASSWORD)
        self.mail.select('inbox')
    
    def process_emails(self):
        """Process unread emails"""
        self.connect()
        
        # Search for unread emails
        status, messages = self.mail.search(None, 'UNSEEN')
        
        if status != 'OK':
            print("No emails found or error searching")
            return
        
        email_ids = messages[0].split()
        
        for email_id in email_ids:
            try:
                # Fetch email
                status, msg_data = self.mail.fetch(email_id, '(RFC822)')
                
                if status != 'OK':
                    continue
                
                email_body = msg_data[0][1]
                email_message = email.message_from_bytes(email_body)
                
                # Extract content
                content_data = self.extractor.extract_from_email(email_message)
                
                if not content_data:
                    print(f"Could not extract content from email {email_id}")
                    continue
                
                # Create EPUB
                epub_path = self.converter.create_epub(
                    title=content_data['title'],
                    content=content_data['content'],
                    images=content_data['images']
                )
                
                # Send to Kindle
                self.sender.send_epub(config.KINDLE_EMAIL, epub_path)
                
                # Mark as read (optional)
                # self.mail.store(email_id, '+FLAGS', '\\Seen')
                
                print(f"Processed: {content_data['title']}")
                
            except Exception as e:
                print(f"Error processing email {email_id}: {e}")
                continue
        
        self.mail.close()
        self.mail.logout()
```

### 7. Main Script (`main.py`)

```python
import time
import schedule
from email_processor import EmailProcessor
import config

def process_newsletters():
    """Main function to process newsletters"""
    processor = EmailProcessor()
    try:
        processor.process_emails()
    except Exception as e:
        print(f"Error in main processing: {e}")

if __name__ == '__main__':
    print("Starting Kindle Newsletter Processor...")
    print(f"Checking for new emails every 5 minutes...")
    
    # Run immediately
    process_newsletters()
    
    # Schedule to run every 5 minutes
    schedule.every(5).minutes.do(process_newsletters)
    
    # Keep running
    while True:
        schedule.run_pending()
        time.sleep(60)
```

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Create a `.env` file or set environment variables:
```bash
export EMAIL_USER='your-email@gmail.com'
export EMAIL_PASSWORD='your-app-password'  # Gmail App Password
export KINDLE_EMAIL='your-kindle@kindle.com'
export SENDER_EMAIL='your-email@gmail.com'
```

### 3. Gmail App Password Setup
1. Go to Google Account settings
2. Security → 2-Step Verification (enable if not already)
3. App Passwords → Generate new app password
4. Use this password in `EMAIL_PASSWORD`

### 4. Kindle Email Setup
1. Find your Kindle email: Amazon Account → Content & Devices → Devices
2. Add your sender email to approved senders list
3. Use this email in `KINDLE_EMAIL`

### 5. Test Email Forwarding
1. Forward a newsletter email to your Gmail account
2. Run the script: `python main.py`
3. Check your Kindle for the converted article

## RSS Feed Support (Substack)

Add this to handle RSS feeds:

```python
# rss_processor.py
import feedparser
from content_extractor import ContentExtractor
from epub_converter import EPUBConverter
from kindle_sender import KindleSender
import config
import requests

class RSSProcessor:
    def __init__(self):
        self.extractor = ContentExtractor()
        self.converter = EPUBConverter(config.OUTPUT_DIR)
        self.sender = KindleSender(
            config.SMTP_HOST,
            config.SMTP_PORT,
            config.SENDER_EMAIL,
            config.EMAIL_PASSWORD
        )
        self.processed_urls = set()
    
    def process_substack_feed(self, rss_url):
        """Process Substack RSS feed"""
        feed = feedparser.parse(rss_url)
        
        for entry in feed.entries:
            article_url = entry.link
            
            # Skip if already processed
            if article_url in self.processed_urls:
                continue
            
            try:
                # Fetch article
                response = requests.get(article_url)
                response.raise_for_status()
                
                # Extract content
                content_data = self.extractor.extract_from_html(
                    response.text,
                    base_url=article_url
                )
                
                # Create EPUB
                epub_path = self.converter.create_epub(
                    title=content_data['title'],
                    content=content_data['content'],
                    images=content_data['images']
                )
                
                # Send to Kindle
                self.sender.send_epub(config.KINDLE_EMAIL, epub_path)
                
                # Mark as processed
                self.processed_urls.add(article_url)
                
                print(f"Processed: {content_data['title']}")
                
            except Exception as e:
                print(f"Error processing {article_url}: {e}")

# Usage
if __name__ == '__main__':
    processor = RSSProcessor()
    # Substack RSS URL format: https://[publication].substack.com/feed
    processor.process_substack_feed('https://your-substack.substack.com/feed')
```

## Next Steps

1. **Add Web Interface**: Use Flask/FastAPI to create a dashboard
2. **Database**: Store user preferences and delivery history
3. **Scheduling**: Add daily/weekly digest options
4. **Multiple Sources**: Support multiple RSS feeds and email addresses
5. **Error Handling**: Add retry logic and error notifications
6. **Testing**: Test with various newsletter formats

## Troubleshooting

- **Email not received**: Check spam folder, verify sender email is approved
- **Images missing**: Check image URLs are accessible, may need to handle authentication
- **Formatting issues**: Adjust CSS in EPUB converter
- **Conversion errors**: Ensure all dependencies are installed correctly

