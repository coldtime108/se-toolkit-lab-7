# Инструкции по настройке VM для Lab 7

Подключитесь к VM:
```bash
ssh coldtime108@10.93.26.30
```
Пароль: `innopolisTimurA!`

## Шаг 1: Остановить Lab 6 (если запущен)

```bash
cd ~/se-toolkit-lab-6 2>/dev/null && docker compose --env-file .env.docker.secret down
cd ~
```

## Шаг 2: Клонировать репозиторий (или обновить)

```bash
# Если репозиторий уже есть, обновить
if [ -d ~/se-toolkit-lab-7 ]; then
    cd ~/se-toolkit-lab-7
    git pull
else
    # Клонировать ваш форк
    git clone https://github.com/coldtime108/se-toolkit-lab-7 ~/se-toolkit-lab-7
    cd ~/se-toolkit-lab-7
fi
```

## Шаг 3: Создать файл окружения

```bash
cp .env.docker.example .env.docker.secret
```

Отредактируйте `.env.docker.secret` (уже должен быть настроен локально, можно скопировать значения).

## Шаг 4: Настроить DNS для Docker

```bash
sudo tee /etc/docker/daemon.json <<'EOF'
{
  "dns": ["8.8.8.8", "8.8.4.4"]
}
EOF
sudo systemctl restart docker
```

## Шаг 5: Запустить сервисы

```bash
cd ~/se-toolkit-lab-7
docker compose --env-file .env.docker.secret up --build -d
```

Проверить статус:
```bash
docker compose --env-file .env.docker.secret ps
```

## Шаг 6: Выполнить ETL синхронизацию

```bash
curl -X POST http://localhost:42002/pipeline/sync \
  -H "Authorization: Bearer mysecretkey123" \
  -H "Content-Type: application/json" \
  -d '{}'
```

Проверить данные:
```bash
curl -s http://localhost:42002/items/ -H "Authorization: Bearer mysecretkey123" | head -c 200
```

## Шаг 7: Настроить SSH для autochecker

```bash
mkdir -p ~/.ssh
echo 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIKiL0DDQZw7L0Uf1c9cNlREY7IS6ZkIbGVWNsClqGNCZ se-toolkit-autochecker' >> ~/.ssh/authorized_keys
chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys
```

## Шаг 8: Настроить Qwen Code API (если ещё не настроено)

Проверить, работает ли Qwen API:
```bash
curl -s http://localhost:42005/v1/models 2>/dev/null || echo "Qwen API not running"
```

Если не работает, нужно настроить по инструкции: [Qwen Code API Deployment](../../wiki/qwen-code-api-deployment.md)

## Шаг 9: Создать файл для бота

```bash
cd ~/se-toolkit-lab-7
cp .env.bot.example .env.bot.secret
nano .env.bot.secret
```

Заполните значения:
```text
BOT_TOKEN=8456337233:AAGvvClW7u6EjGaTIUysSKiQZHYZVxGfhh4
LMS_API_URL=http://localhost:42002
LMS_API_KEY=mysecretkey123
LLM_API_KEY=<your-qwen-key>
LLM_API_BASE_URL=http://localhost:42005/v1
LLM_API_MODEL=coder-model
```

## Шаг 10: Проверить работу LLM

```bash
curl -s http://localhost:42005/v1/chat/completions \
  -H "Authorization: Bearer YOUR_QWEN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"coder-model","messages":[{"role":"user","content":"Hello"}]}'
```

---

После выполнения всех шагов, вернитесь и сообщите, что VM готова.
