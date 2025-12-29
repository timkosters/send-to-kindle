#!/usr/bin/env python3
"""
Modern Web App for Kindle Newsletter Processing
"""

import os
from flask import Flask, render_template, request, flash, redirect, url_for, send_file
from app.content import ContentExtractor
from app.epub import EpubBuilder
from app.sender import KindleSender
from app.config import OUTPUT_DIR

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Register Webhooks
from app.webhooks import webhooks_bp
app.register_blueprint(webhooks_bp)

# Initialize Services
extractor = ContentExtractor()
builder = EpubBuilder()
sender = KindleSender()

@app.route('/', methods=['GET', 'POST'])
def index():
    epub_filename = None
    title = None
    image_count = 0
    email_sent = False

    if request.method == 'POST':
        url = request.form.get('url')
        if not url:
            flash('Please enter a URL', 'error')
            return redirect(url_for('index'))

        try:
            # 1. Extract
            data = extractor.process_url(url)
            title = data['title']
            image_count = len(data['images'])

            # 2. Build EPUB
            epub_path = builder.create_epub(
                data['title'],
                data['content'],
                data['images'],
                data['url']
            )

            # 3. Send
            email_sent = sender.send_epub(epub_path)
            
            if email_sent:
                flash(f"Successfully converted '{title}' and sent to Kindle!", 'success')
            else:
                flash(f"Converted '{title}' but email failed. You can download it below.", 'success')

            epub_filename = os.path.basename(epub_path)
            
            # Pass results to template
            return render_template('index.html', 
                                 epub_filename=epub_filename,
                                 title=title,
                                 image_count=image_count,
                                 email_sent=email_sent)

        except Exception as e:
            flash(f"Error processing URL: {str(e)}", 'error')
            return redirect(url_for('index'))

    return render_template('index.html')

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
    # Get port from environment variable (Railway sets this automatically)
    # Default to 8000 for local development
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 Starting Modern Kindle App on port {port}")
    # Use 0.0.0.0 to be accessible from outside
    app.run(debug=True, host='0.0.0.0', port=port)
