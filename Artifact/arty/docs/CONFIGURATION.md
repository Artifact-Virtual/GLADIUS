# Configuration Reference

Complete configuration guide for all Arty modules.

## Overview

Arty uses two configuration layers:
1. **Environment Variables** (`.env`) - Secrets and credentials
2. **Configuration Files** (`config.json`) - Features and behavior

## Research Engine

### Environment Variables (`research/.env`)

```env
# Search APIs (choose one or more)
BRAVE_SEARCH_API_KEY=your_brave_key
SERPER_API_KEY=your_serper_key
SERPAPI_KEY=your_serpapi_key

# Storage paths (optional)
STORAGE_PATH=../store
DATABASE_PATH=../store/research.db
VECTOR_DB_PATH=../store/vector.db

# Logging
LOG_LEVEL=info
LOG_PATH=./logs
```

### Configuration File (`research/config.json`)

```json
{
  "research": {
    "broadField": "artificial intelligence",
    "targetedField": "machine learning",
    "enabled": true,
    "cycleFrequency": "daily",
    "iterations": 3,
    "keywordsPerIteration": 10,
    "maxResultsPerSearch": 20,
    "searchAPIs": {
      "brave": { "enabled": true, "priority": 1 },
      "serper": { "enabled": true, "priority": 2 },
      "serpapi": { "enabled": false, "priority": 3 }
    },
    "analysis": {
      "tfidfThreshold": 0.5,
      "minKeywordFrequency": 3,
      "maxKeywordsPerDocument": 50,
      "entityRecognition": true
    },
    "contentGeneration": {
      "enabled": true,
      "postsPerCycle": 5,
      "platforms": ["linkedin", "discord"],
      "formatting": {
        "frontmatter": true,
        "markdown": true,
        "wordLimit": 300
      }
    },
    "cleanup": {
      "enabled": true,
      "oldArticles": "30d",
      "oldDrafts": "7d",
      "oldSearchResults": "14d",
      "oldLogs": "60d"
    }
  },
  "engagement": {
    "discord": {
      "enabled": true,
      "frequency": "3h",
      "topicsPerCycle": 5,
      "contextWindow": 5,
      "messageLength": 200
    }
  },
  "storage": {
    "vectorEmbeddings": true,
    "fileSystem": true,
    "cacheEnabled": true,
    "cacheExpiry": "24h"
  }
}
```

## Discord Bot

### Environment Variables (`discord/.env`)

```env
# Bot authentication
DISCORD_TOKEN=your_bot_token
CLIENT_ID=your_application_id
GUILD_ID=your_test_server_id
OWNER_ID=your_discord_user_id

# Database
DATABASE_PATH=./data/discord.db

# Logging
LOG_LEVEL=info
LOG_PATH=./logs
```

### Configuration File (`discord/config.json`)

```json
{
  "prefix": "!",
  "features": {
    "welcome": {
      "enabled": true,
      "channelId": "123456789",
      "message": "Welcome {user} to {server}!",
      "embed": true,
      "dm": false,
      "autorole": ""
    },
    "goodbye": {
      "enabled": true,
      "channelId": "123456789",
      "message": "Goodbye {user}!"
    },
    "automod": {
      "enabled": true,
      "spam": {
        "enabled": true,
        "maxMessages": 5,
        "timeWindow": 5,
        "action": "timeout"
      },
      "mentions": {
        "enabled": true,
        "maxMentions": 5,
        "action": "warn"
      },
      "emoji": {
        "enabled": true,
        "maxEmoji": 10,
        "action": "delete"
      },
      "badWords": {
        "enabled": true,
        "words": ["word1", "word2"],
        "action": "delete"
      },
      "invites": {
        "enabled": true,
        "action": "delete"
      }
    },
    "economy": {
      "enabled": true,
      "currency": "coins",
      "dailyReward": 100,
      "workReward": [10, 50],
      "bankCapacity": 10000
    },
    "leveling": {
      "enabled": true,
      "xpPerMessage": 15,
      "xpRange": [10, 20],
      "cooldown": 60,
      "stackRoles": false,
      "levelRoles": {
        "5": "role_id",
        "10": "role_id",
        "25": "role_id"
      }
    },
    "logging": {
      "enabled": true,
      "messageLog": "channel_id",
      "memberLog": "channel_id",
      "modLog": "channel_id",
      "voiceLog": "channel_id",
      "webhook": ""
    },
    "moderation": {
      "warnings": {
        "enabled": true,
        "thresholds": {
          "3": "timeout",
          "5": "kick",
          "7": "ban"
        }
      }
    }
  },
  "permissions": {
    "ownerOnly": ["setup"],
    "adminOnly": [],
    "modOnly": ["kick", "ban", "warn", "timeout", "clear"]
  }
}
```

## LinkedIn Automation

### Environment Variables (`linkedin/.env`)

```env
# LinkedIn OAuth
LINKEDIN_CLIENT_ID=your_client_id
LINKEDIN_CLIENT_SECRET=your_client_secret
LINKEDIN_ACCESS_TOKEN=your_access_token
LINKEDIN_REFRESH_TOKEN=your_refresh_token

# LinkedIn URNs
LINKEDIN_PERSON_URN=urn:li:person:XXXXXXXX
LINKEDIN_ORGANIZATION_URN=urn:li:organization:XXXXXXXX

# Storage
DATABASE_PATH=./data/linkedin.db
MEDIA_PATH=./media
TEMP_PATH=./temp

# Logging
LOG_LEVEL=info
LOG_PATH=./logs
```

### Configuration File (`linkedin/config.json`)

```json
{
  "authentication": {
    "oauth2": {
      "clientId": "",
      "clientSecret": "",
      "redirectUri": "http://localhost:3000/callback",
      "scopes": [
        "w_member_social",
        "r_liteprofile",
        "r_emailaddress"
      ]
    },
    "tokenRefresh": {
      "enabled": true,
      "refreshBeforeExpiry": "7d"
    }
  },
  "posting": {
    "defaultVisibility": "PUBLIC",
    "defaultAuthor": "person",
    "contentTypes": {
      "text": true,
      "image": true,
      "video": true,
      "document": true
    },
    "limits": {
      "textLength": 3000,
      "imagesPerPost": 9,
      "imageMaxSize": 5242880,
      "videoMaxSize": 209715200,
      "documentMaxSize": 104857600
    }
  },
  "scheduling": {
    "enabled": true,
    "timezone": "America/New_York",
    "checkInterval": 60000,
    "retryFailed": true,
    "maxRetries": 3,
    "optimalTimes": {
      "weekday": ["09:00", "12:00", "17:00"],
      "weekend": ["10:00", "14:00"]
    }
  },
  "rateLimits": {
    "enabled": true,
    "postsPerDay": 50,
    "postsPerHour": 10,
    "apiCallsPerMinute": 60,
    "backoff": {
      "enabled": true,
      "multiplier": 2,
      "maxDelay": 300000
    }
  },
  "media": {
    "storage": {
      "path": "./media",
      "tempPath": "./temp"
    },
    "formats": {
      "image": ["jpg", "jpeg", "png", "gif"],
      "video": ["mp4", "avi", "mov"],
      "document": ["pdf", "docx", "pptx"]
    },
    "cleanup": {
      "enabled": true,
      "afterUpload": true,
      "oldFiles": "7d"
    }
  },
  "analytics": {
    "enabled": true,
    "tracking": {
      "impressions": true,
      "clicks": true,
      "engagement": true
    },
    "updateInterval": "1h",
    "reports": {
      "enabled": true,
      "frequency": "weekly"
    }
  },
  "cleanup": {
    "enabled": true,
    "schedule": "0 2 * * *",
    "targets": {
      "media": true,
      "logs": true,
      "temp": true
    },
    "retention": {
      "media": "7d",
      "logs": "30d",
      "temp": "1d"
    }
  }
}
```

## Storage Layer

### File System (`store/file_system/settings/context.json`)

```json
{
  "arty": {
    "version": "1.0.0",
    "lastUpdate": "2026-01-08T21:00:00Z",
    "modules": {
      "discord": {
        "enabled": true,
        "version": "1.0.0",
        "path": "../discord"
      },
      "linkedin": {
        "enabled": true,
        "version": "1.0.0",
        "path": "../linkedin"
      },
      "research": {
        "enabled": true,
        "version": "1.0.0",
        "path": "../research"
      },
      "store": {
        "enabled": true,
        "version": "1.0.0",
        "path": "./"
      }
    },
    "structure": {
      "files": {},
      "directories": {}
    }
  }
}
```

## Workspace Configuration

### Root Package.json (`arty/package.json`)

```json
{
  "name": "arty",
  "version": "1.0.0",
  "description": "Autonomous Research Team",
  "workspaces": [
    "discord",
    "linkedin",
    "research"
  ],
  "scripts": {
    "discord:install": "cd discord && npm install",
    "discord:deploy": "cd discord && npm run deploy-commands",
    "discord:start": "cd discord && npm start",
    "discord:test": "cd discord && npm test",
    "linkedin:install": "cd linkedin && npm install",
    "linkedin:start": "cd linkedin && npm start",
    "linkedin:post": "cd linkedin && npm run post",
    "linkedin:schedule": "cd linkedin && npm run schedule",
    "linkedin:test": "cd linkedin && npm test",
    "research:install": "cd research && npm install",
    "research:init": "cd store && node init-databases.js",
    "research:cycle": "cd research && npm run research:cycle",
    "research:start": "cd research && npm start",
    "test": "npm run discord:test && npm run linkedin:test"
  }
}
```

## Configuration Tips

**Security:**
- Never commit `.env` files
- Use `.env.example` as templates
- Rotate tokens regularly
- Use environment-specific configs

**Performance:**
- Adjust rate limits based on API tier
- Configure caching for cost optimization
- Set appropriate cleanup schedules
- Monitor log sizes

**Customization:**
- Start with example configs
- Modify incrementally
- Test changes before production
- Document custom settings

See specific module guides for detailed configuration:
- [Discord Guide](DISCORD.md)
- [LinkedIn Guide](LINKEDIN.md)
- [Research Engine](RESEARCH.md)
