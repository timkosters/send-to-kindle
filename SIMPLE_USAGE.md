# Simple Web App Usage (No Email Setup!)

The easiest way to convert newsletters to Kindle - no passwords, no email configuration!

## 🚀 Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the simple web app**:
   ```bash
   python simple_web_app.py
   ```

3. **Open browser** to `http://localhost:5000`

4. **Use it**:
   - Paste newsletter URL
   - Click "Convert to EPUB"
   - Download the EPUB file
   - Email it to your Kindle manually

## 🎯 How It Works

**Step 1: Convert**
- Paste any newsletter URL
- App fetches and cleans the content
- Converts to EPUB format
- Shows download link

**Step 2: Send to Kindle**
- Download the EPUB file
- Email it as attachment to your Kindle email
- File appears on Kindle in 2-5 minutes

## 📧 Manual Email to Kindle

**Your Kindle Email:**
- Find it at: https://www.amazon.com/myk
- Looks like: `ABCDEF123456@kindle.com`

**Send the Email:**
- To: `your-kindle@kindle.com`
- Subject: "Convert" (or anything)
- Attachment: The downloaded .epub file
- From: Any email address you own

**Approve Your Email (One-time setup):**
1. Go to: https://www.amazon.com/gp/digital/fiona/manage
2. Add your email address to "Approved Personal Document E-mail List"
3. Click "Add Address"

## ✅ Why This Approach?

- **No passwords needed** - no email configuration
- **Works immediately** - just run the app
- **Totally private** - everything local
- **Simple and reliable** - manual step ensures it works
- **No API keys or services** - just you and your Kindle

## 🔄 Workflow

```
Newsletter URL → Local Web App → Clean EPUB → Download → Email to Kindle → 📖 Enjoy!
```

## 🎉 Perfect For:

- Users who don't want email automation
- Testing the conversion quality
- Privacy-conscious users
- Simple, reliable workflow

## 🚀 Ready to Try?

```bash
python simple_web_app.py
```

Then visit `http://localhost:5000` and paste any newsletter URL!
