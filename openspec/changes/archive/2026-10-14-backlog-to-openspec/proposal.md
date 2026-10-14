# Proposal

## Why

The project now runs its work through OpenSpec — three changes planned,
applied and archived, four main specs created by sync — while `proposals.md`
still claims to be the backlog and every contributor document points at it.
The file is empty, so the two processes have not yet contradicted each other,
but the next idea has two places to land and the docs describe only the old
one. Retiring `proposals.md` now, while there is nothing to migrate, makes the
OpenSpec flow the one the documents, the agent guide and the `backlog` skill
describe.

## What Changes

- **`proposals.md` is deleted.** The backlog is the set of active changes under
  `openspec/changes/`; a closed item is its archive under
  `openspec/changes/archive/`. The numbered-item convention (continue from the
  highest, restart at 1 when empty) and the `docs: close proposal N` commit go
  with it: a change has a name, and its archive commit is the closing record.
- **`CONTRIBUTING.md`** describes the new flow where it described the old one:
  the "Open backlog" pointer, "Confirm scope before multi-part plans", the
  Language rule, the whole "Closing a proposal" section (becomes "Closing a
  change"), and the PR checklist line. It also states the granularity rule: one
  change per theme, one task per finding, so an audit with twenty findings is
  one change with twenty checkboxes, as the "close proposals 1–11" commit
  already did in practice.
- **`AGENTS.md`** replaces the `proposals.md` bullet with the OpenSpec one:
  work starts as a change, artifacts are English, implemented changes are
  archived, never left active.
- **`README.md`** points "open design backlog" at `openspec/changes/`.
- **`INFECTIONS.md`** changes one sentence only: the principle "Activate
  validator only when the substitute exists" says unactivated validators live
  in `proposals.md`; they live in an open change now. The catalogue itself is
  unchanged and keeps its role as the record of *why*; `openspec/specs/`
  records *what the system does*, growing only by delta.
- **`openspec/config.yaml`** gains the project context an agent cannot infer
  (where the design principles live, the English rule, the same-commit docs
  rule, the one-change-per-theme rule) and a `specs` naming rule so a
  capability and its INFECTIONS.md section find each other: `<builtin>-type`
  for a wrapper, `<name>-validator`, `<name>-transformer`, a plain noun for a
  cross-cutting behavior (`block-arity`).
- **`.claude/skills/backlog/SKILL.md`** is rewritten from "read
  `proposals.md`" to the OpenSpec loop: `openspec list`, pick with the user,
  `/opsx:apply`, `/opsx:archive`, keeping the two rules it carried (discuss
  trade-offs first, confirm scope).

Nothing in `poop/`, `tests/` or `examples/` changes.

## Capabilities

### New Capabilities
<!-- none -->

### Modified Capabilities
<!-- none: documentation, a skill and workflow configuration; no spec-level
     behavior. `.openspec.yaml` declares `skip_specs: true`. -->

## Impact

- Deleted: `proposals.md`.
- Edited: `CONTRIBUTING.md`, `AGENTS.md`, `README.md`, `INFECTIONS.md` (one
  sentence), `openspec/config.yaml`, `.claude/skills/backlog/SKILL.md`.
- `tests/test_doc_counts.py` reads validator and example counts from
  `README.md`; the sentence it matches is untouched.
- Every later `/opsx:propose` inherits the context and the naming rule.
