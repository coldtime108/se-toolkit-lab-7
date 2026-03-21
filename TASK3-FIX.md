# 🔄 СРОЧНО: Обновление кода на VM для Task 3

## Проблема
Авточекер показывает 0% за Task 3, потому что код на VM не обновлён.

## Решение

### 1. Подключиться к VM:
```bash
ssh coldtime108@10.93.26.30
# Пароль: innopolisTimurA!
```

### 2. Обновить код:
```bash
cd ~/se-toolkit-lab-7
git pull origin task-1-2-bot-scaffold
```

### 3. Перезапустить Qwen API (если ошибка HTTP 401):
```bash
cd ~/qwen-code-oai-proxy
docker compose restart
```

### 4. Проверить, что бэкенд работает:
```bash
curl http://localhost:42002/items/ -H "Authorization: Bearer mysecretkey123" | head -c 100
```

### 5. Протестировать бота:
```bash
cd ~/se-toolkit-lab-7/bot
.venv/bin/uv run bot.py --test "what labs are available"
```

**Ожидаемый вывод:**
```
📋 Доступные лабораторные работы:

• Lab 1: Lab 01 – Products, Architecture & Roles
• Lab 2: Lab 02 — Run, Fix, and Deploy a Backend Service
...
```

### 6. Протестировать другие запросы:
```bash
.venv/bin/uv run bot.py --test "show me scores for lab 4"
.venv/bin/uv run bot.py --test "how many students are enrolled"
```

## Что исправлено:

✅ **9 Tool Schemas** — LLM вызывает инструменты, а не regex
✅ **Inline Keyboard Buttons** — кнопки для быстрых действий
✅ **LLM Tool Calling** — бот использует function calling API
✅ **Backend API Calls** — реальные вызовы API для всех инструментов

## Инструменты (9 шт):

1. `get_health` — проверка статуса бэкенда
2. `list_labs` — список лабораторных
3. `get_scores` — оценки для лабы
4. `get_analytics` — аналитика (pass-rates, score-distribution)
5. `get_tasks` — задачи для лабы
6. `get_learners` — список студентов
7. `get_submissions` — статистика отправок
8. `get_interactions` — взаимодействия
9. `sync_data` — синхронизация данных

## Проверка перед авточекером:

Убедитесь, что все тесты проходят:
```bash
cd ~/se-toolkit-lab-7/bot

# Команды
.venv/bin/uv run bot.py --test "/start"
.venv/bin/uv run bot.py --test "/help"
.venv/bin/uv run bot.py --test "/health"

# Natural language
.venv/bin/uv run bot.py --test "what labs are available"
.venv/bin/uv run bot.py --test "show me scores for lab 4"
```

После обновления авточекер должен показать лучший результат!
