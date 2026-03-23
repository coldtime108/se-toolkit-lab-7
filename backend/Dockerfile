FROM python:3.12-slim

WORKDIR /app

# Установим ВСЕ зависимости
RUN pip install --no-cache-dir \
    fastapi uvicorn pydantic pydantic-settings python-dotenv \
    httpx psycopg2-binary sqlalchemy sqlmodel asyncpg

# Копируем код
COPY backend/app /app/app

ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Запускаем
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
