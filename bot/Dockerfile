FROM python:3.12-slim

WORKDIR /app

# Устанавливаем зависимости (aiogram, httpx, python-dotenv)
RUN pip install --upgrade pip && \
    pip install aiogram httpx python-dotenv

# Копируем код бота
COPY bot/ /app/

CMD ["python", "bot.py"]
