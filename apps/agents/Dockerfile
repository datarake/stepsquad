FROM python:3.11-slim
WORKDIR /app
ENV PORT=8004
RUN pip install --no-cache-dir uv
COPY pyproject.toml .
RUN uv sync --frozen || true
COPY . .
EXPOSE 8004
CMD ["uv","run","uvicorn","main:app","--host","0.0.0.0","--port","8004"]
