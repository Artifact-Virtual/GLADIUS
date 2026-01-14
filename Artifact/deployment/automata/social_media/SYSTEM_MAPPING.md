# Social Media System Mapping

> Module: `Artifact/deployment/automata/social_media/`
> Last Updated: 2026-01-14

---

## Overview

The Social Media module provides unified platform adapters for publishing content across multiple social networks.

---

## Components

| File | Class | Purpose | Status |
|------|-------|---------|--------|
| `__init__.py` | Module exports | Platform connector loading | ✅ Active |
| `base_platform.py` | `BasePlatform` | Abstract base for all connectors | ✅ Production |
| `manager.py` | `SocialMediaManager` | Orchestrates multi-platform publishing | ✅ Production |
| `platforms/twitter_connector.py` | `TwitterConnector` | Twitter/X API v2 integration | ✅ Configured |
| `platforms/linkedin_connector.py` | `LinkedInConnector` | LinkedIn API integration | ✅ Configured |
| `platforms/facebook_connector.py` | `FacebookConnector` | Facebook Graph API | ✅ Configured |
| `platforms/instagram_connector.py` | `InstagramConnector` | Instagram Graph API | ✅ Configured |
| `platforms/youtube_connector.py` | `YouTubeConnector` | YouTube Data API v3 | 🔲 Keys Pending |

---

## Platform Commands

### Twitter/X
```python
from automata.social_media.platforms.twitter_connector import TwitterConnector

connector = TwitterConnector(config)
await connector.authenticate()

# Post tweet
result = await connector.post_tweet("Market Analysis: Gold approaching resistance")

# Post thread
result = await connector.post_thread(["Part 1...", "Part 2...", "Part 3..."])

# Get account info
info = await connector.get_account_info()
```

### LinkedIn
```python
from automata.social_media.platforms.linkedin_connector import LinkedInConnector

connector = LinkedInConnector(config)
await connector.authenticate()

# Post to personal profile
result = await connector.post_update(content, visibility="PUBLIC")

# Post to company page
result = await connector.post_to_organization(content, org_urn)

# Share article
result = await connector.share_article(article_url, commentary)
```

### Facebook
```python
from automata.social_media.platforms.facebook_connector import FacebookConnector

connector = FacebookConnector(config)
await connector.authenticate()

# Post to page
result = await connector.post_to_page(content)

# Post with image
result = await connector.post_to_page(content, image_path="path/to/image.png")

# Get page insights
insights = await connector.get_page_insights()
```

### Instagram
```python
from automata.social_media.platforms.instagram_connector import InstagramConnector

connector = InstagramConnector(config)
await connector.authenticate()

# Post image
result = await connector.post_image(image_url, caption)

# Post carousel
result = await connector.post_carousel([image1, image2], caption)

# Get account info
info = await connector.get_account_info()
```

### YouTube
```python
from automata.social_media.platforms.youtube_connector import YouTubeConnector

connector = YouTubeConnector(config)
await connector.authenticate()

# Update video description
result = await connector.update_video_description(video_id, description)

# Add to playlist
result = await connector.add_to_playlist(playlist_id, video_id)
```

---

## Unified Manager Commands

```python
from automata.social_media.manager import SocialMediaManager

manager = SocialMediaManager(config)

# Test all connections
results = await manager.test_all_connections()

# Publish to all enabled platforms
results = await manager.publish_to_all(content, title)

# Publish to specific platforms
results = await manager.publish_to_platforms(["twitter", "linkedin"], content, title)

# Get analytics
analytics = await manager.get_all_analytics()
```

---

## Environment Variables

| Variable | Description | Platform |
|----------|-------------|----------|
| `TWITTER_API_KEY` | Twitter API Key | Twitter |
| `TWITTER_API_SECRET` | Twitter API Secret | Twitter |
| `TWITTER_ACCESS_TOKEN` | OAuth Access Token | Twitter |
| `TWITTER_ACCESS_TOKEN_SECRET` | OAuth Access Token Secret | Twitter |
| `TWITTER_BEARER_TOKEN` | Bearer Token for v2 API | Twitter |
| `TWITTER_ENABLED` | Enable Twitter publishing | Twitter |
| `LINKEDIN_ACCESS_TOKEN` | OAuth 2.0 Access Token | LinkedIn |
| `LINKEDIN_ORGANIZATION_URN` | Company page URN | LinkedIn |
| `LINKEDIN_ENABLED` | Enable LinkedIn publishing | LinkedIn |
| `FACEBOOK_APP_ID` | Facebook App ID | Facebook |
| `FACEBOOK_APP_SECRET` | Facebook App Secret | Facebook |
| `FACEBOOK_ACCESS_TOKEN` | Page Access Token | Facebook |
| `FACEBOOK_PAGE_ID` | Facebook Page ID | Facebook |
| `FACEBOOK_ENABLED` | Enable Facebook publishing | Facebook |
| `INSTAGRAM_ACCESS_TOKEN` | Instagram Graph API Token | Instagram |
| `INSTAGRAM_BUSINESS_ACCOUNT_ID` | Business Account ID | Instagram |
| `INSTAGRAM_ENABLED` | Enable Instagram publishing | Instagram |
| `YOUTUBE_API_KEY` | YouTube Data API Key | YouTube |
| `YOUTUBE_CLIENT_ID` | OAuth Client ID | YouTube |
| `YOUTUBE_CLIENT_SECRET` | OAuth Client Secret | YouTube |
| `YOUTUBE_REFRESH_TOKEN` | OAuth Refresh Token | YouTube |
| `YOUTUBE_ENABLED` | Enable YouTube publishing | YouTube |

---

## Rate Limits

| Platform | Posts/Day | Posts/Hour | Notes |
|----------|-----------|------------|-------|
| Twitter | 2400 | 100 | Tweets + retweets |
| LinkedIn | 100 | 25 | Posts only |
| Facebook | Unlimited | ~200 | Page-level |
| Instagram | 25 | 10 | Image posts |
| YouTube | N/A | N/A | Video upload limits vary |

---

## Testing

```bash
# Test all connectors
python scripts/social_connector_debugger.py

# Test specific platform
python -c "
import asyncio
from automata.social_media.platforms.twitter_connector import TwitterConnector
# ... test code
"
```

---

*Generated by Gladius System Mapper*
