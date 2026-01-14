# Publishing Pipeline System Mapping

> Module: `Artifact/syndicate/src/publishing/`
> Last Updated: 2026-01-14

---

## Overview

The Publishing Pipeline handles content ingestion, approval, scheduling, and multi-platform distribution for Gladius's digital footprint.

---

## Components

| File | Class | Purpose | Status |
|------|-------|---------|--------|
| `__init__.py` | Module exports | Component loading | ✅ Active |
| `content_pipeline.py` | `ContentPipeline` | Ingest → Approve → Schedule flow | ✅ Production |
| `digital_footprint.py` | `DigitalFootprintController` | Full automation controller | ✅ Production |
| `format_adapter.py` | Various formatters | Platform-specific formatting | ✅ Production |
| `platform_router.py` | `PlatformRouter` | Multi-platform publishing | ✅ Production |

---

## Content Pipeline Commands

```python
from publishing import ContentPipeline, ContentType, ContentStatus

pipeline = ContentPipeline(
    data_dir='./data/publishing',
    output_dir='./output'
)

# Ingest Syndicate outputs (journals, reports)
ingested = pipeline.ingest_syndicate_outputs()
# Returns: List of ingested content items

# Get all drafts
drafts = pipeline.get_by_status(ContentStatus.DRAFT)

# Approve content for publishing
pipeline.approve_content(content_id)

# Schedule content for future publishing
from datetime import datetime, timedelta
schedule_time = datetime.now() + timedelta(hours=2)
pipeline.schedule_content(content_id, schedule_time)

# Get pending publications
pending = pipeline.get_pending_publications()

# Get statistics
stats = pipeline.get_stats()
# {'total_content': 50, 'by_status': {'draft': 10, 'approved': 5, 'published': 35}, ...}
```

---

## Format Adapters

### Discord Formatter
```python
from publishing import DiscordFormatter

formatter = DiscordFormatter()
formatted = formatter.format(
    content="# Gold Analysis\n\nBullish momentum...",
    title="Gold Update",
    metadata={'bias': 'bullish'}
)
# formatted.embeds contains rich embed structure
```

### LinkedIn Formatter
```python
from publishing import LinkedInFormatter

formatter = LinkedInFormatter()
formatted = formatter.format(content, title)
# Adds professional formatting, emojis, hashtags
# formatted.text contains formatted content
```

### Twitter Formatter
```python
from publishing import TwitterFormatter

formatter = TwitterFormatter()
formatted = formatter.format(long_content, title)
# Automatically threads if content > 280 chars
# formatted.metadata['is_thread'] indicates if threading needed
# formatted.metadata['parts'] contains thread parts
```

### Notion Formatter
```python
from publishing import NotionFormatter

formatter = NotionFormatter()
formatted = formatter.format(content, title)
# formatted.metadata['blocks'] contains Notion block structure
```

---

## Platform Router Commands

```python
from publishing import PlatformRouter
import asyncio

config = {
    'discord': {
        'enabled': True,
        'webhook_url': 'https://discord.com/api/webhooks/...'
    },
    'linkedin': {'enabled': True, 'access_token': '...'},
    'twitter': {'enabled': True, 'bearer_token': '...'},
    'notion': {'enabled': True, 'api_key': '...', 'database_id': '...'}
}

router = PlatformRouter(config)

# Test all connections
async def test():
    connections = await router.test_all_connections()
    # {'discord': True, 'linkedin': True, 'twitter': False, ...}

    # Publish to specific platform
    result = await router.publish_to_platform(
        'discord',
        'Market Analysis: Gold approaching resistance',
        'Gold Update'
    )
    # result.success, result.url, result.error

asyncio.run(test())
```

---

## Digital Footprint Controller

```python
from publishing import DigitalFootprintController, run_digital_footprint
import json
import asyncio

# Load config
with open('config/publishing.json') as f:
    config = json.load(f)

controller = DigitalFootprintController(
    config=config,
    data_dir='./data',
    output_dir='./output'
)

async def run():
    # Run full publish cycle
    results = await controller.run_publish_cycle()
    # {'ingested': 5, 'approved': 3, 'scheduled': 2, 'published': 3}

    # Get stats
    stats = controller.get_stats()
    # stats.total_content, stats.published, stats.publish_success_rate

    # Publish specific content now
    results = await controller.publish_now('content_id', ['discord', 'linkedin'])

    # Test platform connections
    connections = await controller.test_platforms()

asyncio.run(run())
controller.close()

# Quick convenience function
run_digital_footprint('./data', './output')
```

---

## Content Types

| Type | Description | Auto-Format |
|------|-------------|-------------|
| `JOURNAL` | Daily market journals | Discord embed, LinkedIn post |
| `REPORT` | Weekly/monthly reports | Discord attachment, LinkedIn article |
| `CATALYST` | Catalyst watchlists | Twitter thread, Discord list |
| `PREMARKET` | Pre-market plans | Discord embed, LinkedIn post |
| `ANALYSIS` | Technical analysis | All platforms |
| `ALERT` | Trade alerts | Discord + Twitter |

---

## Content Statuses

| Status | Description | Next Action |
|--------|-------------|-------------|
| `DRAFT` | Newly ingested content | Review/approve |
| `APPROVED` | Ready for scheduling | Schedule or publish |
| `SCHEDULED` | Scheduled for future | Auto-publish |
| `PUBLISHING` | Currently publishing | Wait |
| `PUBLISHED` | Successfully published | Archive |
| `FAILED` | Publishing failed | Retry or review |

---

## Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    PUBLISHING WORKFLOW                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Syndicate → Ingest → DRAFT → Approve → APPROVED            │
│                                    ↓                        │
│                              Schedule → SCHEDULED           │
│                                    ↓                        │
│                              Publish → PUBLISHING           │
│                                    ↓                        │
│                    Success → PUBLISHED    Fail → FAILED     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DISCORD_WEBHOOK_URL` | Discord webhook for publishing |
| `PUBLISH_ENABLED` | Enable publishing pipeline |
| `PUBLISH_AUTO_SCHEDULE` | Auto-schedule approved content |
| `PUBLISH_TIMEZONE` | Timezone for scheduling |
| `MAX_POSTS_PER_DAY` | Rate limit for posts |

---

## CLI Commands

```bash
# Run publish cycle from Syndicate
cd Artifact/syndicate
python -c "
from src.publishing import run_digital_footprint
run_digital_footprint('./data', './output')
"

# Test platform connections
python scripts/social_connector_debugger.py
```

---

*Generated by Gladius System Mapper*
