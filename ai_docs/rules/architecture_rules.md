# Architecture Rules

This file condenses the repository's architecture rules into an AI-oriented reference.

## Top-level boundaries
Code under `app/` must fit one of these areas:

- `business/`: the only top-level area allowed to carry business semantics.
- `capabilities/`: cross-business reusable capabilities with neutral language and no business semantics.
- `interfaces/`: external protocol entrypoints such as HTTP.
- `shared/`: stable, low-business-semantic kernel and infrastructure building blocks.
- `bootstrap/`: runtime wiring, dependency assembly, and implementation selection.

When choosing a location, prefer semantic ownership over technical type.

## What each area may do
### `business/`
- Own workflows, nodes, business entities, rules, use-case orchestration, and business-defined ports.
- Use `ports + infrastructure` to reach capabilities, external systems, and storage.
- Keep business language in `service.py`, `entities.py`, `rules.py`, and `ports.py`.

Do not:
- Put vendor SDKs, ORM implementations, or HTTP clients directly in business core files.
- Let `service.py` skip `ports` and call concrete adapters directly.

### `capabilities/`
- Host reusable, business-neutral capabilities.
- Standardize provider differences and expose stable contracts.

Do not:
- Depend on `business/`.
- Hide business rules behind a "shared capability" label.
- Leak provider-specific fields into business-facing contracts.

### `interfaces/`
- Parse protocol input, perform boundary concerns, and call business entrypoints.

Do not:
- Reach into `business/**/infrastructure/*`.
- Implement business rules or external dependency adaptation here.

### `shared/`
- Host low-semantic, cross-context kernel types and infrastructure utilities.

Do not:
- Store business DTOs, business enums, business rules, or "misc" leftovers.
- Turn `shared/` into a dumping ground.

### `bootstrap/`
- Assemble dependencies and choose implementations.
- Handle local vs remote vs mock vs provider selection.

Do not:
- Hold business logic.
- Be depended on by other layers.

## Standard business structure
A business domain should generally follow this shape:

```text
business/<domain>/
├─ workflow/
├─ domain_services/
└─ nodes/
   └─ <unit>/
      ├─ node.py
      ├─ service.py
      ├─ dto.py
      ├─ entities.py
      ├─ rules.py
      ├─ ports.py
      └─ infrastructure/
```

Not every file must always exist, but responsibilities must stay consistent.

## Workflow and node responsibilities
### `workflow/`
Responsible for topology, registry, edges, and state flow.

Do not:
- Implement business rules.
- Call external SDKs or storage implementations directly.
- Grow `state.py` into an unbounded global context.

### `node.py`
- Adapt workflow state into node input.
- Call `service.py`.
- Map results back into workflow state.

### `service.py`
- Orchestrate node-level business use cases.
- Combine entities, rules, and port calls.

Do not:
- Call SDKs, HTTP clients, RPC clients, or ORM implementations directly.
- Own timeout, retry, transport, or provider-switching concerns.

### `ports.py`
- Define interfaces in business language.
- Express what the business needs, not how technology works.

### `infrastructure/`
- Implement adapters, translation, protocol mapping, and persistence integration.

Do not:
- Hold business decisions.

## Required call chain
Preferred call chain:

```text
interfaces -> business workflow/node -> service.py -> ports.py -> infrastructure/* -> capabilities/external systems/storage
```

Business code must not bypass `ports`.
Interfaces must not bypass business boundaries.
Workflow code must not perform direct infrastructure calls.

## Allowed dependency direction
```text
interfaces  -> business
business    -> shared
business core -> ports
business infrastructure -> capabilities / external systems / storage
capabilities -> shared
bootstrap   -> all (composition only)
```

## Forbidden dependency direction
- `capabilities -> business`
- `shared -> business`
- `interfaces -> business/**/infrastructure/*`
- `service.py -> concrete adapter`
- `workflow -> external SDK / remote client / storage implementation`
- business core files directly depending on vendor SDKs, HTTP clients, or ORM implementations

## High-sensitivity areas
Changes in these areas need stricter review:
- `shared/`
- `capabilities/`
- `workflow/state.py`
- `business/**/ports.py`
- `business/**/infrastructure/*`

## Quick placement guide
- Carries business meaning: `business/`
- Reusable neutral capability: `capabilities/`
- Protocol entrypoint: `interfaces/`
- Stable low-semantic shared building block: `shared/`
- Wiring and implementation choice: `bootstrap/`
