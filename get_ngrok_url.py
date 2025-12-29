from pyngrok import ngrok
import time

# Open a HTTP tunnel on the default port 8000
public_url = ngrok.connect(8000).public_url
print(f"Tunnel URL: {public_url}")

# Keep it alive for a bit so we can see it (in a real scenario we'd keep it running)
# For this script we just want to output the URL for the user
time.sleep(1)
