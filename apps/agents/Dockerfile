FROM python:3.11-slim
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Install system dependencies if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies directly (more reliable than uv for Cloud Run)
COPY pyproject.toml .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    fastapi>=0.115.0 \
    uvicorn[standard]>=0.30.0 \
    google-cloud-firestore>=2.16.0 \
    google-cloud-bigquery>=3.25.0 \
    google-generativeai>=0.8.0 \
    requests>=2.32.3 \
    python-dotenv>=1.0.0

# Note: google-adk may not be available on PyPI
# The code gracefully falls back if ADK is not available

COPY . .
EXPOSE 8080

# Use PORT environment variable from Cloud Run (defaults to 8080)
CMD ["sh", "-c", "python -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]
