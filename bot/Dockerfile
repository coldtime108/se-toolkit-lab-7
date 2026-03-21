FROM python:3.12-slim

WORKDIR /app

# Копируем только файлы зависимостей
COPY bot/pyproject.toml bot/uv.lock /app/

# Устанавливаем зависимости через pip (без uv)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir aiogram httpx python-dotenv

# Копируем весь код бота
COPY bot/ /app/

CMD ["python", "bot.py"]
