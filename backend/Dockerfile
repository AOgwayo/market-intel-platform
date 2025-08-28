# Simple production-ish image; can be refined with multi-stage build if needed.
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

COPY backend/pyproject.toml ./pyproject.toml

RUN pip install --upgrade pip && pip install -e .[dev]

COPY backend/src ./src
COPY backend/tests ./tests

EXPOSE 8000

CMD ["uvicorn", "market_intel.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
