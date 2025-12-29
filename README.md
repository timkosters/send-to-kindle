# Send to Kindle - Newsletter & Article Service

A service to convert newsletters, Substack articles, and essays into Kindle-native format (EPUB) for comfortable reading with full highlighting support and image preservation.

## 📚 Overview

This project analyzes how services like ReadBetter.io work and provides a complete guide to building your own alternative. The goal is to read newsletters and articles on your Kindle in a native format (not PDF) that supports:

- ✅ Text reflow and adjustable fonts
- ✅ Highlighting and notes
- ✅ Dictionary lookup
- ✅ Embedded images
- ✅ Clean, distraction-free reading

## 📖 Documentation

This repository contains three comprehensive guides:

1. **[ANALYSIS.md](./ANALYSIS.md)** - Deep dive into how ReadBetter.io and similar services work
   - Technical architecture
   - System components
   - Technology stack options
   - Database schema
   - Security considerations

2. **[IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md)** - Step-by-step implementation guide
   - Complete code examples
   - Project structure
   - Setup instructions
   - Troubleshooting tips

3. **[QUICK_REFERENCE.md](./QUICK_REFERENCE.md)** - Quick reference for key concepts
   - Technology summary
   - Common issues
   - Setup checklist

## 🎯 How It Works

### The Problem
- Native Kindle file sending often results in PDFs
- PDFs are hard to read on Kindle (no text reflow, limited highlighting)
- Need native format (EPUB/MOBI) for best reading experience

### The Solution
```
Newsletter/Article → Extract Content → Process Images → Create EPUB → Send to Kindle
```

### Key Components

1. **Email Reception**: Receive forwarded newsletters via IMAP
2. **Content Extraction**: Parse HTML, remove ads/navigation, extract main content
3. **Image Processing**: Download, optimize, and embed images
4. **EPUB Conversion**: Create Kindle-compatible EPUB files
5. **Kindle Delivery**: Email EPUB to Kindle address via Amazon's Send to Kindle

## 🚀 Quick Start - Choose Your Approach

### Option 1: Fully Automated (Requires Email Setup)
**Automatic conversion + email to Kindle**

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure email**:
   ```bash
   export KINDLE_EMAIL='your-kindle@kindle.com'
   export SMTP_USER='your-email@gmail.com'
   export SMTP_PASSWORD='your-password'
   ```

3. **Run automated version**:
   ```bash
   python run_web.py
   ```

### Option 2: Manual Download (NO Email Setup!)
**Convert to EPUB, download, email manually to Kindle**

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run simple version** (no configuration needed):
   ```bash
   python simple_web_app.py
   ```

3. **Open browser** to `http://localhost:8000`

4. **Paste URL → Download EPUB → Email to Kindle manually**

### Option 3: Automated with Email Setup
**Full automation - converts AND sends to Kindle**

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Follow the email setup guide**:
   ```bash
   # See EMAIL_SETUP_GUIDE.md for step-by-step instructions
   export KINDLE_EMAIL='your-kindle@kindle.com'
   export SMTP_USER='your-gmail@gmail.com'
   export SMTP_PASSWORD='your-app-password'
   ```

3. **Run with email**:
   ```bash
   python simple_web_app.py
   ```

4. **Paste URL → Auto-converts → Auto-sends to Kindle** ✨

### 🎯 How Each Option Works:

- **Automated**: Paste URL → Auto-converts → Auto-emails to Kindle ✅
- **Manual**: Paste URL → Download EPUB → You email to Kindle manually ✅

**Start with Manual if you're new to this!**

### 📁 Project Files

- **`simple_web_app.py`** - **NEW!** Web interface (no email setup required!)
- **`web_app.py`** - Web interface with auto-email to Kindle
- **`run_web.py`** - Easy launcher for automated version
- **`url_processor.py`** - Send URLs via email (alternative)
- **`main.py`** - Forward full newsletters (alternative)
- **`demo_url.py`** - Demo URL processing (no setup needed)
- **`config.py`** - Configuration and credentials
- **`test_epub.py`** - Test EPUB creation without emails
- **`requirements.txt`** - Python dependencies
- **`EMAIL_SETUP_GUIDE.md`** - **NEW!** Complete email setup guide (multiple providers)
- **`test_email.py`** - **NEW!** Test your email configuration
- **`SIMPLE_USAGE.md`** - Simple web app guide (no setup!)
- **`WEB_SETUP.md`** - Web app with email automation
- **`SETUP.md`** - Alternative setup guides
- **`URL_PROCESSOR.md`** - URL method explanation
- **`ANALYSIS.md`** - Technical analysis of ReadBetter.io
- **`IMPLEMENTATION_GUIDE.md`** - Complete implementation guide
- **`QUICK_REFERENCE.md`** - Quick reference

## 📋 Features

### Current Capabilities
- ✅ Email forwarding support
- ✅ HTML content extraction
- ✅ Image downloading and optimization
- ✅ EPUB file creation
- ✅ Send to Kindle via email

### Planned Enhancements
- 🔄 RSS feed support (Substack, Medium, etc.)
- 🔄 Web dashboard for managing subscriptions
- 🔄 Scheduled deliveries (daily/weekly digests)
- 🔄 Multiple article bundling
- 🔄 Custom formatting options

## 🏗️ Architecture

```
┌─────────────┐
│ Email/RSS   │
└──────┬──────┘
       │
┌──────▼──────────────────┐
│ Content Extractor       │  (readability, beautifulsoup)
└──────┬──────────────────┘
       │
┌──────▼──────────────────┐
│ Image Processor         │  (Pillow, requests)
└──────┬──────────────────┘
       │
┌──────▼──────────────────┐
│ EPUB Converter          │  (ebooklib)
└──────┬──────────────────┘
       │
┌──────▼──────────────────┐
│ Kindle Sender           │  (smtplib)
└─────────────────────────┘
```

## 🔧 Technology Stack

- **Backend**: Python 3.8+
- **Email**: `imaplib`, `smtplib`
- **Content Extraction**: `readability-lxml`, `beautifulsoup4`
- **E-book Creation**: `ebooklib`
- **Image Processing**: `Pillow`
- **RSS Parsing**: `feedparser`
- **HTTP Requests**: `requests`

## 📝 Use Cases

1. **Substack Newsletters**: Subscribe to RSS feeds, automatically convert and send
2. **Email Newsletters**: Forward emails, get converted versions on Kindle
3. **Web Articles**: Submit URLs, convert and send
4. **Personal Reading List**: Batch process multiple articles into digest

## 🔒 Privacy & Security

- Email credentials stored securely (use environment variables)
- Content processed temporarily, not stored long-term
- No tracking or analytics
- User data handled according to privacy best practices

## 💰 Cost Considerations

- **Free Tier**: Gmail (500 emails/day), basic VPS ($5/month)
- **Paid Options**: Email service ($10-20/month), better hosting ($10-20/month)
- **MVP Total**: ~$15-40/month

## 📚 Related Services

This project is inspired by and analyzes:
- [ReadBetter.io](https://www.readbetter.io)
- [Serifize](https://serifize.com)
- [Link to Reader](https://www.linktoreader.com)
- [KTool](https://dev.ktool.io)
- [Substack2Kindle](https://www.substack2kindle.com)

## 🤝 Contributing

This is a learning/implementation project. Feel free to:
- Improve the code examples
- Add new features
- Fix bugs
- Share your implementation

## 📄 License

This is an educational project. Use the code as you see fit.

## 🎓 Learning Resources

- [EPUB Format Specification](https://www.w3.org/publishing/epub3/)
- [Amazon Send to Kindle Documentation](https://www.amazon.com/gp/sendtokindle/email)
- [Python Email Processing](https://docs.python.org/3/library/email.html)
- [Content Extraction Techniques](https://github.com/mozilla/readability)

## 🐛 Troubleshooting

See [IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md) for detailed troubleshooting, or [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) for common issues.

## 📞 Next Steps

1. Read [ANALYSIS.md](./ANALYSIS.md) to understand the architecture
2. Follow [IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md) to build your MVP
3. Use [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) as a cheat sheet
4. Start with email forwarding, then add RSS support
5. Build a web interface for easier management

---

**Happy Reading! 📖✨**

