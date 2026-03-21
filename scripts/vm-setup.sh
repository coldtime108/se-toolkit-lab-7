#!/bin/bash
# Lab 7 VM Setup Script
# Run this on your VM after SSH login

set -e

echo "=== Lab 7 VM Setup ==="
echo ""

# Step 1: Stop Lab 6 if running
echo "Step 1: Stopping Lab 6 services..."
if [ -d ~/se-toolkit-lab-6 ]; then
    cd ~/se-toolkit-lab-6
    docker compose --env-file .env.docker.secret down 2>/dev/null || true
    echo "Lab 6 stopped."
else
    echo "Lab 6 not found, skipping."
fi
cd ~
echo ""

# Step 2: Clone or update repo
echo "Step 2: Cloning/updating se-toolkit-lab-7..."
if [ -d ~/se-toolkit-lab-7 ]; then
    cd ~/se-toolkit-lab-7
    git pull
    echo "Repository updated."
else
    git clone https://github.com/coldtime108/se-toolkit-lab-7 ~/se-toolkit-lab-7
    echo "Repository cloned."
fi
cd ~/se-toolkit-lab-7
echo ""

# Step 3: Create .env.docker.secret if not exists
echo "Step 3: Setting up .env.docker.secret..."
if [ ! -f .env.docker.secret ]; then
    cp .env.docker.example .env.docker.secret
    echo "Created .env.docker.secret from example."
else
    echo ".env.docker.secret already exists."
fi
echo ""

# Step 4: Configure Docker DNS
echo "Step 4: Configuring Docker DNS..."
sudo tee /etc/docker/daemon.json <<'EOF'
{
  "dns": ["8.8.8.8", "8.8.4.4"]
}
EOF
sudo systemctl restart docker
echo "Docker DNS configured."
echo ""

# Step 5: Start services
echo "Step 5: Starting Docker services..."
docker compose --env-file .env.docker.secret up --build -d
echo "Services started."
echo ""

# Step 6: Wait for backend to be ready
echo "Step 6: Waiting for backend to be ready..."
sleep 10
echo "Checking backend health..."
curl -s http://localhost:42002/health -H "Authorization: Bearer mysecretkey123" || echo "Backend not ready yet, continuing..."
echo ""

# Step 7: Run ETL sync
echo "Step 7: Running ETL sync..."
curl -X POST http://localhost:42002/pipeline/sync \
  -H "Authorization: Bearer mysecretkey123" \
  -H "Content-Type: application/json" \
  -d '{}'
echo ""
echo "ETL sync completed."
echo ""

# Step 8: Setup SSH for autochecker
echo "Step 8: Setting up SSH for autochecker..."
mkdir -p ~/.ssh
echo 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIKiL0DDQZw7L0Uf1c9cNlREY7IS6ZkIbGVWNsClqGNCZ se-toolkit-autochecker' >> ~/.ssh/authorized_keys
chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys 2>/dev/null || true
echo "SSH setup complete."
echo ""

# Step 9: Check Qwen API
echo "Step 9: Checking Qwen Code API..."
if curl -s http://localhost:42005/v1/models > /dev/null 2>&1; then
    echo "Qwen API is running."
else
    echo "WARNING: Qwen API not running. Set it up manually."
    echo "See: wiki/qwen-code-api-deployment.md"
fi
echo ""

# Step 10: Create .env.bot.secret
echo "Step 10: Creating .env.bot.secret..."
cd ~/se-toolkit-lab-7/bot
if [ ! -f .env.bot.secret ]; then
    cp .env.bot.example .env.bot.secret
    echo ""
    echo "Please edit .env.bot.secret and fill in:"
    echo "  BOT_TOKEN=8456337233:AAGvvClW7u6EjGaTIUysSKiQZHYZVxGfhh4"
    echo "  LMS_API_URL=http://localhost:42002"
    echo "  LMS_API_KEY=mysecretkey123"
    echo "  LLM_API_KEY=<your-qwen-key>"
    echo "  LLM_API_BASE_URL=http://localhost:42005/v1"
    echo "  LLM_API_MODEL=coder-model"
    echo ""
    echo "Edit with: nano .env.bot.secret"
else
    echo ".env.bot.secret already exists."
fi
echo ""

echo "=== Setup Complete! ==="
echo ""
echo "Next steps:"
echo "1. Edit bot/.env.bot.secret with your tokens"
echo "2. Test the bot: cd bot && .venv/bin/uv run bot.py --test '/start'"
echo "3. Deploy the bot: nohup .venv/bin/uv run bot.py > bot.log 2>&1 &"
echo "4. Test in Telegram: t.me/my_lms_inno_bot"
