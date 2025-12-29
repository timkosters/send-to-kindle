#!/usr/bin/env python3
"""
Simple Kindle Newsletter Web App - No Email Setup Required!

This version creates EPUB files locally. You manually email them to your Kindle.
Perfect for users who don't want to set up email automation.
"""

from flask import Flask, render_template_string, request, send_file, flash, redirect, url_for
import os
import requests
from readability import Document
from bs4 import BeautifulSoup
import ebooklib
from ebooklib import epub
from PIL import Image
from datetime import datetime
from io import BytesIO

from config import (
    OUTPUT_DIR,
    MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT, IMAGE_QUALITY
)

app = Flask(__name__)
# Use environment variable for secret key, fallback to random bytes for security
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

# HTML template for the simple web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Send to Kindle</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
            line-height: 1.6;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #555;
        }
        input[type="url"] {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
            box-sizing: border-box;
        }
        input[type="url"]:focus {
            border-color: #007bff;
            outline: none;
        }
        .btn {
            background: #007bff;
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            width: 100%;
            transition: background 0.3s;
        }
        .btn:hover {
            background: #0056b3;
        }
        .btn:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        .alert {
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .alert-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .alert-error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .result {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 5px;
            margin-top: 20px;
        }
        .download-btn {
            background: #28a745;
            color: white;
            padding: 15px 30px;
            text-decoration: none;
            border-radius: 5px;
            display: inline-block;
            margin: 10px 0;
            font-weight: bold;
        }
        .download-btn:hover {
            background: #218838;
            color: white;
        }
        .instructions {
            background: #e3f2fd;
            padding: 20px;
            border-radius: 5px;
            margin-top: 20px;
            border-left: 4px solid #2196F3;
        }
        .instructions h3 {
            margin-top: 0;
            color: #1976D2;
        }
        .examples {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 5px;
            margin-top: 20px;
        }
        .examples h3 {
            margin-top: 0;
        }
        .loading {
            display: none;
            text-align: center;
            margin-top: 20px;
        }
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #007bff;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            display: inline-block;
            margin-right: 10px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📖 Newsletter to Kindle</h1>

        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ 'success' if category == 'success' else 'error' }}">
                        {{ message }}
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        {% if epub_file %}
        <div class="result">
            <h2>✅ Success!</h2>
            <p><strong>{{ title }}</strong> converted to EPUB format with {{ images }} images.</p>

            <a href="/download/{{ epub_file }}" class="download-btn">
                📥 Download EPUB File
            </a>

            <div class="instructions">
                <h3>📧 Send to Kindle:</h3>
                <ol>
                    <li>Download the EPUB file above</li>
                    <li>Email it as an attachment to: <strong>{{ kindle_email }}</strong></li>
                    <li>Subject: "Convert" (or anything)</li>
                    <li>File appears on your Kindle in 2-5 minutes!</li>
                </ol>
                <p><small>Make sure your email address is approved in Amazon's "Send to Kindle" settings.</small></p>
            </div>
        </div>
        {% endif %}

        <form method="POST" action="/" onsubmit="showLoading()">
            <div class="form-group">
                <label for="url">Newsletter URL:</label>
                <input type="url"
                       id="url"
                       name="url"
                       placeholder="https://example.com/newsletter-article"
                       required
                       value="{{ request.form.get('url', '') }}">
            </div>

            <button type="submit" class="btn" id="submitBtn">
                🚀 Convert to EPUB
            </button>
        </form>

        <div class="loading" id="loading">
            <div class="spinner"></div>
            Converting newsletter... This may take a minute.
        </div>

        <div class="examples">
            <h3>💡 Examples</h3>
            <p>Works with any newsletter or article:</p>
            <ul>
                <li><strong>Substack:</strong> <code>https://author.substack.com/p/article-title</code></li>
                <li><strong>Medium:</strong> <code>https://medium.com/@author/article-title</code></li>
                <li><strong>News sites:</strong> <code>https://nytimes.com/article</code></li>
                <li><strong>Any blog:</strong> Any article URL with readable content</li>
            </ul>
        </div>
    </div>

    <script>
        function showLoading() {
            document.getElementById('loading').style.display = 'block';
            document.getElementById('submitBtn').disabled = true;
            document.getElementById('submitBtn').textContent = 'Converting...';
        }
    </script>
</body>
</html>
"""

class SimpleNewsletterProcessor:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        os.makedirs(OUTPUT_DIR, exist_ok=True)

    def extract_images_from_original_html(self, soup, base_url):
        """Extract image URLs from original HTML content areas"""
        images = []

        # Common selectors for newsletter content areas
        content_selectors = [
            'div[itemprop="articleBody"]',
            '.post-content',
            '.entry-content',
            '.article-content',
            '.body',
            'article',
            '.post',
            '[data-testid="post-content"]',
            '.substack-post-content',
            '.post-body',
            '.article-body',
            '.content',
            '.entry',
            '.main-content'
        ]

        # Find the main content area
        content_area = None
        for selector in content_selectors:
            content_area = soup.select_one(selector)
            if content_area:
                print(f"📍 Found content area: {selector}")
                break

        # If no specific content area found, use the whole body
        if not content_area:
            content_area = soup.find('body') or soup
            print("📍 Using full body for image extraction")

        # Extract images from content area
        img_tags = content_area.find_all('img')
        print(f"🖼️  Found {len(img_tags)} images in content area")

        for img in img_tags:
            img_url = None

            # Try different image sources
            if img.get('src'):
                img_url = img['src']
            elif img.get('data-src'):
                img_url = img['data-src']
            elif img.get('srcset'):
                srcset_parts = img['srcset'].split(',')
                if srcset_parts:
                    img_url = srcset_parts[0].split()[0]
            elif img.get('data-srcset'):
                srcset_parts = img['data-srcset'].split(',')
                if srcset_parts:
                    img_url = srcset_parts[0].split()[0]

            if img_url:
                img_url = img_url.strip()
                if not img_url.startswith('http'):
                    img_url = urljoin(base_url, img_url)

                # Skip icons, logos, etc.
                if not self.is_image_worth_downloading(img_url):
                    continue

                images.append(img_url)

        return images

    def is_image_worth_downloading(self, url):
        """Check if an image URL is worth downloading (not an icon/logo)"""
        url_lower = url.lower()
        skip_patterns = [
            'icon', 'logo', 'avatar', 'favicon', 'social', 'share',
            'button', 'sprite', 'badge', 'pixel', 'tracking'
        ]

        for pattern in skip_patterns:
            if pattern in url_lower:
                return False
        return True

    def insert_images_into_content(self, soup, images):
        """Insert image references into the clean HTML content"""
        if not images:
            return

        # Find good places to insert images (paragraphs, headings)
        content_elements = soup.find_all(['p', 'h2', 'h3', 'h4', 'div'])
        content_elements = [elem for elem in content_elements if len(elem.get_text().strip()) > 50]

        # Insert images at reasonable intervals
        if content_elements:
            images_per_content = max(1, len(images) // len(content_elements))
            image_index = 0

            for i, elem in enumerate(content_elements):
                if image_index >= len(images):
                    break

                # Insert an image after this element
                if i % max(1, len(content_elements) // len(images)) == 0:
                    img_tag = soup.new_tag('img')
                    img_tag['src'] = f"images/{images[image_index]['filename']}"
                    img_tag['style'] = 'max-width: 100%; height: auto; display: block; margin: 1em auto;'

                    # Insert after the current element
                    elem.insert_after(img_tag)
                    image_index += 1

        print(f"📝 Inserted {image_index} image references into content")

    def process_url(self, url):
        """Process a newsletter URL and return EPUB info"""
        try:
            print(f"🌐 Fetching: {url}")

            # Fetch content
            response = self.session.get(url, timeout=15)
            response.raise_for_status()

            # Parse original HTML to find images
            original_soup = BeautifulSoup(response.text, 'html.parser')

            # Extract images from original HTML content areas
            content_images = self.extract_images_from_original_html(original_soup, url)

            # Extract clean content with readability
            doc = Document(response.text)
            title = doc.title() or "Newsletter Article"

            # Get clean HTML
            soup = BeautifulSoup(doc.summary(), 'html.parser')

            # Process images from original HTML
            images = []
            print(f"🔍 Found {len(content_images)} images in original content")

            for i, img_url in enumerate(content_images):
                print(f"🖼️  Processing image {i+1}: {img_url}")

                try:
                    img_data = self.download_image(img_url)
                    if img_data:
                        filename = f"image_{i}.jpg"
                        images.append({
                            'filename': filename,
                            'data': img_data
                        })
                        print(f"✅ Downloaded image {i+1}: {len(img_data)} bytes")
                    else:
                        print(f"❌ Failed to download image {i+1}")
                except Exception as e:
                    print(f"❌ Error processing image {i+1} ({img_url}): {e}")

            # Insert image references into the clean HTML
            if images:
                self.insert_images_into_content(soup, images)

            print(f"📊 Successfully processed {len(images)} images")

            # Create EPUB
            epub_path = self.create_epub(title, str(soup), images, url)
            if not epub_path:
                raise Exception("Failed to create EPUB")

            # Try to send to Kindle if email is configured
            sent_to_kindle = self.send_to_kindle(epub_path)

            return {
                'success': True,
                'title': title,
                'epub_file': os.path.basename(epub_path),
                'images': len(images),
                'sent_to_kindle': sent_to_kindle
            }

        except Exception as e:
            print(f"❌ Error processing {url}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def download_image(self, url):
        """Download and optimize image for Kindle"""
        try:
            # Skip very small images or icons
            if 'icon' in url.lower() or 'favicon' in url.lower() or 'logo' in url.lower():
                print(f"⏭️  Skipping icon/logo: {url}")
                return None

            print(f"⬇️  Downloading: {url}")
            response = self.session.get(url, timeout=15, allow_redirects=True)
            response.raise_for_status()

            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            if not content_type.startswith('image/'):
                print(f"⏭️  Not an image (content-type: {content_type})")
                return None

            # Check content length (skip very small images)
            content_length = len(response.content)
            if content_length < 1000:  # Less than 1KB
                print(f"⏭️  Image too small ({content_length} bytes)")
                return None

            img = Image.open(BytesIO(response.content))

            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')

            # Resize if too large
            if img.width > MAX_IMAGE_WIDTH or img.height > MAX_IMAGE_HEIGHT:
                img.thumbnail((MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT), Image.Resampling.LANCZOS)

            output = BytesIO()
            img.save(output, format='JPEG', quality=IMAGE_QUALITY, optimize=True)
            processed_data = output.getvalue()

            print(f"✅ Processed image: {img.width}x{img.height} → {len(processed_data)} bytes")
            return processed_data

        except Exception as e:
            print(f"❌ Error processing image {url}: {e}")
            return None

    def create_epub(self, title, content, images, source_url):
        """Create EPUB file from content"""
        try:
            book = epub.EpubBook()
            book.set_identifier(f'simple_{datetime.now().timestamp()}')
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
                print(f"📚 Added image to EPUB: images/{img['filename']}")

            # Create chapter
            chapter = epub.EpubHtml(
                title=title,
                file_name='content.xhtml',
                lang='en'
            )

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
            book.toc = [chapter]
            book.add_item(epub.EpubNcx())
            book.add_item(epub.EpubNav())
            book.spine = ['nav', chapter]

            # Save EPUB
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_title = safe_title[:30]
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{safe_title}_{timestamp}.epub"
            filepath = os.path.join(OUTPUT_DIR, filename)

            epub.write_epub(filepath, book)
            print(f"📖 Created EPUB: {filename}")
            return filepath
        except Exception as e:
            print(f"❌ Error creating EPUB: {e}")
            return None

    def send_to_kindle(self, epub_path):
        """Send EPUB file to Kindle email (optional)"""
        # Get SMTP settings (optional - if not set, just skip sending)
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        smtp_user = os.getenv('SMTP_USER')
        smtp_password = os.getenv('SMTP_PASSWORD')

        if not smtp_user or not smtp_password:
            print("ℹ️  Email not configured - EPUB created successfully")
            return False

        try:
            msg = MIMEMultipart()
            msg['From'] = smtp_user
            msg['To'] = KINDLE_EMAIL
            msg['Subject'] = 'Convert'

            with open(epub_path, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename="{os.path.basename(epub_path)}"'
                )
                msg.attach(part)

            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
            server.quit()

            print(f"📤 Successfully sent to Kindle: {KINDLE_EMAIL}")
            return True
        except Exception as e:
            print(f"❌ Error sending to Kindle: {e}")
            return False

# Create processor instance
processor = SimpleNewsletterProcessor()

@app.route('/', methods=['GET', 'POST'])
def index():
    epub_info = None

    if request.method == 'POST':
        url = request.form.get('url')
        if not url:
            flash('Please enter a URL', 'error')
            return redirect(url_for('index'))

        # Process the URL
        print("🚀 Starting URL processing...")
        result = processor.process_url(url)
        print(f"📊 Processing result: {result}")

        if result['success']:
            message = f"✅ '{result['title']}' converted successfully! Found {result['images']} images."
            if result.get('sent_to_kindle'):
                message += " 📤 Sent to Kindle automatically!"
            else:
                message += " 💾 Download available below."
            flash(message, 'success')
            epub_info = result
        else:
            flash(f"❌ Error: {result['error']}", 'error')

    # Get Kindle email from config (optional display)
    kindle_email = os.getenv('KINDLE_EMAIL', 'your-kindle@kindle.com')

    return render_template_string(HTML_TEMPLATE,
                                epub_file=epub_info.get('epub_file') if epub_info else None,
                                title=epub_info.get('title') if epub_info else None,
                                images=epub_info.get('images') if epub_info else None,
                                kindle_email=kindle_email)

@app.route('/download/<filename>')
def download(filename):
    """Serve the EPUB file for download"""
    filepath = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True, download_name=filename)
    else:
        flash('File not found', 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    port = 8000  # Changed from 5000 to avoid conflicts
    print("🚀 Starting Simple Kindle Newsletter Web App...")
    print(f"📱 Open your browser to: http://localhost:{port}")
    print("❌ Close this window to stop the server")
    print()
    print("🎯 This version creates EPUB files locally.")
    print("   Download them and email to your Kindle manually.")
    print()

    app.run(debug=True, host='0.0.0.0', port=port)
