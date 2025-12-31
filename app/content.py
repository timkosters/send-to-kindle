import requests
from bs4 import BeautifulSoup
from readability import Document
from urllib.parse import urljoin
from .images import ImageProcessor

class ContentExtractor:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.image_processor = ImageProcessor(self.session)

    def process_url(self, url):
        """Fetch and process a URL"""
        print(f"🌐 Fetching: {url}")
        
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            # 1. Parse original HTML to find potential high-res images
            original_soup = BeautifulSoup(response.text, 'html.parser')
            
            # 2. Extract content using Readability
            doc = Document(response.text)
            title = doc.title()
            clean_html = doc.summary()
            
            # 3. Create Clean Soup
            soup = BeautifulSoup(clean_html, 'html.parser')
            
            # 4. Extract and Download Images
            # We look at the original soup to find the "best" image URLs
            image_urls = self.image_processor.extract_images_from_original_html(original_soup, url)
            
            processed_images = []
            print(f"🔍 Found {len(image_urls)} potential images")
            
            for i, img_url in enumerate(image_urls):
                img_data = self.image_processor.download_image(img_url, referrer=url)
                if img_data:
                    filename = f"image_{i}.jpg"
                    processed_images.append({
                        'filename': filename,
                        'data': img_data,
                        'original_url': img_url
                    })
            
            # 5. Insert Images into Clean Content
            self._insert_images_into_content(soup, processed_images)
            
            return {
                'title': title,
                'content': str(soup),
                'images': processed_images,
                'url': url
            }
            
        except Exception as e:
            print(f"❌ Error processing URL {url}: {e}")
            raise e

    def process_html(self, html_content, base_url=""):
        """Process raw HTML content (e.g. from email)"""
        try:
            # 1. Parse original HTML
            original_soup = BeautifulSoup(html_content, 'html.parser')
            
            # 2. Extract content using Readability
            doc = Document(html_content)
            title = doc.title()
            clean_html = doc.summary()
            
            # 3. Create Clean Soup
            soup = BeautifulSoup(clean_html, 'html.parser')
            
            # 4. Extract and Download Images
            image_urls = self.image_processor.extract_images_from_original_html(original_soup, base_url)
            
            processed_images = []
            print(f"🔍 Found {len(image_urls)} potential images in HTML")
            
            for i, img_url in enumerate(image_urls):
                img_data = self.image_processor.download_image(img_url, referrer=base_url)
                if img_data:
                    filename = f"image_{i}.jpg"
                    processed_images.append({
                        'filename': filename,
                        'data': img_data,
                        'original_url': img_url
                    })
            
            # 5. Insert Images into Clean Content
            self._insert_images_into_content(soup, processed_images)
            
            return {
                'title': title,
                'content': str(soup),
                'images': processed_images,
                'url': base_url
            }
        except Exception as e:
            print(f"❌ Error processing HTML: {e}")
            raise e

    def _insert_images_into_content(self, soup, images):
        """
        Update existing img tags in the Readability-cleaned content with our downloaded images.
        This preserves the original image positions from the article.
        """
        if not images:
            return

        # Build a lookup map from original URL to our processed image
        url_to_image = {}
        for img in images:
            if 'original_url' in img:
                url_to_image[img['original_url']] = img

        # Find all existing img tags in the cleaned content
        img_tags = soup.find_all('img')
        images_updated = 0

        for img_tag in img_tags:
            # Get the original src
            original_src = img_tag.get('src') or img_tag.get('data-src')
            if not original_src:
                continue

            # Check if we have a downloaded version of this image
            matching_image = url_to_image.get(original_src)
            
            if matching_image:
                # Update the src to point to our local copy
                img_tag['src'] = f"images/{matching_image['filename']}"
                img_tag['alt'] = img_tag.get('alt', 'Article image')
                # Remove lazy-loading attributes
                for attr in ['data-src', 'data-srcset', 'srcset', 'loading']:
                    if attr in img_tag.attrs:
                        del img_tag.attrs[attr]
                images_updated += 1
            else:
                # Image not in our downloaded set - remove it to avoid broken images
                img_tag.decompose()

        print(f"📝 Updated {images_updated} image references in content (preserved positions)")
