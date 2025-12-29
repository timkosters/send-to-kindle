import os
import base64
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content, Attachment, FileContent, FileName, FileType, Disposition

class KindleSender:
    def __init__(self):
        pass

    def send_epub(self, epub_path):
        """Send EPUB file to Kindle email using SendGrid"""
        
        # Load credentials from environment
        api_key = os.environ.get('SENDGRID_API_KEY')
        from_email_addr = os.environ.get('FROM_EMAIL')
        to_email_addr = os.environ.get('KINDLE_EMAIL')

        if not api_key:
            print("ℹ️  SendGrid API Key not found. Skipping email.")
            return False

        if not from_email_addr or not to_email_addr:
             print("ℹ️  Email addresses (FROM/TO) not configured. Skipping email.")
             return False

        try:
            filename = os.path.basename(epub_path)
            print(f"📤 Sending {filename} to {to_email_addr} via SendGrid...")

            sg = SendGridAPIClient(api_key)
            
            message = Mail(
                from_email=Email(from_email_addr),
                to_emails=To(to_email_addr),
                subject='Convert',
                html_content=Content("text/html", f"Here is your converted article: <strong>{filename}</strong><br><br>Sent from your Kindle Web App.")
            )

            # Read and encode file
            with open(epub_path, 'rb') as f:
                data = f.read()
                f.close()
            
            encoded_file = base64.b64encode(data).decode()
            
            attachedFile = Attachment(
                FileContent(encoded_file),
                FileName(filename),
                FileType('application/epub+zip'),
                Disposition('attachment')
            )
            message.attachment = attachedFile

            response = sg.send(message)
            print(f"✅ Email sent! Status code: {response.status_code}")
            
            return str(response.status_code).startswith('2')

        except Exception as e:
            print(f"❌ Error sending to Kindle: {e}")
            return False
