# Modules

`app/modules/` is reserved for future business modules. The initial scaffold must not ship
sample domain behavior, so this directory contains only documentation and a reusable template.

## Boundary Rules

- Each module lives under `app/modules/<module_name>/`.
- Cross-module access must go through `api/contracts.py` and `api/facade.py`.
- Do not import another module's `application/`, `domain/`, or `infrastructure/` internals.
- Do not place business-specific helpers in `app/shared/`.

## Standard Module Layout

```text
app/modules/<module_name>/
├─ api/
│  ├─ contracts.py
│  └─ facade.py
├─ application/
├─ domain/
├─ infrastructure/
└─ module.py
```

Use [`_template/`](/Users/simon/code/person_up/ops_project/app/modules/_template) as the copy
source when creating a new module.
