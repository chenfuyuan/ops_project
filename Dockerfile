FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY app ./app
COPY tests ./tests
# Runtime image includes migration files so containers can run Alembic against the configured database.
COPY alembic ./alembic
COPY alembic.ini ./alembic.ini
COPY CLAUDE.md ./CLAUDE.md

RUN uv sync --frozen --no-dev

EXPOSE 8000

CMD ["/app/.venv/bin/uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]
