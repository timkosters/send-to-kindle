# Kindle Newsletter Prototype - Setup Guide

Get your newsletter-to-Kindle service running in 10 minutes!

## 🎯 Choose Your Method

### Method 1: URL Submission (SIMPLEST - Recommended)
Send newsletter URLs via email to yourself. No complex forwarding needed!

### Method 2: Email Forwarding
Forward complete newsletters via email (original method).

---

## 🚀 Quick Setup (URL Method)

### 1. Install Dependencies
```bash
cd /Users/timourkosters/Projects/Send-to-kingle
pip install -r requirements.txt
```

### 2. Configure Gmail App Password

**Why Gmail App Password?** Gmail requires special "App Passwords" for automated access (not your regular password). This is Google's security requirement.

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. **Enable 2-Step Verification** (if not already enabled)
3. Go to **App Passwords** → **Select App** → **Mail** → **Other (custom name)**
4. Enter "Kindle Newsletter" → **Generate**
5. Copy the 16-character password (no spaces)

### 3. Find Your Kindle Email

1. Go to [Manage Your Kindle](https://www.amazon.com/myk)
2. Select your Kindle device
3. Copy the email address (looks like `ABCDEF123456@kindle.com`)

### 4. Approve Your Sender Email

**Critical Step - Without this, emails will be rejected!**

1. Go to [Personal Document Settings](https://www.amazon.com/gp/digital/fiona/manage)
2. Under "Approved Personal Document E-mail List", add your Gmail address
3. Click **Add Address**

### 5. Configure the Script

**Option A: Environment Variables (Recommended)**
```bash
export GMAIL_USER='your-gmail@gmail.com'
export GMAIL_APP_PASSWORD='abcdefghijklmnop'  # Your 16-char app password
export KINDLE_EMAIL='ABCDEF123456@kindle.com'
```

**Option B: Edit config.py directly**
```python
# In config.py, replace these lines:
GMAIL_USER = 'your-gmail@gmail.com'
GMAIL_APP_PASSWORD = 'abcdefghijklmnop'
KINDLE_EMAIL = 'ABCDEF123456@kindle.com'
```

### 6. Test It!

1. **Send yourself a newsletter URL**
   - Email yourself with: `https://example.com/newsletter-article`
   - Subject: anything (or just "Convert")

2. **Run the script**
   ```bash
   python url_processor.py
   ```

3. **Check your Kindle**
   - Wait 2-5 minutes
   - The article should appear in your Kindle library!

---

## 📧 How URL Method Works

**From your phone or computer:**
- Open newsletter in browser
- Copy the URL
- Email it to yourself
- Run `python url_processor.py`
- Article appears on Kindle!

**No more:**
- ❌ Complex email forwarding rules
- ❌ Dealing with HTML formatting issues
- ❌ Newsletter clutter and ads

**Benefits:**
- ✅ Simple: Just send URLs
- ✅ Clean: Fetches fresh content
- ✅ Mobile-friendly
- ✅ Works with any newsletter platform

## 📋 Expected Output

When you run the script, you should see:
```
🚀 Starting Kindle Newsletter Processor
📧 Gmail: your-gmail@gmail.com
📖 Kindle: ABCDEF123456@kindle.com

🔗 Connecting to Gmail...
✅ Connected successfully
📧 Found 1 unread emails

📧 Processing email 12345
📄 Title: Your Newsletter Title
🖼️  Images: 2
📖 Created EPUB: Your_Newsletter_Title_20241228_143022.epub
📤 Sent to Kindle: ABCDEF123456@kindle.com
✅ Successfully processed and sent to Kindle

🎉 Processing complete! Sent 1 articles to your Kindle
📖 Check your Kindle in a few minutes
```

## 🐛 Troubleshooting

### "Failed to connect" Error
- ✅ Check Gmail username and App Password
- ✅ Make sure 2-Step Verification is enabled
- ✅ App Password should be 16 characters (no spaces)

### Email Not Appearing on Kindle
- ✅ Verify Kindle email address is correct
- ✅ Confirm your Gmail is in Amazon's approved sender list
- ✅ Check spam/junk folder on Amazon account
- ✅ Wait up to 10 minutes for delivery

### No Content Extracted
- ✅ Make sure you're forwarding HTML emails (not plain text)
- ✅ Try forwarding a different newsletter
- ✅ Check if the email contains HTML content

### Images Not Showing
- ✅ Some newsletters block image downloads
- ✅ Try a different newsletter with images
- ✅ Images will be optimized for Kindle automatically

## 🔧 Advanced Configuration

### Change Image Quality
In `config.py`:
```python
MAX_IMAGE_WIDTH = 600    # Smaller for faster loading
MAX_IMAGE_HEIGHT = 800   # Smaller for faster loading
IMAGE_QUALITY = 75       # Lower quality, smaller files
```

### Custom Output Directory
In `config.py`:
```python
OUTPUT_DIR = './my_epub_files'  # Custom directory for EPUB files
```

## 📱 Testing with Different Newsletters

Try forwarding these to test:
- **Substack**: Any Substack newsletter
- **Medium**: Medium articles
- **Newsletters**: Morning Brew, The Hustle, etc.
- **Blog posts**: Any blog with good HTML formatting

## 🎯 Next Steps

Once the prototype works:

1. **Set up automatic forwarding** in Gmail:
   - Gmail Settings → See all settings → Filters and Blocked Addresses
   - Create filter for newsletter emails
   - Forward to your Gmail address

2. **Run periodically**:
   ```bash
   # Check every hour
   while true; do python main.py; sleep 3600; done
   ```

3. **Add RSS support** (see IMPLEMENTATION_GUIDE.md for Substack RSS)

## 📞 Support

If you get stuck:
1. Check the troubleshooting section above
2. Verify all configuration steps
3. Try with a simple newsletter first
4. Check the terminal output for specific error messages

The prototype should work immediately once configured correctly! 🚀
