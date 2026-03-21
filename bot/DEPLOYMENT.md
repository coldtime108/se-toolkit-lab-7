# Bot Deployment Guide

## Overview

This guide covers containerization and deployment of the Telegram bot for Lab 7.

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  ┌──────────────┐     ┌──────────────────────────────────┐   │
│  │  Telegram    │────▶│  Bot Container                   │   │
│  │  User        │◀────│  (aiogram + LLM tool calling)    │   │
│  └──────────────┘     └──────┬───────────────────────────┘   │
│                              │                               │
│                              │ Tool calls via LLM             │
│                              ├───────▶ /start, /help         │
│                              ├───────▶ get_health, get_labs  │
│                              ├───────▶ get_scores, etc.      │
│                              │                               │
│  ┌──────────────┐     ┌──────┴───────┐                       │
│  │  Qwen API    │◀────│  LMS Backend │                       │
│  │  (on VM)     │     │  (FastAPI)   │                       │
│  └──────────────┘     └──────────────┘                       │
└──────────────────────────────────────────────────────────────┘
```

## Prerequisites

1. **Telegram Bot Token** — from [@BotFather](https://t.me/BotFather)
2. **Qwen Code API** — running on your VM at port 42005
3. **LMS Backend** — running via docker-compose
4. **LLM API Key** — from your Qwen Code setup

## Files

```
se-toolkit-lab-7/
├── bot/
│   ├── Dockerfile              ← Bot container definition
│   ├── bot.py                  ← Bot entry point
│   ├── handlers/               ← Command handlers
│   ├── services/               ← API clients (LMS, LLM)
│   ├── keyboards.py            ← Inline keyboard layouts
│   ├── config.py               ← Environment configuration
│   └── pyproject.toml          ← Python dependencies
├── docker-compose.yml          ← Bot service added
└── .env.docker.example         ← Bot environment variables
```

## Configuration

### 1. Create `.env.docker.secret`

Copy the example file and fill in your values:

```bash
cp .env.docker.example .env.docker.secret
nano .env.docker.secret
```

Required variables:

```text
# Bot Configuration
BOT_TOKEN=123456789:ABCdefGhIJKlmNoPQRsTUVwxyz

# LMS Backend (inside Docker network)
LMS_API_URL=http://backend:8000
LMS_API_KEY=my-secret-api-key

# LLM API (Qwen Code on VM)
LLM_API_KEY=your-qwen-api-key
LLM_API_BASE_URL=http://host.docker.internal:42005/v1
LLM_API_MODEL=coder-model
```

### 2. Qwen Code API Setup

The bot needs access to the Qwen Code API for intent classification.

**On your VM**, ensure Qwen API is running:

```bash
# Check if running
curl http://localhost:42005/v1/models -H "Authorization: Bearer YOUR_KEY"

# If not running, restart:
cd ~/qwen-code-oai-proxy
docker compose restart
```

## Deployment

### Option 1: Deploy with Docker Compose (Recommended)

1. **Build and start all services:**

   ```bash
   cd ~/se-toolkit-lab-7
   docker compose --env-file .env.docker.secret up --build -d
   ```

2. **Check bot status:**

   ```bash
   docker compose --env-file .env.docker.secret ps
   docker compose --env-file .env.docker.secret logs bot
   ```

3. **Test in Telegram:**
   
   Open your bot in Telegram and send `/start`.

### Option 2: Deploy Bot Separately

If backend is already running:

```bash
cd ~/se-toolkit-lab-7
docker compose --env-file .env.docker.secret up -d bot
```

### Option 3: Run Without Docker (Development)

```bash
cd ~/se-toolkit-lab-7/bot
.venv/bin/uv sync
.venv/bin/uv run bot.py
```

## Testing

### Test Mode (No Telegram Connection)

```bash
cd ~/se-toolkit-lab-7/bot

# Test commands
.venv/bin/uv run bot.py --test "/start"
.venv/bin/uv run bot.py --test "/help"
.venv/bin/uv run bot.py --test "/health"
.venv/bin/uv run bot.py --test "/labs"
.venv/bin/uv run bot.py --test "/scores lab-01"

# Test natural language
.venv/bin/uv run bot.py --test "what labs are available"
.venv/bin/uv run bot.py --test "show me scores for lab 4"
```

### Live Testing in Telegram

1. Open your bot: `t.me/YOUR_BOT_NAME`
2. Send commands:
   - `/start` — Welcome message with keyboard
   - `/help` — List of commands
   - `/health` — Backend status
   - `/labs` — Available labs with buttons
   - `/scores lab-01` — Scores for specific lab
3. Try natural language:
   - "What labs are available?"
   - "Show me scores for lab 4"
   - "Is the system working?"

## Monitoring

### View Logs

```bash
# Real-time logs
docker compose --env-file .env.docker.secret logs -f bot

# Last 100 lines
docker compose --env-file .env.docker.secret logs --tail=100 bot
```

### Health Check

```bash
# Check if bot container is running
docker compose --env-file .env.docker.secret ps bot

# Check bot response (via Telegram API)
# Send /health command in Telegram
```

## Troubleshooting

### Bot doesn't respond in Telegram

1. **Check logs:**
   ```bash
   docker compose --env-file .env.docker.secret logs bot
   ```

2. **Verify BOT_TOKEN:**
   ```bash
   docker compose --env-file .env.docker.secret config | grep BOT_TOKEN
   ```

3. **Check if another bot process is running:**
   ```bash
   ps aux | grep bot.py
   pkill -f "bot.py"
   ```

### LLM errors (HTTP 401/403)

1. **Verify LLM_API_KEY:**
   ```bash
   curl http://localhost:42005/v1/models -H "Authorization: Bearer YOUR_KEY"
   ```

2. **Restart Qwen proxy:**
   ```bash
   cd ~/qwen-code-oai-proxy
   docker compose restart
   ```

### Backend connection errors

1. **Check backend is running:**
   ```bash
   docker compose --env-file .env.docker.secret ps backend
   curl http://localhost:42002/health -H "Authorization: Bearer YOUR_KEY"
   ```

2. **Verify LMS_API_URL:**
   - Inside Docker: `http://backend:8000`
   - Outside Docker: `http://localhost:42002`

### Bot container exits immediately

1. **Check environment variables:**
   ```bash
   docker compose --env-file .env.docker.secret config
   ```

2. **Rebuild container:**
   ```bash
   docker compose --env-file .env.docker.secret up -d --build bot
   ```

## Tool Calling Architecture

The bot uses **LLM function calling** to route user requests to appropriate tools:

### Available Tools (9):

| Tool | Description | Parameters |
|------|-------------|------------|
| `get_health` | Check backend status | — |
| `list_labs` | List all labs | — |
| `get_scores` | Get lab scores | `lab_id` |
| `get_analytics` | Get analytics data | `metric`, `lab_id` |
| `get_tasks` | Get tasks for lab | `lab_id` |
| `get_learners` | Get student list | `group` |
| `get_submissions` | Get submissions | `lab_id`, `limit` |
| `get_interactions` | Get interactions | `user_id` |
| `sync_data` | Trigger ETL sync | — |

### Example Flow:

1. User: "Show me scores for lab 4"
2. LLM classifies intent → calls `get_scores(lab_id="lab-04")`
3. Bot executes tool → calls LMS API
4. Bot returns formatted response with scores

## Security Notes

- **Never commit `.env.docker.secret`** — it's in `.gitignore`
- **Keep BOT_TOKEN secure** — anyone with the token can control your bot
- **Use HTTPS for LLM API** — if deploying outside local network
- **Rotate tokens periodically** — especially if compromised

## Cleanup

```bash
# Stop bot only
docker compose --env-file .env.docker.secret stop bot

# Stop all services
docker compose --env-file .env.docker.secret down

# Remove bot container
docker compose --env-file .env.docker.secret rm -f bot
```

## Next Steps

After deployment:

1. ✅ Test all commands in Telegram
2. ✅ Verify natural language queries work
3. ✅ Check inline keyboard buttons respond
4. ✅ Monitor logs for errors
5. ✅ Document any custom configurations

---

**Lab 7 Complete!** 🎉

Your bot is now:
- Containerized with Docker
- Integrated with LMS backend
- Using LLM for natural language understanding
- Deployed and running on VM
