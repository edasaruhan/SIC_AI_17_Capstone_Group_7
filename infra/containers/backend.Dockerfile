FROM python:3.12.11-slim-bookworm AS builder

ARG UV_VERSION=0.11.26
WORKDIR /app
RUN pip install --no-cache-dir "uv==${UV_VERSION}"
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

FROM python:3.12.11-slim-bookworm AS runtime
ENV PATH="/app/.venv/bin:${PATH}" \
    PYTHONPATH=/app/backend \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app
RUN groupadd --system growthpilot && useradd --system --gid growthpilot growthpilot
COPY --from=builder /app/.venv /app/.venv
COPY backend /app/backend
COPY alembic.ini /app/alembic.ini
COPY artifacts/ml/final_candidate.json /app/artifacts/ml/final_candidate.json
USER growthpilot
EXPOSE 8000
CMD ["uvicorn", "app.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "*"]
