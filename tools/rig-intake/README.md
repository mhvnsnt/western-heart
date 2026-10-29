# tools/rig-intake — auto-rig providers for the import pipeline

`tools/import_model.py` calls into this directory when an imported model has
no skinning. Providers are tried in order; the first one that is READY rigs
the mesh, otherwise the import keeps its existing fail message.

| Provider | File | Needs |
|---|---|---|
| UniRig (SIGGRAPH 2025) | `unirig_intake.py` | CUDA GPU 8GB+, `UNIRIG_ROOT` checkout — setup: `UNIRIG-SETUP.md` |

Contract for a provider module (so new rigs plug in the same way):

- `maybe_autorig(src, workdir) -> str | None` — returns the rigged GLB path
  on success, `None` when unavailable. **Must never raise.**
- `--check` CLI flag — prints readiness, exit 0/1.

Tests: `python3 -m pytest tools/rig-intake/tests/ -v`
