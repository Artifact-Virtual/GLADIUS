# LinkedIn Automation Module for Arty

Comprehensive LinkedIn integration for automated post management, scheduling, and page administration using LinkedIn's official API.

## 🌟 Features

### ✅ Post Management
- **Text Posts**: Create simple text-based posts
- **Media Posts**: Post with images, videos, and documents
- **Multiple Media**: Support for up to 9 images per post
- **Post Visibility**: Control who sees your posts (PUBLIC, CONNECTIONS)
- **Hashtags**: Automatic hashtag support
- **Mentions**: Tag people and companies in posts

### 📅 Advanced Scheduling
- **Precise Scheduling**: Schedule posts down to the second
- **Timezone Support**: Schedule in any timezone
- **Relative Scheduling**: Use shortcuts like "2h", "1d", "30m"
- **Bulk Scheduling**: Schedule hundreds of posts programmatically
- **Auto-Publishing**: Scheduled posts publish automatically
- **Cancellation**: Cancel scheduled posts before they publish

### 📊 Analytics & Monitoring
- **Post Analytics**: Track likes, comments, shares
- **Engagement Rates**: Calculate post performance
- **Real-time Tracking**: Monitor post metrics
- **Historical Data**: Store analytics in database

### 🛡️ Rate Limiting & Safety
- **API Rate Limits**: Automatic rate limit management
- **Retry Logic**: Exponential backoff on failures
- **Error Handling**: Comprehensive error tracking
- **Quota Management**: Respects LinkedIn's API quotas

### 🧹 Cleanup & Maintenance
- **Auto Media Cleanup**: Delete media after posting (optional)
- **Old File Cleanup**: Remove old media and logs
- **Temp File Management**: Clean up temporary uploads
- **Database Cleanup**: Maintain database performance

### 🔐 Security
- **OAuth 2.0**: Secure authentication
- **Token Management**: Automatic token refresh
- **Environment Variables**: Sensitive data in .env
- **Access Control**: Organization and personal posts

## 📋 Prerequisites

1. **LinkedIn Developer Account**: Create an app at [LinkedIn Developers](https://www.linkedin.com/developers/)
2. **Node.js**: v18.0.0 or higher
3. **LinkedIn API Access**: Request appropriate permissions

### Required LinkedIn API Scopes
- `w_member_social` - Post as a member
- `w_organization_social` - Post as an organization
- `r_organization_social` - Read organization posts
- `rw_organization_admin` - Manage organization pages

## 🚀 Quick Start

### 1. Installation

```bash
cd arty/linkedin
npm install
```

### 2. Configuration

Copy environment template:
```bash
cp .env.example .env
nano .env
```

**Required variables:**
```env
LINKEDIN_CLIENT_ID=your_client_id
LINKEDIN_CLIENT_SECRET=your_client_secret
LINKEDIN_ACCESS_TOKEN=your_access_token
LINKEDIN_PERSON_URN=urn:li:person:XXXXXXXX
# OR for company pages:
LINKEDIN_ORGANIZATION_URN=urn:li:organization:XXXXXXXX
```

Copy config template:
```bash
cp config.example.json config.json
```

### 3. Getting Access Token

#### Option A: Manual OAuth Flow
1. Get authorization code:
```
https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=YOUR_CLIENT_ID&redirect_uri=YOUR_REDIRECT_URI&scope=w_member_social
```

2. Exchange code for token:
```bash
curl -X POST https://www.linkedin.com/oauth/v2/accessToken \
  -d grant_type=authorization_code \
  -d code=YOUR_CODE \
  -d client_id=YOUR_CLIENT_ID \
  -d client_secret=YOUR_CLIENT_SECRET \
  -d redirect_uri=YOUR_REDIRECT_URI
```

#### Option B: Use LinkedIn's Developer Tools
Visit your app's Auth tab and generate a test token for development.

### 4. Basic Usage

#### Post Immediately
```bash
npm run post -- "Hello LinkedIn! #networking"
```

#### Post with Media
```bash
npm run post -- --media ./image.jpg "Check out this image!"
```

#### Schedule a Post
```bash
npm run schedule -- "Future post content" "2026-01-10T14:00:00Z"
```

#### Run Scheduler Service
```bash
npm start
```

This starts the scheduler service that monitors and publishes scheduled posts.

## 📖 Detailed Usage

### Posting Text Content

```javascript
import LinkedInManager from './src/index.js';

const manager = new LinkedInManager();
await manager.initialize();

// Simple text post
const result = await manager.postNow(
  "Hello LinkedIn! #networking #growth",
  "urn:li:person:XXXXXXXX",  // Your person URN
  "PUBLIC"
);

console.log(`Posted: ${result.postId}`);
```

### Posting with Media

```javascript
// Post with images
const result = await manager.postWithMedia(
  "Check out our new product!",
  ["./images/product1.jpg", "./images/product2.jpg"],
  "urn:li:organization:XXXXXXXX",
  "PUBLIC"
);
```

### Scheduling Posts

```javascript
// Schedule for specific date/time
const result = await manager.schedulePost(
  "Happy New Year 2027!",
  new Date("2027-01-01T00:00:00Z"),
  null,  // no media
  "urn:li:person:XXXXXXXX",
  "PUBLIC"
);

console.log(`Scheduled: ${result.scheduledPostId}`);
console.log(`Will publish at: ${result.scheduledTime}`);
```

### Using Command-Line Scripts

#### Post Script
```bash
# Basic text post
node src/scripts/post.js "My post content"

# Post with image
node src/scripts/post.js --media ./image.jpg "Check this out!"

# Post with multiple images
node src/scripts/post.js --media ./img1.jpg,./img2.jpg "Gallery post"

# Post to connections only
node src/scripts/post.js --visibility CONNECTIONS "Private update"

# Post as organization
node src/scripts/post.js --author urn:li:organization:123 "Company update"
```

#### Scheduler Script
```bash
# Schedule with ISO timestamp
node src/scripts/scheduler.js "Post content" "2026-01-10T14:00:00Z"

# Schedule relative time (2 hours from now)
node src/scripts/scheduler.js "Future post" "2h"

# Schedule with media
node src/scripts/scheduler.js --media ./image.jpg "Scheduled post" "1d"

# Cancel a scheduled post
node src/scripts/scheduler.js --cancel scheduled_12345
```

#### Cleanup Script
```bash
# Clean up everything
node src/scripts/cleanup.js

# Clean up only media
node src/scripts/cleanup.js --media

# Clean up only logs
node src/scripts/cleanup.js --logs

# Clean up only temp files
node src/scripts/cleanup.js --temp
```

## 🏗️ Project Structure

```
linkedin/
├── src/
│   ├── services/
│   │   ├── linkedinService.js    # LinkedIn API integration
│   │   └── schedulerService.js   # Post scheduling logic
│   ├── utils/
│   │   ├── logger.js             # Winston logging
│   │   └── database.js           # SQLite database
│   ├── scripts/
│   │   ├── post.js               # Immediate posting CLI
│   │   ├── scheduler.js          # Scheduling CLI
│   │   └── cleanup.js            # Cleanup utilities
│   └── index.js                  # Main entry point
├── data/                         # SQLite database
├── logs/                         # Log files
├── media/                        # Media storage
├── .env.example                  # Environment template
├── config.example.json           # Configuration template
├── package.json                  # Dependencies
└── README.md                     # This file
```

## ⚙️ Configuration

### Environment Variables (.env)

| Variable | Description | Required |
|----------|-------------|----------|
| `LINKEDIN_CLIENT_ID` | Your app's client ID | Yes |
| `LINKEDIN_CLIENT_SECRET` | Your app's client secret | Yes |
| `LINKEDIN_ACCESS_TOKEN` | OAuth access token | Yes |
| `LINKEDIN_PERSON_URN` | Your person URN | For personal posts |
| `LINKEDIN_ORGANIZATION_URN` | Organization URN | For company posts |
| `SCHEDULER_ENABLED` | Enable auto-scheduler | No (default: true) |
| `AUTO_DELETE_MEDIA_AFTER_POST` | Clean media after post | No (default: true) |

### Config File (config.json)

Key configuration sections:
- **posting**: Content types, limits, hashtags
- **scheduling**: Timezone, intervals, optimal times
- **rateLimiting**: API limits, backoff strategy
- **media**: Storage, formats, cleanup rules
- **cleanup**: Automatic cleanup schedules
- **logging**: Log levels, rotation

## 🔍 LinkedIn API Capabilities

### Supported Content Types
- ✅ Text posts (up to 3,000 characters)
- ✅ Image posts (up to 9 images, 5MB each)
- ✅ Video posts (up to 200MB, 10 minutes)
- ✅ Document posts (PDF, DOCX, PPTX, etc.)
- ✅ Article shares (with preview)

### Supported Features
- ✅ Post scheduling
- ✅ Post visibility control
- ✅ Hashtags and mentions
- ✅ Media uploads
- ✅ Post analytics
- ✅ Post deletion
- ✅ Organization posting
- ✅ Personal posting

### API Limits
- **Posts per hour**: 25 (configurable)
- **Posts per day**: 100 (configurable)
- **Requests per minute**: 60
- **Media size**: Varies by type

## 📊 Database Schema

### Tables
- **posts**: Published posts tracking
- **scheduled_posts**: Queued posts for publishing
- **media**: Uploaded media assets
- **analytics**: Post performance metrics
- **rate_limits**: API call tracking
- **oauth_tokens**: Authentication tokens

## 🧪 Testing

Test your setup:

```bash
# Test basic posting
npm run post -- "Test post from Arty LinkedIn module!"

# Test scheduling (30 seconds from now)
npm run schedule -- "Test scheduled post" "30s"

# Watch the logs
tail -f logs/combined-$(date +%Y-%m-%d).log
```

## 🛡️ Error Handling

The module handles common errors:
- **Rate Limits**: Automatic backoff and retry
- **Auth Errors**: Clear error messages
- **Media Upload Failures**: Cleanup and retry
- **Network Issues**: Exponential backoff
- **Invalid Data**: Validation before API calls

## 📝 Best Practices

1. **Rate Limiting**: Don't exceed LinkedIn's limits
2. **Content Quality**: Post valuable, relevant content
3. **Scheduling**: Use optimal posting times
4. **Media**: Compress images before uploading
5. **Testing**: Test in development before production
6. **Monitoring**: Check logs regularly
7. **Cleanup**: Run cleanup scripts periodically

## 🔧 Integration with Arty

From Arty root, you can trigger LinkedIn actions:

```javascript
// In your Arty bot (Discord, Telegram, etc.)
import LinkedInManager from './linkedin/src/index.js';

// Trigger LinkedIn post from Discord command
async function handleDiscordCommand(message) {
  const linkedIn = new LinkedInManager();
  await linkedIn.initialize();
  
  await linkedIn.postNow(
    `New post from Discord: ${message.content}`,
    process.env.LINKEDIN_ORGANIZATION_URN
  );
  
  await linkedIn.shutdown();
}
```

## 🐛 Troubleshooting

### Common Issues

**"Access token expired"**
- Refresh your OAuth token
- LinkedIn tokens typically expire after 60 days

**"Rate limit exceeded"**
- Wait for rate limit window to reset
- Adjust rate limits in config.json

**"Media upload failed"**
- Check file size and format
- Ensure file exists and is readable
- Check media storage path

**"Scheduled posts not publishing"**
- Ensure scheduler is running (`npm start`)
- Check logs for errors
- Verify scheduled time is in the future

## 📚 Resources

- [LinkedIn API Documentation](https://learn.microsoft.com/en-us/linkedin/)
- [OAuth 2.0 Guide](https://learn.microsoft.com/en-us/linkedin/shared/authentication/authentication)
- [Posts API Reference](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/posts-api)
- [LinkedIn Developer Portal](https://www.linkedin.com/developers/)

## 📄 License

MIT License - See root LICENSE file

## 🆘 Support

For issues:
1. Check logs in `logs/` directory
2. Review error messages
3. Verify configuration
4. Check LinkedIn API status

---

**Arty LinkedIn Module** - Professional LinkedIn automation made simple
