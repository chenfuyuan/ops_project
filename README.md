# OPS Project Scaffold

This repository is a boundary-first FastAPI scaffold for a modular monolith. It provides a
minimal runnable application, a health endpoint, shared foundation placeholders, and a reusable
module template without introducing any real business module yet.

## Layout

```text
app/
├─ bootstrap/          # Application assembly and future module registration
├─ interfaces/http/    # HTTP routes, schemas, and middleware
├─ shared/             # Stable, business-free shared capabilities
└─ modules/            # Module docs and template only
tests/
├─ unit/
├─ integration/
└─ e2e/
```

## Local Development

1. Install dependencies with `uv sync`.
2. Copy `.env.example` to `.env` if you want to customize the local service name or port.
3. Start the app with `make dev`.
4. Check the service with `curl http://127.0.0.1:8000/health`.

## Quality Checks

- `make test`
- `make lint`

## Module Rules

- New modules live under `app/modules/<module_name>/`.
- Other modules may depend only on `api/contracts.py` and `api/facade.py`.
- `app/shared/` must stay free of business-specific logic.
