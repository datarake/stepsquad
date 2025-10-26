FROM python:3.11-slim AS base
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN pip install --no-cache-dir uv
COPY pyproject.toml .
RUN uv sync --frozen || true
COPY . .
EXPOSE 8080
CMD ["sh","-c","uv run uvicorn main:app --host 0.0.0.0 --port $PORT"]
