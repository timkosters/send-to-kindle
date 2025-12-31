import requests
from PIL import Image
from io import BytesIO
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from .config import MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT, IMAGE_QUALITY

class ImageProcessor:
    def __init__(self, session=None):
        self.session = session or requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

    def extract_images_from_original_html(self, soup, base_url):
        """Extract image URLs from original HTML content areas - ported from simple_web_app.py"""
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

    def download_image(self, url, referrer=None):
        """Download and optimize image for Kindle"""
        try:
            # Skip very small images or icons
            if 'icon' in url.lower() or 'favicon' in url.lower() or 'logo' in url.lower():
                # print(f"⏭️  Skipping icon/logo: {url}")
                return None

            print(f"⬇️  Downloading: {url}")
            
            headers = {}
            if referrer:
                headers['Referer'] = referrer
            
            # Retry logic
            max_retries = 3
            response = None
            
            for attempt in range(max_retries):
                try:
                    response = self.session.get(url, timeout=15, allow_redirects=True, headers=headers)
                    if response.status_code == 200:
                        break
                except requests.RequestException as e:
                    if attempt == max_retries - 1:
                        raise e
                    continue
            
            response.raise_for_status()

            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            if not content_type.startswith('image/'):
                # print(f"⏭️  Not an image (content-type: {content_type})")
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
            
            # Skip if extremely small (likely pixel tracker) after processing
            if img.width < 10 or img.height < 10:
                print(f"⏭️  Image too small ({img.width}x{img.height})")
                return None

            output = BytesIO()
            img.save(output, format='JPEG', quality=IMAGE_QUALITY, optimize=True)
            processed_data = output.getvalue()

            print(f"✅ Processed image: {img.width}x{img.height} → {len(processed_data)} bytes")
            return processed_data

        except Exception as e:
            print(f"❌ Error processing image {url}: {e}")
            return None
