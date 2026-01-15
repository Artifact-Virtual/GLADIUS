# LEGION Enterprise - Quick Start Guide

## ✅ System Fixed and Ready

All critical issues have been resolved. The system is now operational.

---

## 🚀 Start the System (3 Steps)

### Step 1: Navigate to Directory
```bash
cd /home/runner/work/LEGION/LEGION
```

### Step 2: Run Startup Script
```bash
python start_enterprise.py
```

This will automatically:
- Create/activate virtual environment
- Install all dependencies
- Initialize databases
- Start backend API (port 5001)
- Build and serve frontend (port 3000)

### Step 3: Access Dashboard
Open your browser to:
```
http://localhost:3000
```

**That's it!** The system is now running.

---

## ⚡ Alternative: Manual Start

If you prefer manual control:

```bash
# Activate virtual environment
source venv/bin/activate

# Start backend (terminal 1)
python backend_api.py

# Start frontend (terminal 2)
npx serve -s build -l 3000
```

---

## 🔍 Verify Everything Works

### Check Backend Health
```bash
curl http://localhost:5001/api/health
```

Should return JSON with `"status": "healthy"`

### Check Frontend
Open `http://localhost:3000` in browser - should see dashboard

### Check Databases
```bash
ls -lh data/enterprise_operations.db
# Should show ~236KB file
```

---

## 📋 What Was Fixed

1. ✅ **Python shebang** - Changed from `python4` to `python3`
2. ✅ **Hard-coded paths** - All paths now relative/configurable
3. ✅ **Package versions** - Fixed react-scripts version
4. ✅ **Dependencies** - All Python and Node packages installed
5. ✅ **Database bugs** - Fixed initialization errors
6. ✅ **Rate limiter** - Fixed enum handling

**Result**: System fully operational with all 26 AI agents ready.

---

## 🤖 AI Features Available

The system includes AI/LLM integration with 8 provider options:

1. **Ollama** (local, recommended)
2. llama.cpp (local GGUF)
3. LocalAI
4. LM Studio
5. OpenAI
6. Google Gemini
7. Anthropic Claude
8. Hugging Face

### To Enable AI (Optional)

#### Option 1: Ollama (Easiest)
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model
ollama pull deepseek-r1:latest

# Start Ollama
ollama serve
```

#### Option 2: OpenAI
Create `config/.env`:
```bash
OPENAI_API_KEY=your_key_here
```

Edit `config/llm_config.json`:
```json
{
  "providers": {
    "openai": {
      "enabled": true,
      "api_key": "${OPENAI_API_KEY}",
      "model": "gpt-4"
    }
  }
}
```

---

## 🔧 Optional Configuration

### Add External API Keys
Create `config/.env`:
```bash
# Financial APIs
COINGECKO_API_KEY=your_key

# News
NEWSAPI_KEY=your_key

# AI Providers
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
GEMINI_API_KEY=your_key
```

### Email Notifications
Edit `config/integrations.json`:
```json
{
  "email": {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "username": "your_email@gmail.com",
    "password": "your_app_password",
    "use_tls": true
  }
}
```

---

## 📊 System Components

### Backend API (Port 5001)
- REST endpoints for all operations
- WebSocket for real-time updates
- Database management
- Rate limiting and caching
- Health monitoring

### Frontend Dashboard (Port 3000)
- AMOLED dark theme
- 7 specialized dashboards:
  1. Command Dashboard
  2. Operations Dashboard
  3. Intelligence Dashboard
  4. Coordination Dashboard
  5. Management Dashboard
  6. Optimization Dashboard
  7. API Monitoring Dashboard

### Databases
- `data/enterprise_operations.db` - Main database (25 tables)
- `legion/active_system.db` - Agent operations
- Automated hourly backups to `backups/`

### AI Agents (26 Total)
Across 7 domains:
- Financial Intelligence (4)
- Operations (4)
- Business Intelligence (6)
- Communication (3)
- Integration (5)
- Legal & Compliance (2)
- Customer Intelligence (2)

---

## 🛠️ Troubleshooting

### Port Already in Use
```bash
# Find and kill process on port 5001
lsof -ti:5001 | xargs kill -9

# Find and kill process on port 3000
lsof -ti:3000 | xargs kill -9
```

### Dependencies Missing
```bash
# Reinstall Python packages
source venv/bin/activate
pip install -r requirements.txt

# Reinstall Node packages
npm install
```

### Database Issues
```bash
# Reinitialize database
source venv/bin/activate
python initialize_database_schema.py
```

### Frontend Not Building
```bash
# Clean and rebuild
rm -rf build node_modules
npm install
npm run build
```

---

## 📚 More Information

- **Full Report**: `SYSTEM_INVESTIGATION_REPORT.md`
- **Architecture**: `ARCHITECTURE.md`
- **Main Docs**: `README.md`
- **Security**: `SECURITY.md`

---

## 🎯 Next Steps

1. ✅ System is running
2. Browse dashboard at http://localhost:3000
3. Check backend health at http://localhost:5001/api/health
4. (Optional) Configure AI provider
5. (Optional) Add external API keys
6. (Optional) Run `npm audit fix` for security updates

---

## 🆘 Need Help?

1. Check logs in `logs/` directory
2. Review `SYSTEM_INVESTIGATION_REPORT.md`
3. Check browser console (F12) for frontend issues
4. Check terminal output for backend issues

---

**System Status**: ✅ Operational  
**Version**: 1.0.0  
**Last Updated**: January 13, 2026
