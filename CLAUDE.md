# CLAUDE.md

This repository keeps long-lived AI coding guidance in `ai_docs/`.

## Default reading order
When working in this repository, read these files first before making non-trivial code changes:

1. `ai_docs/00_readme.md`
2. `ai_docs/rules/architecture_rules.md`
3. `ai_docs/rules/naming_rules.md`
4. `ai_docs/rules/tech_stack_baseline.md`
5. `ai_docs/rules/review_checklist.md`
6. Relevant files under `ai_docs/examples/` when generating or refactoring business-layer code

## How to use `ai_docs/`
- Treat `ai_docs/rules/` as the default long-lived coding rules.
- Treat `ai_docs/examples/` as the preferred implementation patterns to imitate.
- Prefer these files over older duplicated guidance when both exist.
- Keep generated code aligned with these rules unless the user explicitly overrides them.

## OpenSpec boundary
- Do not duplicate `openspec/` artifacts into `ai_docs/`.
- When an OpenSpec workflow is active, rely on `openspec/` artifacts as task-specific context.
- Use `ai_docs/` for stable AI-facing guidance that applies across many tasks.

## Implementation expectations
- Follow the architecture boundaries under `app/business`, `app/capabilities`, `app/interfaces`, `app/shared`, and `app/bootstrap`.
- Keep business core files free of SDK, HTTP client, and ORM implementation details.
- Use business-defined `ports` plus adapter implementations in `infrastructure/`.
- Keep runtime wiring and implementation selection in `bootstrap`.
- Use `uv` as the dependency and command runner baseline.

## Updating guidance
When repository conventions change, update the corresponding files in `ai_docs/` so future AI work stays aligned.
