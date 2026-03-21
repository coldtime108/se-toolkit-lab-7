# Bot Testing Instructions

## Local Testing (on your Windows machine)

Since the project uses a Linux-based .venv, you need to either:
1. Use WSL with the project files
2. Test directly on the VM
3. Install uv globally on Windows

### Option 1: Install uv on Windows

Download and install uv from: https://github.com/astral-sh/uv/releases

Then run:
```powershell
cd c:\Users\timur\Desktop\c++\se-toolkit-lab-7\bot
uv sync
uv run bot.py --test "/start"
```

### Option 2: Test on VM (Recommended)

SSH to your VM:
```bash
ssh coldtime108@10.93.26.30
```

Pull your latest changes:
```bash
cd ~/se-toolkit-lab-7
git pull
```

Sync bot dependencies:
```bash
cd bot
.venv/bin/uv sync
```

Test the bot:
```bash
.venv/bin/uv run bot.py --test "/start"
.venv/bin/uv run bot.py --test "/help"
.venv/bin/uv run bot.py --test "/health"
.venv/bin/uv run bot.py --test "/labs"
.venv/bin/uv run bot.py --test "/scores lab-01"
```

Expected output for `/start`:
```
👋 Добро пожаловать в LMS Bot!

Я ваш помощник для взаимодействия с системой управления обучением.
Используйте /help, чтобы увидеть список доступных команд.
```

## Deploy Bot on VM

1. Create `.env.bot.secret` on VM:
```bash
cd ~/se-toolkit-lab-7/bot
cp .env.bot.example .env.bot.secret
nano .env.bot.secret
```

Fill in:
```text
BOT_TOKEN=8456337233:AAGvvClW7u6EjGaTIUysSKiQZHYZVxGfhh4
LMS_API_URL=http://localhost:42002
LMS_API_KEY=mysecretkey123
LLM_API_KEY=<your-qwen-key-from-step-1.9>
LLM_API_BASE_URL=http://localhost:42005/v1
LLM_API_MODEL=coder-model
```

2. Start the bot:
```bash
pkill -f "bot.py" 2>/dev/null; nohup .venv/bin/uv run bot.py > bot.log 2>&1 &
```

3. Check the log:
```bash
tail -20 bot.log
```

4. Test in Telegram: Open `t.me/my_lms_inno_bot` and send `/start`

## Troubleshooting

**Bot doesn't respond in Telegram:**
- Check log: `tail bot.log`
- Verify BOT_TOKEN is correct
- Check if bot is running: `ps aux | grep bot.py`

**Test mode fails:**
- Ensure `.env.bot.secret` exists
- Check LMS_API_URL is reachable: `curl http://localhost:42002/health`
- Verify LMS_API_KEY matches `.env.docker.secret`

**LLM not working:**
- Test LLM API: `curl http://localhost:42005/v1/models -H "Authorization: Bearer YOUR_KEY"`
- Ensure Qwen Code API is running on VM
