# LinkedIn Automation Guide

Complete guide for LinkedIn automation setup and operation.

## Setup

### 1. Create LinkedIn App

1. Go to [LinkedIn Developers](https://www.linkedin.com/developers/apps)
2. Click "Create app"
3. Fill in app details
4. Submit for verification
5. Once approved, get credentials:
   - Client ID
   - Client Secret

### 2. OAuth 2.0 Authentication

**Generate Access Token:**

```bash
# Authorization URL (open in browser)
https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=YOUR_CLIENT_ID&redirect_uri=YOUR_REDIRECT_URI&scope=w_member_social%20r_liteprofile%20r_emailaddress

# Exchange code for token
curl -X POST https://www.linkedin.com/oauth/v2/accessToken \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'grant_type=authorization_code' \
  -d 'code=YOUR_CODE' \
  -d 'client_id=YOUR_CLIENT_ID' \
  -d 'client_secret=YOUR_CLIENT_SECRET' \
  -d 'redirect_uri=YOUR_REDIRECT_URI'
```

**Required Scopes:**
- `w_member_social` - Create posts
- `r_liteprofile` - Read profile
- `r_organization_social` - Organization posts (if needed)
- `w_organization_social` - Post as organization

### 3. Get URNs

**Person URN:**
```bash
curl -X GET 'https://api.linkedin.com/v2/me' \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN'
```

**Organization URN:**
```bash
curl -X GET 'https://api.linkedin.com/v2/organizationalEntityAcls?q=roleAssignee' \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN'
```

### 4. Configure Module

```bash
cd arty/linkedin
cp .env.example .env
cp config.example.json config.json
```

**Edit `.env`:**
```env
LINKEDIN_CLIENT_ID=your_client_id
LINKEDIN_CLIENT_SECRET=your_client_secret
LINKEDIN_ACCESS_TOKEN=your_access_token
LINKEDIN_PERSON_URN=urn:li:person:XXXXXXXX
LINKEDIN_ORGANIZATION_URN=urn:li:organization:XXXXXXXX
```

**Edit `config.json`:**
```json
{
  "posting": {
    "defaultVisibility": "PUBLIC",
    "defaultAuthor": "person",
    "contentTypes": {
      "text": true,
      "image": true,
      "video": true,
      "document": true
    }
  },
  "scheduling": {
    "enabled": true,
    "timezone": "America/New_York",
    "checkInterval": 60000
  },
  "rateLimits": {
    "postsPerDay": 50,
    "postsPerHour": 10
  }
}
```

### 5. Install Dependencies

```bash
npm install
```

## Usage

### Immediate Posting

**Text post:**
```bash
npm run post -- "Hello LinkedIn! This is my first automated post."
```

**Post with image:**
```bash
npm run post -- --media ./image.jpg "Check out this amazing image!"
```

**Post with multiple images:**
```bash
npm run post -- --media ./img1.jpg,./img2.jpg,./img3.jpg "Gallery post"
```

**Post with video:**
```bash
npm run post -- --media ./video.mp4 "Watch this video"
```

**Organization post:**
```bash
npm run post -- --author organization "Official company announcement"
```

**Visibility control:**
```bash
npm run post -- --visibility CONNECTIONS "Post for connections only"
```

### Scheduling Posts

**Schedule for specific time:**
```bash
npm run schedule -- "Future post" "2026-01-10T14:00:00Z"
```

**Relative time:**
```bash
npm run schedule -- "Post in 2 hours" "2h"
npm run schedule -- "Post tomorrow" "1d"
npm run schedule -- "Post in 30 minutes" "30m"
```

**With media:**
```bash
npm run schedule -- "Scheduled image post" "2h" --media ./image.jpg
```

### Scheduler Service

**Start continuous scheduler:**
```bash
npm start
```

This runs in background and automatically publishes scheduled posts.

### Cleanup

**Remove old media and logs:**
```bash
npm run cleanup
```

**Targeted cleanup:**
```bash
npm run cleanup -- --media      # Only media files
npm run cleanup -- --logs       # Only log files
npm run cleanup -- --temp       # Only temp files
npm run cleanup -- --days 30    # Files older than 30 days
```

## Features

### Post Types

**Text Posts:**
- Up to 3,000 characters
- Hashtags supported
- @mentions supported
- URLs auto-linked

**Image Posts:**
- Up to 9 images per post
- Max 5MB per image
- Formats: JPG, PNG, GIF
- Auto-upload and optimization

**Video Posts:**
- Single video per post
- Max 200MB
- Max 10 minutes duration
- Formats: MP4, AVI, MOV

**Document Posts:**
- PDF, DOCX, PPTX supported
- Max 100MB per document
- Title and description

### Scheduling

**Precise Timing:**
- ISO 8601 format: `2026-01-10T14:00:00Z`
- Timezone support (config)
- Second-level precision

**Relative Times:**
- `30s`, `5m`, `2h`, `1d`, `1w`
- Easy scheduling without date math
- Converted to exact time automatically

**Optimal Times:**
- Configure best posting times
- Auto-suggest optimal slots
- Avoid off-hours posting

### Rate Limiting

**Automatic Management:**
- Tracks API calls per hour/day
- Enforces LinkedIn limits
- Exponential backoff on errors
- Queue overflow handling

**Configurable Limits:**
```json
{
  "rateLimits": {
    "postsPerDay": 50,
    "postsPerHour": 10,
    "backoffMultiplier": 2,
    "maxRetries": 3
  }
}
```

### Analytics

**Track Performance:**
- Impressions
- Clicks
- Likes
- Comments
- Shares
- Engagement rate

**Database Storage:**
```sql
SELECT post_id, likes, comments, shares 
FROM analytics 
WHERE created_at > datetime('now', '-7 days')
ORDER BY engagement_rate DESC;
```

### Media Management

**Auto-Upload:**
- Images uploaded to LinkedIn CDN
- Videos transcoded automatically
- Documents processed for preview

**Auto-Cleanup:**
- Remove local files after upload
- Configurable retention period
- Cleanup on schedule or manual

### Research Integration

**Automated Content:**
- Posts generated from research
- Auto-formatted with frontmatter
- Scheduled automatically
- Tracks research source

**Configuration:**
```json
{
  "research": {
    "enabled": true,
    "postsPerCycle": 5,
    "platform": "linkedin"
  }
}
```

## Testing

```bash
npm test
```

Runs 49 comprehensive tests (100% pass rate):
- Configuration validation
- LinkedIn API integration
- Scheduling logic
- Media uploads
- Rate limiting
- Database operations
- CLI scripts

## Monitoring

**Logs:**
```bash
tail -f logs/linkedin-YYYY-MM-DD.log
```

**Database:**
```bash
sqlite3 data/linkedin.db

# Recent posts
SELECT * FROM posts ORDER BY created_at DESC LIMIT 10;

# Scheduled posts
SELECT * FROM scheduled_posts WHERE status = 'pending';

# Analytics summary
SELECT COUNT(*), AVG(engagement_rate) FROM analytics;
```

## Common Issues

**Authentication failed:**
- Verify access token validity
- Check token expiration (90 days default)
- Regenerate token if needed

**Post failed:**
- Check rate limits
- Verify media file size/format
- Review error logs

**Scheduler not running:**
- Ensure `npm start` is active
- Check for errors in logs
- Verify scheduled_posts table

See [Troubleshooting](TROUBLESHOOTING.md) for more solutions.

## Production Deployment

See [Deployment Guide](DEPLOYMENT.md) for PM2 setup and production best practices.
