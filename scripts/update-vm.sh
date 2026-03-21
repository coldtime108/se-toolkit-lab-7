# Инструкция по обновлению кода на VM для авточекера

## Быстрое обновление (после каждого коммита)

Подключитесь к VM:
```bash
ssh coldtime108@10.93.26.30
# Пароль: innopolisTimurA!
```

Выполните обновление:
```bash
cd ~/se-toolkit-lab-7
git pull
cd bot
.venv/bin/uv sync
```

## Проверка test mode

Протестируйте команды:
```bash
cd ~/se-toolkit-lab-7/bot
.venv/bin/uv run bot.py --test "/start"
.venv/bin/uv run bot.py --test "/help"
.venv/bin/uv run bot.py --test "/health"
.venv/bin/uv run bot.py --test "/labs"
.venv/bin/uv run bot.py --test "/scores lab-01"
.venv/bin/uv run bot.py --test "/foo"  # Должен вернуть helpful message, не крашиться
```

## Ожидаемый вывод

### `/start`:
```
👋 Добро пожаловать в LMS Bot!

Я ваш помощник для взаимодействия с системой управления обучением.
Используйте /help, чтобы увидеть список доступных команд.
```

### `/help`:
```
📚 Доступные команды:

/start - Приветственное сообщение
/help - Показать эту справку
/health - Проверить статус бэкенда
/labs - Показать доступные лабораторные работы
/scores <lab> - Показать результаты по лабораторной

Вы также можете писать обычные сообщения, и я постараюсь понять, что вам нужно!
```

### `/health`:
```
✅ Бэкенд работает нормально
{...данные...}
```
ИЛИ (если бэкенд недоступен):
```
❌ Бэкенд недоступен
Backend is not reachable
```

### `/foo` (неизвестная команда):
```
⚠️ Неизвестная команда: /foo

Используйте /help для списка команд.
```

## Проверка exit code

```bash
.venv/bin/uv run bot.py --test "/start"
echo $?  # Должен вывести 0
```

## Если тесты не проходят

1. Проверьте, что `.env.bot.secret` существует:
   ```bash
   ls -la ~/se-toolkit-lab-7/bot/.env.bot.secret
   ```

2. Если файла нет, создайте:
   ```bash
   cd ~/se-toolkit-lab-7/bot
   cp .env.bot.example .env.bot.secret
   nano .env.bot.secret
   ```
   
   Заполните:
   ```text
   BOT_TOKEN=8456337233:AAGvvClW7u6EjGaTIUysSKiQZHYZVxGfhh4
   LMS_API_URL=http://localhost:42002
   LMS_API_KEY=mysecretkey123
   LLM_API_KEY=
   LLM_API_BASE_URL=
   LLM_API_MODEL=coder-model
   ```

3. Проверьте, работает ли бэкенд:
   ```bash
   curl http://localhost:42002/health -H "Authorization: Bearer mysecretkey123"
   ```

4. Перезапустите Docker сервисы если нужно:
   ```bash
   cd ~/se-toolkit-lab-7
   docker compose --env-file .env.docker.secret down
   docker compose --env-file .env.docker.secret up --build -d
   ```
