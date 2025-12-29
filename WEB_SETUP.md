# Web App Setup Guide

Get your newsletter-to-Kindle web interface running in 5 minutes!

## 🚀 Quick Setup

### 1. Install Dependencies
```bash
cd /Users/timourkosters/Projects/Send-to-kingle
pip install -r requirements.txt
```

### 2. Configure Your Email & Kindle

**Option A: Environment Variables (Recommended)**
```bash
export KINDLE_EMAIL='your-kindle@kindle.com'     # Your Kindle email address
export SMTP_USER='your-email@gmail.com'          # Your email address
export SMTP_PASSWORD='your-password'             # Your email password
```

**Option B: Create a .env file**
Create a file named `.env` in the project folder:
```
KINDLE_EMAIL=your-kindle@kindle.com
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-password
```

### 3. Find Your Kindle Email

1. Go to [Manage Your Kindle](https://www.amazon.com/myk)
2. Select your Kindle device
3. Copy the email address (looks like `ABCDEF123456@kindle.com`)

### 4. Configure Email for Sending

**For Gmail:**
- Use your regular Gmail address as `SMTP_USER`
- Create a Gmail App Password as `SMTP_PASSWORD`:
  - Go to [Google Account Security](https://myaccount.google.com/security)
  - Enable 2-Step Verification
  - App Passwords → Generate "Kindle App"

**For Other Email Providers:**
- Use your email address as `SMTP_USER`
- Use your regular password as `SMTP_PASSWORD`
- The app will auto-detect the SMTP server

### 5. Approve Your Email on Amazon

**CRITICAL: Without this, emails will be rejected!**

1. Go to [Personal Document Settings](https://www.amazon.com/gp/digital/fiona/manage)
2. Under "Approved Personal Document E-mail List"
3. Add your email address (`SMTP_USER`)
4. Click "Add Address"

### 6. Test It!

1. **Start the web app**:
   ```bash
   python run_web.py
   ```

2. **Open browser** to `http://localhost:5000`

3. **Paste a newsletter URL**:
   - Example: `https://www.nytimes.com/2024/01/15/technology/ai-chatbot-testing.html`
   - Click "Send to Kindle"

4. **Check your Kindle** in 2-5 minutes!

## 📧 Email Provider Settings

The app automatically detects SMTP settings for common providers:

| Provider | SMTP Server | Port |
|----------|-------------|------|
| Gmail | smtp.gmail.com | 587 |
| Outlook/Hotmail | smtp-mail.outlook.com | 587 |
| Yahoo | smtp.mail.yahoo.com | 587 |
| iCloud | smtp.mail.me.com | 587 |

For other providers, set custom SMTP settings:
```bash
export SMTP_SERVER='your-smtp-server.com'
export SMTP_PORT='587'
```

## 🐛 Troubleshooting

### "Configuration Issues" Error
- Check that all environment variables are set correctly
- Make sure Kindle email is from Amazon (ends with @kindle.com)

### "Failed to send to Kindle" Error
- Verify your email is approved in Amazon settings
- Check your email credentials
- Try using a Gmail App Password

### Web App Won't Start
- Make sure port 5000 is not in use
- Check that Flask installed correctly: `pip list | grep flask`

### No Content Extracted
- Try a different newsletter URL
- Some sites block automated access - try another article

## 🎯 Examples to Test With

- **Substack**: `https://yourauthor.substack.com/p/article-title`
- **Medium**: `https://medium.com/@author/article-title`
- **News**: `https://www.nytimes.com/article-url`
- **Blogs**: Any blog post URL

## 🔄 Keeping the App Running

**For personal use:**
- Run `python run_web.py` whenever you want to use it
- The app runs locally on your computer

**For continuous use:**
- Keep the terminal window open
- Or set up as a background service

The web app is completely local - no data is sent anywhere except your Kindle!
