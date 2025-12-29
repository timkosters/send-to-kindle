import requests
import json

def test_webhook():
    url = 'http://localhost:8000/webhooks/inbound-email'
    
    # Simulate SendGrid multipart payload
    # SendGrid sends 'text' and 'html' fields, and 'envelope' JSON
    
    payload = {
        'subject': 'Article to Convert',
        'text': 'Hey, please convert this article: https://www.theverge.com/2023/12/1/23984675/google-deepmind-gemini-ai-model-release-date\n\nThanks!',
        'envelope': json.dumps({'to': ['save@kindle.timour.xyz'], 'from': 'timour@example.com'})
    }
    
    print(f"🚀 Sending test webhook to {url}...")
    try:
        response = requests.post(url, data=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Webhook test passed!")
        else:
            print("❌ Webhook test failed.")
            
    except Exception as e:
        print(f"❌ Error connecting to server: {e}")

if __name__ == '__main__':
    test_webhook()
