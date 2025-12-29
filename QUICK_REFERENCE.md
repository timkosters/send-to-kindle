# Quick Reference: Kindle Newsletter Service

## How ReadBetter.io Works (Summary)

1. **User Setup**: User provides Kindle email, service assigns forwarding email
2. **Content Input**: User forwards newsletters OR service polls RSS feeds
3. **Processing**: Extract content → Download images → Convert to EPUB
4. **Delivery**: Email EPUB file to Kindle address

## Key Technologies

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Email Reading | `imaplib` (Python) | Receive forwarded emails |
| Content Extraction | `readability-lxml`, `beautifulsoup4` | Extract main article content |
| Image Processing | `Pillow`, `requests` | Download and optimize images |
| EPUB Creation | `ebooklib` | Create Kindle-compatible files |
| Email Sending | `smtplib` | Send to Kindle email |
| RSS Parsing | `feedparser` | Process Substack/other RSS feeds |

## Why EPUB/MOBI vs PDF?

- ✅ **EPUB/MOBI**: Native format, supports highlighting, text reflow, dictionary
- ❌ **PDF**: Fixed layout, harder to read, limited features

## Core Workflow

```
Email/RSS → Extract Content → Process Images → Create EPUB → Send to Kindle
```

## Amazon Send to Kindle

- **Method**: Email attachment to `your-kindle@kindle.com`
- **Format**: EPUB, MOBI, PDF, DOCX
- **Requirement**: Sender email must be in approved list
- **Subject**: Can use "Convert" for automatic conversion

## Substack RSS Format

- URL: `https://[publication].substack.com/feed`
- Contains full article content in feed
- Images hosted on Substack CDN

## Minimal Setup Checklist

- [ ] Gmail account with App Password
- [ ] Kindle email address (from Amazon account)
- [ ] Add sender email to Kindle approved list
- [ ] Install Python dependencies
- [ ] Configure environment variables
- [ ] Test with one forwarded email

## Common Issues

1. **Email not appearing on Kindle**
   - Check sender email is approved
   - Verify Kindle email is correct
   - Check spam/junk folder

2. **Images not showing**
   - Verify image URLs are accessible
   - Check image download permissions
   - Ensure images are embedded in EPUB

3. **Formatting problems**
   - Adjust CSS in EPUB converter
   - Check HTML structure
   - Test with different content sources

## Cost Estimate

- **Free Tier**: Gmail (500 emails/day), basic VPS ($5/month)
- **Paid**: Email service ($10-20/month), better hosting ($10-20/month)
- **Total MVP**: ~$15-40/month

## Alternative Services to Study

- ReadBetter.io
- Serifize
- Link to Reader
- KTool
- Substack2Kindle

## Next Level Features

- Web dashboard for managing subscriptions
- Daily/weekly digests (bundle multiple articles)
- Custom formatting options
- Mobile app or browser extension
- Support for more platforms (Medium, personal blogs)
- AI-generated summaries
- Highlight sync back to service

