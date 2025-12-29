# 📧 Complete Email Setup Guide (Beginner-Friendly)

## 🎯 Goal: Make Your Newsletter App Send Emails to Kindle Automatically

This guide will walk you through setting up Gmail to send emails automatically. It's easier than it sounds!

---

## 📋 Step 1: Get Your Kindle Email Address

**Your Kindle needs a special email address to receive books.**

1. Go to [Amazon Manage Your Kindle](https://www.amazon.com/myk)
2. Click on your Kindle device
3. Find "Email address" - it looks like: `ABCDEF123456@kindle.com`
4. **Copy this address** - you'll need it later

---

## 📧 Step 2: Choose Your Email Provider

### 🎯 **EASIEST: Outlook/Hotmail (Works Immediately!)**

**No special setup required - just use your regular password:**

```bash
export SMTP_USER='yourname@outlook.com'
export SMTP_PASSWORD='your-regular-outlook-password'
export SMTP_SERVER='smtp-mail.outlook.com'
```

**That's it!** Outlook doesn't require app passwords or special configuration.

### 📧 **Other Options (if you prefer different email):**

### 📧 **Other Options:**

#### Option A: Gmail (if App Passwords still work for you)
Some Gmail accounts still support App Passwords:

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. **Turn on 2-Step Verification** (if not already on)
3. **Create an App Password:**
   - Go to "Signing in to Google" → "App passwords"
   - Select "Mail" and "Other (custom name)"
   - Enter "Kindle Newsletter"
   - Click "Generate"
   - **Copy the 16-character password**

```bash
export SMTP_USER='your-gmail@gmail.com'
export SMTP_PASSWORD='abcdefghijklmnop'  # Your app password
```

#### Option B: Yahoo Mail
Yahoo works with regular passwords:

```bash
export SMTP_USER='your-yahoo-email@yahoo.com'
export SMTP_PASSWORD='your-regular-password'
export SMTP_SERVER='smtp.mail.yahoo.com'
```

#### Option C: iCloud Mail
iCloud requires an app-specific password:

1. Go to [Apple ID](https://appleid.apple.com)
2. "Sign-in and Security" → "App-Specific Passwords"
3. Generate password for "Kindle Newsletter"

```bash
export SMTP_USER='your-icloud@icloud.com'
export SMTP_PASSWORD='your-app-specific-password'
export SMTP_SERVER='smtp.mail.me.com'
```

#### Option D: Any Other Email Provider
Most email providers support SMTP. Check your provider's settings:

```bash
export SMTP_USER='your-email@your-provider.com'
export SMTP_PASSWORD='your-password'
export SMTP_SERVER='smtp.your-provider.com'  # Check your provider
export SMTP_PORT='587'  # Usually 587 or 465
```

---

## ⚙️ Step 3: Configure Your App

### Method A: Easy Environment Variables

Open Terminal and run these commands:

```bash
# Set your Kindle email (from Step 1)
export KINDLE_EMAIL='ABCDEF123456@kindle.com'

# Set your Gmail details (from Step 2)
export SMTP_USER='your-gmail@gmail.com'
export SMTP_PASSWORD='abcdefghijklmnop'  # Your 16-character app password

# Optional: If using non-Gmail, set server details
# export SMTP_SERVER='smtp.gmail.com'  # Usually not needed
# export SMTP_PORT='587'               # Usually not needed
```

### Method B: Edit the Config File

1. Open the file `config.py` in a text editor
2. Find these lines and update them:

```python
# Change this line:
KINDLE_EMAIL = os.getenv('KINDLE_EMAIL', 'your-kindle@kindle.com')

# To this (replace with your actual Kindle email):
KINDLE_EMAIL = 'ABCDEF123456@kindle.com'

# And uncomment/change these lines:
SMTP_USER = 'your-gmail@gmail.com'           # Your Gmail address
SMTP_PASSWORD = 'abcdefghijklmnop'           # Your 16-character app password
```

---

## 📧 Step 4: Tell Amazon to Accept Emails from Your Gmail

**CRITICAL: Amazon blocks emails by default for security.**

1. Go to [Personal Document Settings](https://www.amazon.com/gp/digital/fiona/manage)
2. Under "Approved Personal Document E-mail List":
   - Add your Gmail address (`your-gmail@gmail.com`)
   - Click "Add Address"
3. **Check your email** - Amazon will send a confirmation link
4. **Click the confirmation link** in your Gmail

---

## 🚀 Step 5: Test Your Email Setup

**First, test that your email works:**

```bash
cd /Users/timourkosters/Projects/Send-to-kingle
PYTHONPATH=/Users/timourkosters/Library/Python/3.12/lib/python/site-packages /Library/Frameworks/Python/framework/Versions/3.12/bin/python3 test_email.py
```

**Look for:** `✅ Email configuration is working!`

## 🚀 Step 6: Run the Full App

```bash
cd /Users/timourkosters/Projects/Send-to-kingle
PYTHONPATH=/Users/timourkosters/Library/Python/3.12/lib/python/site-packages /Library/Frameworks/Python/framework/Versions/3.12/bin/python3 simple_web_app.py
```

1. Open `http://localhost:8000`
2. Paste a newsletter URL
3. Click "Convert to EPUB"
4. **Check your Kindle** in 2-5 minutes!

You should see: "✅ [Title] converted successfully! 📤 Sent to Kindle automatically!"

---

## 🔧 Troubleshooting

### "Email not configured"
- Make sure you set `SMTP_USER` and `SMTP_PASSWORD` correctly
- Check that your App Password is exactly 16 characters

### "Failed to send to Kindle"
- Verify your Kindle email address is correct
- Confirm your Gmail is approved in Amazon settings
- Try sending a test email manually to your Kindle first

### "Authentication failed"
- Double-check your App Password (not your regular password)
- Make sure 2-Step Verification is enabled on your Google account

### Still not working?
- Try creating a new App Password
- Test with a simple email first

---

## 🎉 Success!

Once set up, your workflow will be:
1. Find newsletter URL
2. Paste in web app
3. Click button
4. Article appears on Kindle automatically!

**Questions?** The setup is designed to be foolproof. If you get stuck on any step, let me know which one and I'll help!
