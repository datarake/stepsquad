FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir uv
COPY pyproject.toml .
RUN uv sync && uv pip install fastapi uvicorn
COPY . .
EXPOSE 8080
CMD ["sh","-c","uv run uvicorn worker:app --host 0.0.0.0 --port $PORT"]
