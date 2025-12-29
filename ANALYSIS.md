# Kindle Newsletter Service - Technical Analysis

## How ReadBetter.io and Similar Services Work

### Core Workflow

1. **User Registration**
   - User creates account and provides their Kindle email address
   - User adds service's email to their Kindle approved sender list (via Amazon account settings)
   - Service assigns user a unique forwarding email address

2. **Content Input Methods**
   - **Email Forwarding**: User forwards newsletters from their email to the service's unique address
   - **RSS/Feed Subscription**: Service polls RSS feeds (e.g., Substack) and automatically fetches new articles
   - **URL Submission**: User submits article URLs directly

3. **Content Processing Pipeline**
   - **Email Parsing**: Extract HTML/text content from forwarded emails
   - **Web Scraping**: Fetch article content from URLs (for RSS/URL submissions)
   - **Content Extraction**: Use libraries like `readability`, `newspaper3k`, or `beautifulsoup4` to extract main content, removing ads, navigation, etc.
   - **Image Processing**: Download images, optimize/resize for Kindle, embed in document
   - **Format Conversion**: Convert HTML → EPUB/MOBI format using tools like `ebooklib`, `calibre`, or `pandoc`

4. **Delivery to Kindle**
   - Send converted file as email attachment to user's Kindle email address
   - Use Amazon's "Send to Kindle" service (via email or API)
   - File appears in user's Kindle library, supports native features (highlights, notes, font adjustment)

### Why Native Format (EPUB/MOBI) vs PDF?

- **EPUB/MOBI**: Native Kindle format, supports:
  - Text reflow (adjustable font sizes)
  - Highlighting and notes
  - Dictionary lookup
  - Better image handling
  - Smaller file sizes
  
- **PDF**: Fixed layout, harder to read on small screens, limited highlighting, larger files

## Technical Architecture for Building Your Own

### System Components

```
┌─────────────────┐
│  User Interface │  (Web Dashboard)
└────────┬────────┘
         │
┌────────▼─────────────────────────────────────┐
│         Backend Service                      │
│  ┌──────────────────────────────────────┐   │
│  │  Email Receiver (IMAP/POP3/Webhook)  │   │
│  └──────────────┬───────────────────────┘   │
│                 │                            │
│  ┌──────────────▼───────────────────────┐   │
│  │  Content Extractor (HTML Parser)     │   │
│  └──────────────┬───────────────────────┘   │
│                 │                            │
│  ┌──────────────▼───────────────────────┐   │
│  │  Image Processor & Optimizer          │   │
│  └──────────────┬───────────────────────┘   │
│                 │                            │
│  ┌──────────────▼───────────────────────┐   │
│  │  EPUB/MOBI Converter                  │   │
│  └──────────────┬───────────────────────┘   │
│                 │                            │
│  ┌──────────────▼───────────────────────┐   │
│  │  Email Sender (SMTP)                  │   │
│  └───────────────────────────────────────┘   │
└──────────────────────────────────────────────┘
```

### Technology Stack Options

#### Backend (Python - Recommended)
- **Framework**: FastAPI, Flask, or Django
- **Email Processing**: 
  - `imaplib` (Python stdlib) for IMAP email reading
  - `email` (Python stdlib) for parsing emails
  - Alternative: Use services like SendGrid, Mailgun webhooks
- **Content Extraction**:
  - `readability-lxml` or `trafilatura` - Extract main content from HTML
  - `beautifulsoup4` - HTML parsing and manipulation
  - `newspaper3k` - Article extraction (includes image handling)
  - `html2text` - Convert HTML to clean text
- **E-book Conversion**:
  - `ebooklib` - Create EPUB files programmatically
  - `calibre` (via subprocess) - Convert to MOBI/AZW3
  - `pandoc` (via subprocess) - Universal document converter
- **Image Processing**:
  - `Pillow` (PIL) - Image optimization, resizing
  - `requests` - Download images from URLs
- **RSS Feed Processing**:
  - `feedparser` - Parse RSS/Atom feeds
- **Email Sending**:
  - `smtplib` (Python stdlib) or `sendgrid`, `boto3` (for AWS SES)

#### Alternative Stack (Node.js)
- **Framework**: Express.js, Next.js
- **Email**: `imap`, `mailparser`
- **Content**: `readability`, `jsdom`, `cheerio`
- **E-book**: `epub-gen`, `calibre` (via child_process)
- **Images**: `sharp`, `jimp`

### Key Implementation Details

#### 1. Email Reception
```python
# Pseudo-code for email processing
import imaplib
import email
from email.header import decode_header

# Connect to email server
mail = imaplib.IMAP4_SSL('imap.gmail.com')
mail.login('your-email@gmail.com', 'password')
mail.select('inbox')

# Search for unread emails
status, messages = mail.search(None, 'UNSEEN')

# Process each email
for msg_num in messages[0].split():
    # Fetch email
    status, msg_data = mail.fetch(msg_num, '(RFC822)')
    email_body = msg_data[0][1]
    email_message = email.message_from_bytes(email_body)
    
    # Extract content
    # Process and convert
    # Send to Kindle
```

#### 2. Content Extraction
```python
from readability import Document
import requests
from bs4 import BeautifulSoup

def extract_content(html_content):
    # Use readability to get main content
    doc = Document(html_content)
    clean_html = doc.summary()
    
    # Parse with BeautifulSoup
    soup = BeautifulSoup(clean_html, 'html.parser')
    
    # Extract images
    images = []
    for img in soup.find_all('img'):
        img_url = img.get('src')
        if img_url:
            images.append(download_and_optimize_image(img_url))
    
    return {
        'title': doc.title(),
        'content': str(soup),
        'images': images
    }
```

#### 3. EPUB Creation
```python
import ebooklib
from ebooklib import epub

def create_epub(title, content, images):
    book = epub.EpubBook()
    book.set_identifier('id123456')
    book.set_title(title)
    book.set_language('en')
    
    # Add content chapter
    chapter = epub.EpubHtml(title='Content', file_name='chap_01.xhtml', lang='en')
    chapter.content = content
    book.add_item(chapter)
    
    # Add images
    for img_path, img_data in images:
        img_item = epub.EpubItem(
            uid=f'img_{img_path}',
            file_name=f'images/{img_path}',
            media_type='image/jpeg',
            content=img_data
        )
        book.add_item(img_item)
    
    # Add default NCX and Nav file
    book.toc = [chapter]
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    
    # Define CSS
    style = 'body { font-family: Georgia, serif; }'
    nav_css = epub.EpubItem(
        uid="nav_css",
        file_name="style/nav.css",
        media_type="text/css",
        content=style
    )
    book.add_item(nav_css)
    
    # Create EPUB file
    epub.write_epub(f'{title}.epub', book)
```

#### 4. Send to Kindle
```python
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

def send_to_kindle(kindle_email, epub_file_path, sender_email):
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = kindle_email
    msg['Subject'] = 'Convert'
    
    # Attach EPUB file
    with open(epub_file_path, 'rb') as f:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename= {epub_file_path}'
        )
        msg.attach(part)
    
    # Send via SMTP
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, 'app_password')
    server.send_message(msg)
    server.quit()
```

#### 5. RSS Feed Processing (for Substack)
```python
import feedparser
import requests

def process_substack_rss(rss_url):
    feed = feedparser.parse(rss_url)
    
    articles = []
    for entry in feed.entries:
        # Fetch article content
        response = requests.get(entry.link)
        content = extract_content(response.text)
        
        articles.append({
            'title': entry.title,
            'content': content,
            'published': entry.published
        })
    
    return articles
```

### Substack-Specific Implementation

Substack newsletters can be accessed via RSS feeds:
- RSS URL format: `https://[publication].substack.com/feed`
- Each entry contains full article content in the RSS feed
- Images are typically hosted on Substack CDN

### Database Schema (Simplified)

```sql
Users:
- id
- email
- kindle_email
- forwarding_email (unique per user)
- created_at

Subscriptions:
- id
- user_id
- source_type (email, rss, url)
- source_value (RSS URL, email address, etc.)
- active
- created_at

Deliveries:
- id
- user_id
- article_title
- source
- epub_file_path
- sent_at
- status
```

### Deployment Considerations

1. **Email Service**: Use Gmail with App Passwords, or services like SendGrid/Mailgun
2. **Storage**: Store EPUB files temporarily (S3, local filesystem)
3. **Scheduling**: Use cron jobs or task queues (Celery, RQ) for RSS polling
4. **Scaling**: Queue-based architecture for processing multiple articles
5. **Error Handling**: Retry logic for failed conversions, email delivery failures

### Security & Privacy

- Encrypt stored Kindle email addresses
- Secure email credentials
- Handle user data according to GDPR/privacy regulations
- Rate limiting on email processing
- Validate email addresses before sending

### Cost Considerations

- Email sending: Free tier limits (Gmail: 500/day, SendGrid: 100/day free)
- Storage: Minimal for temporary file storage
- Hosting: VPS ($5-20/month) or serverless (AWS Lambda, Vercel)

## MVP Implementation Plan

### Phase 1: Core Functionality
1. User registration with Kindle email
2. Email forwarding setup (manual forwarding initially)
3. Email parsing and content extraction
4. EPUB conversion
5. Send to Kindle via email

### Phase 2: Enhancements
1. RSS feed support (Substack)
2. Image optimization
3. Web dashboard for managing subscriptions
4. Delivery history

### Phase 3: Advanced Features
1. Scheduled deliveries (daily/weekly digests)
2. Multiple article bundling
3. Custom formatting options
4. Mobile app or browser extension

## Quick Start Example

A minimal working example would involve:
1. Setting up email forwarding to a Gmail account
2. Python script that checks inbox periodically
3. Extracts content from emails
4. Converts to EPUB
5. Sends to Kindle email

This can be run as a simple cron job or background service.

