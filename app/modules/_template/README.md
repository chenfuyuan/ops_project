# Module Template

Copy this directory to `app/modules/<module_name>/` when adding a real business module.

- Keep `api/contracts.py` and `api/facade.py` as the only public cross-module surface.
- Add internal implementation files inside `application/`, `domain/`, and
  `infrastructure/`.
- Update `module.py` with the module's registration metadata.
