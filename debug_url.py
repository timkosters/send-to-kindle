#!/usr/bin/env python3
"""
Debug a specific newsletter URL to see image processing
"""

import requests
from readability import Document
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import sys

def debug_newsletter_url(url):
    """Debug image extraction from a newsletter URL"""
    print(f"🔍 Debugging: {url}")
    print("=" * 60)

    try:
        # Fetch the page
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

        print("🌐 Fetching webpage...")
        response = session.get(url, timeout=15)
        response.raise_for_status()
        print(f"✅ Page fetched: {len(response.text)} characters")

        # Check images in original HTML first
        original_soup = BeautifulSoup(response.text, 'html.parser')
        original_imgs = original_soup.find_all('img')
        print(f"\n🖼️  Images in ORIGINAL HTML: {len(original_imgs)}")

        for i, img in enumerate(original_imgs[:5]):  # Show first 5
            img_url = img.get('src') or img.get('data-src', 'no-src')
            print(f"  Original img {i+1}: {img_url[:100]}...")

        # Extract content with readability
        print("\n📄 Extracting content...")
        doc = Document(response.text)
        title = doc.title() or "Untitled"
        print(f"📖 Title: {title}")

        # Get clean HTML
        soup = BeautifulSoup(doc.summary(), 'html.parser')
        print(f"📝 Clean content: {len(str(soup))} characters")

        # Find all images in clean content
        img_tags = soup.find_all('img')
        print(f"🖼️  Images in CLEAN content: {len(img_tags)}")

        # Check if we can find images in content areas
        if len(img_tags) == 0 and len(original_imgs) > 0:
            print("\n⚠️  PROBLEM: Readability removed all images!")
            print("💡 We need to extract images from original HTML content areas")

            # Common content selectors
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
                '.content'
            ]

            print("\n🔍 Looking for images in original HTML content areas...")

            for selector in content_selectors:
                content_area = original_soup.select_one(selector)
                if content_area:
                    imgs_in_content = content_area.find_all('img')
                    if imgs_in_content:
                        print(f"✅ Found {len(imgs_in_content)} images in {selector}")
                        for j, img in enumerate(imgs_in_content[:3]):
                            img_url = img.get('src') or img.get('data-src', 'no-src')
                            print(f"    Content img {j+1}: {img_url[:80]}...")
                        break

            # If still no images found, show what content areas exist
            if not any(original_soup.select_one(selector) for selector in content_selectors):
                print("❌ No standard content selectors found")
                print("🔍 Available content areas in page:")
                potential_areas = original_soup.find_all(['div', 'section', 'article'], class_=True)
                for area in potential_areas[:5]:
                    classes = ' '.join(area.get('class', []))
                    if len(classes) < 50:  # Skip very long class names
                        print(f"    .{classes}")

        for i, img in enumerate(img_tags):
            print(f"\n--- Image {i+1} ---")
            print(f"Tag attributes: {list(img.attrs.keys())}")

            # Check all possible image sources
            candidates = []

            if img.get('src'):
                candidates.append(('src', img['src']))
            if img.get('data-src'):
                candidates.append(('data-src', img['data-src']))
            if img.get('srcset'):
                srcset_parts = img['srcset'].split(',')
                if srcset_parts:
                    candidates.append(('srcset', srcset_parts[0].split()[0]))
            if img.get('data-srcset'):
                srcset_parts = img['data-srcset'].split(',')
                if srcset_parts:
                    candidates.append(('data-srcset', srcset_parts[0].split()[0]))

            print(f"Candidate URLs: {len(candidates)}")

            for source_type, img_url in candidates:
                print(f"  {source_type}: {img_url}")

                # Convert to absolute URL
                if not img_url.startswith('http'):
                    abs_url = urljoin(url, img_url)
                    print(f"    → Absolute: {abs_url}")
                else:
                    abs_url = img_url

                # Test if image is fetchable
                try:
                    img_response = session.get(abs_url, timeout=10)
                    if img_response.status_code == 200:
                        content_type = img_response.headers.get('content-type', 'unknown')
                        size = len(img_response.content)
                        print(f"    ✅ Fetchable: {content_type}, {size:,} bytes")

                        # Check if it's a real image
                        if content_type.startswith('image/') and size > 2000:
                            print(f"    🎯 GOOD: This is a valid image!")
                        elif size < 2000:
                            print(f"    ⚠️  SMALL: Might be an icon ({size} bytes)")
                        else:
                            print(f"    ❓  {content_type} - not sure if this is a display image")
                    else:
                        print(f"    ❌ HTTP {img_response.status_code}")

                except Exception as e:
                    print(f"    ❌ Error: {str(e)[:100]}")

        print(f"\n📊 Summary: {len(img_tags)} images found in article")
        print("💡 Look for images marked with '🎯 GOOD' - these should appear in your EPUB")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        url = sys.argv[1]
        debug_newsletter_url(url)
    else:
        print("Usage: python debug_url.py 'https://example.com/article'")
        print("\nExample:")
        print("python debug_url.py 'https://www.nytimes.com/article-url'")
