# Review Checklist

Use this checklist before considering generated code complete.

## Boundary checks
- Is the new code placed in the correct top-level area?
- Does any business-core file directly depend on SDKs, HTTP clients, or ORM implementations?
- Does `service.py` depend only on business-defined ports?
- Does `interfaces/` avoid reaching into `business/**/infrastructure/*`?
- Does `capabilities/` stay free of business dependencies?
- Does `shared/` stay free of business semantics?
- Does `workflow/` stay free of external implementation details?

## Naming checks
- Are directories and modules named by domain or responsibility?
- Are there any vague names like `misc`, `utils`, `common2`, or `temp`?
- Are ports named by business capability rather than vendor or transport?
- Are adapters named by responsibility and provider or transport role?

## Workflow and state checks
- Is `workflow/state.py` still minimal and clearly bounded?
- Are node inputs and outputs explicit rather than passing around a growing global state object?
- Does `node.py` remain an adapter instead of holding business logic?

## Infrastructure checks
- Does `infrastructure/` stay as an adapter layer rather than a business-logic layer?
- Are timeout, retry, auth, serialization, and provider-specific concerns kept out of business core files?
- Are implementation switches kept in `bootstrap` instead of scattered across business code?

## Testing checks
- Are business rules and services covered by unit tests through fakes, stubs, or mocks at the port boundary?
- Are infrastructure and interfaces covered by integration tests where mapping and boundary behavior matter?
- Are architectural constraints enforceable through architecture tests or equivalent checks?

## High-sensitivity review reminder
Apply extra scrutiny to changes in:
- `shared/`
- `capabilities/`
- `workflow/state.py`
- `business/**/ports.py`
- `business/**/infrastructure/*`
