# Improvement Proposals

Prioritized list of improvements verified against the code, with real `file:line` references. Categories: **bug**, **open decision**.

Guiding principle (`INFECTIONS.md:16`): *"Activate validator only when the substitute exists — blocking without offering an alternative only breaks code without teaching anything."*

---

## Open decisions — revisit "intentional"

Items currently classified as "no possible substitute" (`INFECTIONS.md:299-345`) but worth reassessing.

### ~~1. `open(path)` → POOP `Path` type inspired by `pathlib`?~~ — DONE

Decision: adopt a `pathlib`-based POOP `Path` wrapper.

Implemented:
- Added `poop/types/path.py` and namespace-only `poop/transformers/path.py`.
- Exposed `Path` in `DEFAULT_NAMESPACE` without adding a rewriting transformer.
- Kept `open()` banned and updated guidance to use `Path(...).read_text()/write_text()`.
- Added tests for `Path`, constructor idempotency, namespace bindings, and validator message.
- Updated docs (`INFECTIONS.md`, `README.md`, `CLAUDE.md`) to reflect the new substitute.
