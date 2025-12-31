"""
Webhook Blueprint for Inbound Email Processing

This module handles incoming emails from SendGrid Inbound Parse.
When a user sends an email with a URL to save@kindle.timour.xyz,
we look up their Kindle email in the database and send the converted article there.
"""

from flask import Blueprint, request, jsonify, current_app
import os
import re
import json
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content, Attachment, FileContent, FileName, FileType, Disposition
import base64
from app.content import ContentExtractor
from app.epub import EpubBuilder
from app.models import User

webhooks_bp = Blueprint('webhooks', __name__)

# Initialize services
extractor = ContentExtractor()
builder = EpubBuilder()


def send_epub_email(to_email, epub_path, title):
    """Send EPUB via SendGrid."""
    sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
    from_email = os.environ.get('FROM_EMAIL')
    
    message = Mail(
        from_email=Email(from_email),
        to_emails=To(to_email),
        subject='Convert',
        html_content=Content("text/html", f"Here is your converted article: <strong>{title}</strong>")
    )

    with open(epub_path, 'rb') as f:
        data = f.read()
    
    encoded_file = base64.b64encode(data).decode()
    attachedFile = Attachment(
        FileContent(encoded_file),
        FileName(os.path.basename(epub_path)),
        FileType('application/epub+zip'),
        Disposition('attachment')
    )
    message.attachment = attachedFile

    try:
        response = sg.send(message)
        print(f"✅ Email sent! Status code: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False


@webhooks_bp.route('/webhooks/inbound-email', methods=['POST'])
def inbound_email():
    """
    Handle incoming emails from SendGrid Inbound Parse.
    
    Flow:
    1. Extract sender email from envelope
    2. Look up sender in database to get their Kindle email
    3. Extract URL from email body
    4. Convert URL to EPUB
    5. Send EPUB to user's Kindle
    """
    try:
        # Parse envelope to get sender email
        envelope_raw = request.form.get('envelope', '{}')
        try:
            envelope = json.loads(envelope_raw)
        except json.JSONDecodeError:
            envelope = {}
        
        sender_email = envelope.get('from', '').lower()
        subject = request.form.get('subject', 'No Subject')
        html_body = request.form.get('html', '')
        text_body = request.form.get('text', '')
        
        print(f"📥 Received email from: {sender_email}")
        print(f"📧 Subject: {subject}")
        
        # Look up sender in database
        user = User.get_by_email(sender_email) if sender_email else None
        
        if not user:
            print(f"⚠️ Unknown sender: {sender_email}. Ignoring.")
            return jsonify({
                'status': 'ignored', 
                'reason': 'Sender not registered. Please sign up at the web app first.'
            }), 200
        
        if not user.kindle_email:
            print(f"⚠️ User {sender_email} has no Kindle email configured.")
            return jsonify({
                'status': 'ignored',
                'reason': 'Kindle email not configured. Please set it up in the web app.'
            }), 200
        
        print(f"👤 Found user: {user.name} → Kindle: {user.kindle_email}")
        
        # Extract URL from body
        url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
        urls = re.findall(url_pattern, text_body or html_body or "")
        
        if not urls:
            print("⚠️ No URL found in email body.")
            return jsonify({'status': 'ignored', 'reason': 'No URL found in email'}), 200
            
        target_url = urls[0]
        print(f"🔗 Found URL: {target_url}")
        
        # Process the URL
        data = extractor.process_url(target_url)
        
        # Create EPUB
        epub_path = builder.create_epub(
            data['title'],
            data['content'],
            data['images'],
            data['url']
        )
        
        # Send to user's Kindle
        if send_epub_email(user.kindle_email, epub_path, data['title']):
            print(f"✅ Successfully sent '{data['title']}' to {user.kindle_email}")
            return jsonify({'status': 'success', 'message': 'Converted and sent'}), 200
        else:
            return jsonify({'status': 'error', 'message': 'Failed to send email'}), 500

    except Exception as e:
        print(f"❌ Error in webhook: {e}")
        current_app.logger.error(f"Webhook error: {e}")
        return jsonify({'error': str(e)}), 500
