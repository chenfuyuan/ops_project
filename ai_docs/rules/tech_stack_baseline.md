# Tech Stack Baseline

This file defines the default technical baseline for code generation in this repository.

## Default stack
- Python 3.13
- `uv` with `pyproject.toml` and `uv.lock`
- FastAPI for HTTP APIs
- Pydantic v2 for request, response, config, and DTO validation
- SQLAlchemy 2.x for data access
- Alembic for schema migrations
- PostgreSQL for core persistent business data
- Redis for cache, lightweight coordination, and Celery backing services
- Celery for asynchronous background work
- S3-compatible object storage for files and large artifacts

## Default runtime shape
The default runtime topology is:
- API process
- Worker process

The API process handles synchronous request/response work and task submission.
The Worker process handles long-running, retryable, batch, or background jobs.

## Storage placement rules
- Core business data goes to PostgreSQL.
- Short-lived cache and lightweight coordination go to Redis.
- Files and large binary or text artifacts go to S3-compatible object storage.
- Structured audit-worthy metadata stays in PostgreSQL.
- Large payloads should be passed by reference, not embedded in queue messages.

## Coding implications
- Do not invent alternative stack choices unless the user asks.
- Do not introduce extra dependency-management systems alongside `uv`.
- Do not place implementation selection logic in business code; keep it in `bootstrap`.
- Do not put external SDK calls directly in `service.py`.

## Worker selection rule
Default to background workers for:
- long-running external calls
- file parsing or export/import jobs
- retryable tasks
- work that does not need to block the request lifecycle
- bursty work that benefits from queue-based smoothing

## Shared infrastructure baseline
System-level infrastructure should generally live in `shared/infra`.
Typical examples include:
- config loading
- database connection management
- logging and tracing wrappers
- HTTP client wrappers
- serialization helpers
- generic retry and timeout wrappers

## Bootstrap rule
`bootstrap` owns:
- runtime assembly
- implementation selection
- local vs remote vs mock wiring
- process startup composition
