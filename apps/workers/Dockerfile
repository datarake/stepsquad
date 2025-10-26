FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir uv
COPY pyproject.toml .
RUN uv sync --frozen || true
COPY . .
CMD ["uv", "run", "python", "worker.py"]
