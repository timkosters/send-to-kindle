import os
from datetime import datetime
from ebooklib import epub
from .config import OUTPUT_DIR

class EpubBuilder:
    def __init__(self):
        pass

    def create_epub(self, title, content, images, source_url):
        """Create EPUB file from content"""
        try:
            book = epub.EpubBook()
            book.set_identifier(f'kindle_app_{datetime.now().timestamp()}')
            book.set_title(title)
            book.set_language('en')
            
            # Add author if we can find it, otherwise generic
            book.add_author('Send to Kindle')

            # Add images
            for img in images:
                img_item = epub.EpubItem(
                    uid=f'img_{img["filename"]}',
                    file_name=f'images/{img["filename"]}',
                    media_type='image/jpeg',
                    content=img['data']
                )
                book.add_item(img_item)

            # CSS
            style = '''
                body {
                    font-family: 'Bookerly', 'Georgia', 'Palatino', serif;
                    line-height: 1.6;
                    text-align: justify;
                    margin: 0;
                    padding: 0;
                }
                
                h1 {
                    font-family: 'Helvetica', 'Arial', sans-serif;
                    font-size: 1.8em;
                    line-height: 1.2;
                    margin: 1em 0 0.5em 0;
                    text-align: left;
                }
                
                h2, h3, h4 {
                    font-family: 'Helvetica', 'Arial', sans-serif;
                    margin-top: 1.5em;
                    margin-bottom: 0.5em;
                }
                
                p {
                    margin-bottom: 1em;
                    text-indent: 0;
                }
                
                a {
                    color: #0000EE;
                    text-decoration: none;
                }
                
                img {
                    max-width: 100%;
                    height: auto;
                    display: block;
                    margin: 1em auto;
                }
                
                figure {
                    margin: 1em 0;
                    text-align: center;
                }
                
                .source-url {
                    font-family: 'Helvetica', 'Arial', sans-serif;
                    font-size: 0.8em;
                    color: #666;
                    margin-bottom: 2em;
                    padding: 1em;
                    background: #f9f9f9;
                    border-top: 1px solid #eee;
                    border-bottom: 1px solid #eee;
                }
                
                blockquote {
                    margin: 1em 2em;
                    padding-left: 1em;
                    border-left: 3px solid #ccc;
                    font-style: italic;
                }
            '''
            
            css_item = epub.EpubItem(
                uid="style_nav",
                file_name="style/nav.css",
                media_type="text/css",
                content=style
            )
            book.add_item(css_item)

            # Create chapter
            chapter = epub.EpubHtml(
                title=title,
                file_name='content.xhtml',
                lang='en'
            )
            chapter.add_item(css_item)

            chapter.content = f'''
            <html>
            <head>
                <link rel="stylesheet" type="text/css" href="style/nav.css" />
            </head>
            <body>
                <h1>{title}</h1>
                <div class="source-url">
                    <strong>Source:</strong> <a href="{source_url}">{source_url}</a>
                </div>
                <hr/>
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
            safe_title = safe_title[:50]
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{safe_title}_{timestamp}.epub"
            filepath = os.path.join(OUTPUT_DIR, filename)

            epub.write_epub(filepath, book)
            print(f"📖 Created EPUB: {filename}")
            return filepath
            
        except Exception as e:
            print(f"❌ Error creating EPUB: {e}")
            raise e
