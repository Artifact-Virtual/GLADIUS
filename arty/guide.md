# Arty Integration Setup Guide 🚀

This guide will help you configure the **Centralized Environment** for all Arty integrations (Discord, LinkedIn, Telegram, Notion).

**Source of Truth:**
*   **Environment Variables:** `C:\workspace\_gladius\arty\.env`
*   **Configuration:** `C:\workspace\_gladius\arty\config.json`

---

## 🟢 Part 1: Centralized Setup

### 1. Edit the Master `.env`
Open `C:\workspace\_gladius\arty\.env` and fill in your credentials for all services.

**Discord:**
```ini
DISCORD_TOKEN=your_token
CLIENT_ID=your_id
GUILD_ID=your_guild_id
```

**LinkedIn:**
```ini
LINKEDIN_CLIENT_ID=your_id
LINKEDIN_CLIENT_SECRET=your_secret
LINKEDIN_ACCESS_TOKEN=your_oauth_token
```

**Telegram:**
```ini
TELEGRAM_BOT_TOKEN=your_botfather_token
```

**Notion:**
```ini
NOTION_API_KEY=your_integration_token
NOTION_DATABASE_ID=your_db_id
```

### 2. Edit the Master `config.json`
Open `C:\workspace\_gladius\arty\config.json`. This file controls behavior for all bots.
*   **Discord settings** are under `"discord": { ... }`
*   **LinkedIn settings** are under `"linkedin": { ... }`

---

## 🔵 Part 2: Running the Services

You can run any service from the `arty` root directory:

**Discord:**
```powershell
npm run discord:start
```

**LinkedIn:**
```powershell
npm run linkedin:start
```

**Telegram:**
```powershell
npm run telegram:start
```

**Notion:**
```powershell
npm run notion:start
```

---

## ✅ Verification

Run the test suite to ensure the centralized config is working:

```powershell
cd C:\workspace\_gladius\arty
npm test
```
