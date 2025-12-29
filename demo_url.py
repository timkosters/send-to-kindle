#!/usr/bin/env python3
"""
Demo: URL-Based Newsletter Processing

This demo shows how the URL method works without requiring Gmail setup.
It simulates processing a newsletter URL and creating an EPUB.
"""

import os
import requests
from readability import Document
from bs4 import BeautifulSoup
import ebooklib
from ebooklib import epub
from datetime import datetime

# Demo URL (a real newsletter article)
DEMO_URL = "https://www.nytimes.com/2024/01/15/technology/ai-chatbot-testing.html"

def demo_url_processing():
    """Demonstrate URL-based newsletter processing"""
    print("🎯 Demo: URL-Based Newsletter Processing")
    print("=" * 50)
    print(f"📖 Processing URL: {DEMO_URL}")
    print()

    try:
        # Step 1: Fetch content
        print("🌐 Step 1: Fetching content from URL...")
        response = requests.get(DEMO_URL, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }, timeout=10)
        response.raise_for_status()
        print("✅ Successfully fetched webpage")
        print()

        # Step 2: Extract clean content
        print("📄 Step 2: Extracting clean content...")
        doc = Document(response.text)
        title = doc.title() or "Newsletter Article"

        # Get clean HTML
        soup = BeautifulSoup(doc.summary(), 'html.parser')

        # Count images
        images = soup.find_all('img')
        print(f"📄 Title: {title}")
        print(f"🖼️  Found {len(images)} images in article")
        print()

        # Step 3: Create EPUB
        print("📖 Step 3: Creating EPUB file...")
        book = epub.EpubBook()
        book.set_identifier(f'demo_{datetime.now().timestamp()}')
        book.set_title(title)
        book.set_language('en')

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
                <strong>Source:</strong> <a href="{DEMO_URL}">{DEMO_URL}</a>
                <br><em>This is a demo - images are not downloaded in this version</em>
            </div>
            {str(soup)}
        </body>
        </html>
        '''

        book.add_item(chapter)
        book.toc = [chapter]
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())
        book.spine = ['nav', chapter]

        # Save EPUB
        os.makedirs('./demo_output', exist_ok=True)
        filename = f"demo_newsletter_{datetime.now().strftime('%H%M%S')}.epub"
        filepath = os.path.join('./demo_output', filename)

        epub.write_epub(filepath, book)
        print(f"✅ Created EPUB: {filepath}")

        # Step 4: Summary
        print()
        print("🎉 Demo Complete!")
        print(f"📖 EPUB saved to: {filepath}")
        print()
        print("💡 How this works in the real system:")
        print("   1. You email yourself a newsletter URL")
        print("   2. Script finds URLs in your emails")
        print("   3. Fetches fresh content (with images)")
        print("   4. Creates EPUB and sends to Kindle")
        print()
        print("🚀 Ready to try the real thing?")
        print("   1. Set up your Gmail credentials (see SETUP.md)")
        print("   2. Email yourself a newsletter URL")
        print("   3. Run: python url_processor.py")

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print()
        print("💡 This demo requires internet access to fetch the article.")

if __name__ == '__main__':
    demo_url_processing()
