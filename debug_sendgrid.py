import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

def debug_sendgrid():
    load_dotenv()
    
    api_key = os.environ.get('SENDGRID_API_KEY')
    from_email = os.environ.get('FROM_EMAIL')
    to_email = os.environ.get('KINDLE_EMAIL')

    print("--- DEBUG INFO ---")
    print(f"API Key exists: {bool(api_key)}")
    if api_key:
        print(f"API Key starts with: {api_key[:5]}...")
        print(f"API Key length: {len(api_key)}")
    
    print(f"From Email: {from_email}")
    print(f"To Email: {to_email}")

    if not api_key:
        print("❌ CRITICAL: SENDGRID_API_KEY is missing!")
        return

    try:
        sg = SendGridAPIClient(api_key)
        message = Mail(
            from_email=from_email,
            to_emails=to_email,
            subject='Debug Test',
            html_content='<strong>It works!</strong>'
        )
        response = sg.send(message)
        print(f"✅ SendGrid Response: {response.status_code}")
    except Exception as e:
        print(f"❌ SendGrid Error: {e}")

if __name__ == "__main__":
    debug_sendgrid()
