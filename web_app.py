#!/usr/bin/env python3
"""
Modern Web App for Kindle Newsletter Processing

Multi-user version with Google OAuth authentication.
Each user can set their own Kindle email address.
"""

import os
from flask import Flask, render_template, request, flash, redirect, url_for, send_file
from flask_login import LoginManager, login_required, current_user
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Import our modules
from app.models import db, User
from app.auth import auth_bp, init_oauth
from app.content import ContentExtractor
from app.epub import EpubBuilder
from app.sender import KindleSender
from app.config import OUTPUT_DIR
from app.webhooks import webhooks_bp

# Create Flask app
app = Flask(__name__)

# Handle HTTPS behind Railway's proxy (fixes OAuth redirect_uri using http://)
from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24).hex())

# Database configuration
# Use DATABASE_URL from Railway, fallback to SQLite for local dev
database_url = os.environ.get('DATABASE_URL', 'sqlite:///kindle_users.db')
# Railway uses postgres:// but SQLAlchemy needs postgresql://
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Google OAuth configuration
app.config['GOOGLE_CLIENT_ID'] = os.environ.get('GOOGLE_CLIENT_ID')
app.config['GOOGLE_CLIENT_SECRET'] = os.environ.get('GOOGLE_CLIENT_SECRET')

# Initialize extensions
db.init_app(app)
init_oauth(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_page'
login_manager.login_message = 'Please sign in to access this page.'
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login."""
    return User.query.get(int(user_id))


# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(webhooks_bp)

# Initialize services
extractor = ContentExtractor()
builder = EpubBuilder()
sender = KindleSender()

# Create database tables
with app.app_context():
    db.create_all()


# --- Public Routes ---

@app.route('/login')
def login_page():
    """Show login page."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template('login.html')


# --- Protected Routes ---

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    """Main page - convert URL to EPUB and send to Kindle."""
    epub_filename = None
    title = None
    image_count = 0
    email_sent = False

    # Check if user has set up their Kindle email
    if not current_user.kindle_email:
        flash('Please set up your Kindle email first!', 'warning')
        return redirect(url_for('settings'))

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

            # 3. Send to THIS USER's Kindle email
            email_sent = sender.send_epub(epub_path, to_email=current_user.kindle_email)
            
            if email_sent:
                flash(f"Successfully converted '{title}' and sent to your Kindle!", 'success')
            else:
                flash(f"Converted '{title}' but email failed. You can download it below.", 'warning')

            epub_filename = os.path.basename(epub_path)
            
            return render_template('index.html', 
                                 epub_filename=epub_filename,
                                 title=title,
                                 image_count=image_count,
                                 email_sent=email_sent,
                                 user=current_user)

        except Exception as e:
            flash(f"Error processing URL: {str(e)}", 'error')
            return redirect(url_for('index'))

    return render_template('index.html', user=current_user)


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """User settings page - set Kindle email."""
    if request.method == 'POST':
        kindle_email = request.form.get('kindle_email', '').strip()
        
        if not kindle_email:
            flash('Please enter your Kindle email address.', 'error')
            return redirect(url_for('settings'))
        
        if not kindle_email.endswith('@kindle.com'):
            flash('Kindle email should end with @kindle.com', 'warning')
        
        # Update user's Kindle email
        current_user.kindle_email = kindle_email
        db.session.commit()
        
        flash('Kindle email saved successfully!', 'success')
        return redirect(url_for('index'))
    
    # Get the FROM_EMAIL for instructions
    from_email = os.environ.get('FROM_EMAIL', 'noreply@kindle.timour.xyz')
    
    return render_template('settings.html', user=current_user, from_email=from_email)


@app.route('/download/<filename>')
@login_required
def download(filename):
    """Serve the EPUB file for download."""
    filepath = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True, download_name=filename)
    else:
        flash('File not found', 'error')
        return redirect(url_for('index'))


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 Starting Multi-User Kindle App on port {port}")
    app.run(debug=True, host='0.0.0.0', port=port)
