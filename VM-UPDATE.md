# 🔄 VM Update Instructions

## Для обновления кода на VM (после push в GitHub):

### 1. Подключитесь к VM:
```bash
ssh coldtime108@10.93.26.30
# Пароль: innopolisTimurA!
```

### 2. Обновите код:
```bash
cd ~/se-toolkit-lab-7
git pull
```

### 3. Проверьте test mode:
```bash
cd ~/se-toolkit-lab-7/bot
.venv/bin/uv run bot.py --test "/start"
```

Должно вывести приветственное сообщение и завершиться с кодом 0.

### 4. Проверьте exit code:
```bash
.venv/bin/uv run bot.py --test "/start"; echo "Exit code: $?"
```

Должно быть: `Exit code: 0`

---

## ✅ Acceptance Criteria для авточекера:

- [x] `bot/PLAN.md` существует (≥100 слов)
- [x] `bot/pyproject.toml` существует
- [ ] `bot/handlers/` директория с модулями (проверяется на VM)
- [ ] `--test "/start"` возвращает output с exit code 0
- [ ] `--test "/help"` возвращает output с exit code 0
- [ ] `--test "/foo"` не крашится (exit code 0)

---

## 🐛 Troubleshooting

**Ошибка: "No module named 'config'"**
```bash
cd ~/se-toolkit-lab-7/bot
.venv/bin/uv sync
```

**Ошибка: "BOT_TOKEN not set"**
```bash
# Создать .env.bot.secret
cd ~/se-toolkit-lab-7/bot
cp .env.bot.example .env.bot.secret
# Отредактировать и добавить BOT_TOKEN
nano .env.bot.secret
```

**Бэкенд недоступен:**
```bash
# Перезапустить сервисы
cd ~/se-toolkit-lab-7
docker compose --env-file .env.docker.secret down
docker compose --env-file .env.docker.secret up --build -d
```

---

После обновления на VM, авточекер автоматически проверит изменения через 1-2 минуты.
