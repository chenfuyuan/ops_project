.PHONY: dev test lint health

dev:
	uv run python scripts/dev_start.py

test:
	uv run pytest

lint:
	uv run ruff check .

health:
	curl -fsS http://127.0.0.1:8000/health
