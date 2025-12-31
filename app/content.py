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
        """Insert image references into the clean HTML content - ported from simple_web_app.py"""
        if not images:
            return

        # Find good places to insert images (paragraphs, headings)
        content_elements = soup.find_all(['p', 'h2', 'h3', 'h4', 'div'])
        content_elements = [elem for elem in content_elements if len(elem.get_text().strip()) > 50]

        # Insert images at reasonable intervals
        if content_elements:
            images_inserted = 0
            
            # Calculate interval to spread images evenly
            if len(content_elements) > 0 and len(images) > 0:
                interval = max(1, len(content_elements) // len(images))
            else:
                interval = 1

            for i, elem in enumerate(content_elements):
                if images_inserted >= len(images):
                    break

                # Insert an image after this element at intervals
                if i % interval == 0:
                    image = images[images_inserted]
                    
                    # Create container
                    figure = soup.new_tag('figure')
                    figure['class'] = 'image-container'
                    
                    # Create img
                    img_tag = soup.new_tag('img')
                    img_tag['src'] = f"images/{image['filename']}"
                    img_tag['alt'] = "Article image"
                    
                    figure.append(img_tag)
                    
                    # Insert after the current element
                    elem.insert_after(figure)
                    images_inserted += 1

        print(f"📝 Inserted {images_inserted} image references into content")
