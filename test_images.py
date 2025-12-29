#!/usr/bin/env python3
"""
Test script to debug image processing in newsletters
"""

import requests
from readability import Document
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def test_image_extraction(url):
    """Test extracting images from a newsletter URL"""
    print(f"🔍 Testing image extraction for: {url}")
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
        print("✅ Page fetched successfully")

        # Extract content
        print("📄 Extracting content...")
        doc = Document(response.text)
        title = doc.title() or "Test Article"
        print(f"📖 Title: {title}")

        # Get clean HTML
        soup = BeautifulSoup(doc.summary(), 'html.parser')

        # Find all images
        img_tags = soup.find_all('img')
        print(f"🖼️  Found {len(img_tags)} img tags")

        for i, img in enumerate(img_tags):
            print(f"\nImage {i+1}:")
            print(f"  Attributes: {list(img.attrs.keys())}")

            # Check different sources
            sources = []
            if img.get('src'):
                sources.append(('src', img['src']))
            if img.get('data-src'):
                sources.append(('data-src', img['data-src']))
            if img.get('srcset'):
                srcset_parts = img['srcset'].split(',')
                if srcset_parts:
                    sources.append(('srcset', srcset_parts[0].split()[0]))
            if img.get('data-srcset'):
                srcset_parts = img['data-srcset'].split(',')
                if srcset_parts:
                    sources.append(('data-srcset', srcset_parts[0].split()[0]))

            print(f"  Sources found: {len(sources)}")
            for source_name, source_url in sources:
                print(f"    {source_name}: {source_url}")
                if not source_url.startswith('http'):
                    full_url = urljoin(url, source_url)
                    print(f"      → Full URL: {full_url}")

                    # Try to fetch the image
                    try:
                        img_response = session.get(full_url, timeout=10)
                        if img_response.status_code == 200:
                            content_type = img_response.headers.get('content-type', '')
                            size = len(img_response.content)
                            print(f"      ✅ Fetchable: {content_type}, {size} bytes")
                        else:
                            print(f"      ❌ HTTP {img_response.status_code}")
                    except Exception as e:
                        print(f"      ❌ Error: {e}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    # Test with a sample URL - replace with the URL the user tested
    test_url = input("Enter a newsletter URL to test: ").strip()
    if test_url:
        test_image_extraction(test_url)
    else:
        print("No URL provided. Exiting.")
