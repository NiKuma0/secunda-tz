FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0

WORKDIR /app

COPY uv.lock pyproject.toml /app/

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

FROM python:3.13-slim-bookworm

ENV PYTHONPATH="/app:/app" \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder --chown=app:app /app /app
COPY ./src ./migrations alembic.ini /app/

COPY --chown=app:app . /app

CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
