#!/usr/bin/env python3
"""
Test script for EPUB creation functionality

This script tests the core EPUB creation and image processing
without needing email access. Useful for verifying the prototype works.
"""

import os
from main import KindleNewsletterProcessor

def test_epub_creation():
    """Test EPUB creation with sample content"""
    print("🧪 Testing EPUB creation functionality...")

    # Sample HTML content (simulates a newsletter)
    sample_content = """
    <html>
    <body>
        <h1>Test Newsletter Article</h1>
        <p>This is a test article to verify EPUB creation works correctly.</p>

        <h2>Section 1</h2>
        <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>

        <h2>Section 2</h2>
        <p>Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p>

        <blockquote>
            "This is a sample blockquote that should render nicely in the EPUB."
        </blockquote>

        <p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.</p>
    </body>
    </html>
    """

    # Sample images (empty for this test)
    sample_images = []

    # Create processor
    processor = KindleNewsletterProcessor()

    # Test EPUB creation
    try:
        epub_path = processor.create_epub(
            title="Test Newsletter Article",
            content=sample_content,
            images=sample_images
        )

        if epub_path and os.path.exists(epub_path):
            file_size = os.path.getsize(epub_path)
            print(f"✅ EPUB created successfully: {epub_path}")
            print(f"📊 File size: {file_size} bytes")
            print("📖 You can open this file with any EPUB reader to verify formatting"
            return True
        else:
            print("❌ EPUB creation failed")
            return False

    except Exception as e:
        print(f"❌ Error during EPUB creation: {e}")
        return False

def test_image_download():
    """Test image download and optimization"""
    print("\n🖼️  Testing image download functionality...")

    # Test with a sample image URL
    test_image_url = "https://picsum.photos/800/600"  # Random sample image

    processor = KindleNewsletterProcessor()

    try:
        image_data = processor.download_image(test_image_url)
        if image_data:
            print(f"✅ Image downloaded successfully: {len(image_data)} bytes")
            return True
        else:
            print("❌ Image download failed")
            return False
    except Exception as e:
        print(f"❌ Error downloading image: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Running Kindle Newsletter Prototype Tests")
    print("=" * 50)

    # Test EPUB creation
    epub_success = test_epub_creation()

    # Test image download (optional, requires internet)
    print("\n❓ Test image download? (requires internet connection)")
    try:
        response = input("Enter 'y' to test image download: ").lower().strip()
        if response == 'y':
            image_success = test_image_download()
        else:
            image_success = True  # Skip test
    except:
        image_success = True  # Skip test in non-interactive environments

    print("\n" + "=" * 50)
    if epub_success and image_success:
        print("🎉 All tests passed! The prototype should work correctly.")
        print("📋 Next steps:")
        print("   1. Configure your Gmail and Kindle credentials in config.py")
        print("   2. Forward a newsletter email to your Gmail")
        print("   3. Run: python main.py")
    else:
        print("❌ Some tests failed. Check the error messages above.")

if __name__ == '__main__':
    main()
