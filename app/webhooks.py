from flask import Blueprint, request, jsonify
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content, Attachment, FileContent, FileName, FileType, Disposition
import base64
from app.content import ContentExtractor
from app.epub import EpubBuilder

webhooks_bp = Blueprint('webhooks', __name__)

# Initialize services
extractor = ContentExtractor()
builder = EpubBuilder()

def send_epub_email(to_email, epub_path, title):
    """Send EPUB via SendGrid"""
    sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
    from_email = os.environ.get('FROM_EMAIL')
    
    message = Mail(
        from_email=Email(from_email),
        to_emails=To(to_email),
        subject='Convert',  # "Convert" triggers PDF conversion if needed, good practice for Kindle
        html_content=Content("text/html", f"Here is your converted article: <strong>{title}</strong>")
    )

    # Attach the file
    with open(epub_path, 'rb') as f:
        data = f.read()
        f.close()
    
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
        print(f"Email sent! Status code: {response.status_code}")
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

@webhooks_bp.route('/webhooks/inbound-email', methods=['POST'])
def inbound_email():
    """Handle incoming emails from SendGrid Inbound Parse"""
    try:
        # SendGrid sends multipart/form-data
        # 'text' contains the body, 'html' contains the HTML body
        # 'envelope' contains JSON with from/to
        # 'subject' contains subject
        
        envelope = request.form.get('envelope')
        subject = request.form.get('subject', 'No Subject')
        html_body = request.form.get('html')
        text_body = request.form.get('text')
        
        print(f"📥 Received email: {subject}")
        
        # Extract URL from body (simple logic for now: find first http url)
        # In a real app, we'd have better parsing or handle attachments
        
        import re
        url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
        urls = re.findall(url_pattern, text_body or html_body or "")
        
        if not urls:
            return jsonify({'status': 'ignored', 'reason': 'No URL found'}), 200
            
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
        
        # Send to Kindle
        # For now, hardcode or grab from env. In future, map sender to kindle email.
        # User defined kindle email in .env
        kindle_email = os.environ.get('KINDLE_EMAIL')
        
        if prompt_send := send_epub_email(kindle_email, epub_path, data['title']):
             return jsonify({'status': 'success', 'message': 'Converted and sent'}), 200
        else:
             return jsonify({'status': 'error', 'message': 'Failed to send email'}), 500

    except Exception as e:
        print(f"❌ Error in webhook: {e}")
        return jsonify({'error': str(e)}), 500
