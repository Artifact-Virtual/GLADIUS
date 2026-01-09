# Arty Integration Setup Guide 🚀

This guide will help you set up the **Discord** and **LinkedIn** integrations for Arty in just a few minutes.

---

## 🟢 Part 1: Discord Bot Setup

### 1. Create the Config Files
Open a terminal in `C:\workspace\_gladius\arty\discord` and run:

```powershell
# Windows PowerShell
copy .env.example .env
copy config.example.json config.json
```

### 2. Get Your Credentials
Go to the **[Discord Developer Portal](https://discord.com/developers/applications)**.
1. Click **New Application** > Name it (e.g., "Arty").
2. Go to the **Bot** tab on the left > Click **Reset Token** > **Copy Token**.
3. Go to the **OAuth2** tab > Copy **Client ID**.

### 3. Edit `.env`
Open `.env` and paste your credentials:

```ini
DISCORD_TOKEN=paste_your_token_here
CLIENT_ID=paste_your_client_id_here
```

### 4. Install & Start
```powershell
npm install
npm run deploy-commands
npm start
```

---

## 🔵 Part 2: LinkedIn Automation Setup

### 1. Create the Config Files
Open a terminal in `C:\workspace\_gladius\arty\linkedin` and run:

```powershell
# Windows PowerShell
copy .env.example .env
copy config.example.json config.json
```

### 2. Get Your Credentials
Go to the **[LinkedIn Developers Portal](https://www.linkedin.com/developers/apps)**.
1. Click **Create App** > Fill in details > Link your Company Page.
2. Go to the **Auth** tab > Copy **Client ID** and **Client Secret**.
3. Under **OAuth 2.0 scopes**, ensure you request `w_member_social` (for personal) or `w_organization_social` (for company).

### 3. Edit `.env`
Open `.env` and paste your credentials:

```ini
LINKEDIN_CLIENT_ID=paste_your_client_id
LINKEDIN_CLIENT_SECRET=paste_your_client_secret
LINKEDIN_REDIRECT_URI=http://localhost:3000/callback
```
*(Note: You'll need to generate an Access Token using these credentials. Use a tool like Postman or a simple auth script to perform the OAuth 2.0 handshake to get your `LINKEDIN_ACCESS_TOKEN`)*.

### 4. Install & Start
```powershell
npm install
npm start
```

---

## ✅ Verification

Run the full test suite to make sure everything is connected:

```powershell
cd C:\workspace\_gladius\arty
npm test
```
