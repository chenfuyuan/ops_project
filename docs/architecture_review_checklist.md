# Architecture Review Checklist

- shared/ changes are high-sensitivity and must not introduce business semantics.
- capabilities/ changes are high-sensitivity and must stay free of business dependencies.
- workflow/state.py is a high-sensitivity boundary and shared state must stay minimal.
- business/**/ports.py changes must preserve boundary ownership and naming clarity.
- business/**/infrastructure/* changes must remain adapters, not business logic.
