FROM python:3.12-slim
WORKDIR /app
RUN pip install uv
COPY bot/ .
RUN uv sync --no-dev
CMD ["uv", "run", "bot.py"]
