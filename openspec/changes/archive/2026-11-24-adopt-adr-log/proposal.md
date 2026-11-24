# Proposal

## Why

`INFECTIONS.md` is a single 1486-line file that does three jobs: it records
why each design decision was made, it is the user's catalogue of what is
banned and what to write instead, and it is the API reference for the types.
The *why* is the expensive part to keep: every change that touches a
validator, transformer or type is required to rewrite a paragraph in place,
so a decision's reasoning is edited, extended and occasionally contradicted
over time, and nothing records what it said before. The other record of
decisions, the 23 archived `design.md` files, is immutable but scattered, and
is not discoverable by topic.

An Architecture Decision Record log (Michael Nygard's format, file-compatible
with adr-tools) fixes both: one file per decision, immutable once accepted, a
changed mind is a new record that supersedes the old one. Moving the
catalogue and the reference tables to `MIGRATION.md`, which is already the
reader's quick reference, lets `INFECTIONS.md` be deleted rather than kept as
a fourth copy.

This reverses decision 4 of the archived `backlog-to-openspec` change
("`INFECTIONS.md` keeps the *why*"), which rejected scattering the reasoning
across archived `design.md` files. An ADR log is not that scattering: it is
one directory, one decision per file, indexed by number and title.

## What Changes

- **New `doc/adr/` log and `.adr-dir`.** `0001-record-architecture-decisions.md`
  (the adr-tools seed) opens the log, then one ADR per real decision (a choice with a genuine
  alternative that someone would need the reasoning to avoid undoing),
  extracted from `INFECTIONS.md` (*Principles*, *Explicitly allowed*, and the
  decisions inside the validator, type and transformer sections) and from the
  `Decisions` sections of the archived `design.md` files. About 65
  records after merging near-duplicates; the last records this change. Retroactive records carry the date the decision was originally made
  and status `Accepted`.
- **`MIGRATION.md` absorbs the reference.** A *Banned constructs* section with
  one row per ban (construct → substitute, no rationale), and a *Type
  reference* section with the API tables (Smalltalk message → POOP method,
  builtin-mirroring signatures, collection methods, `Range`, `Slice`).
- **OpenSpec uses the log.** `openspec/config.yaml` gains a `rules.design`
  rule: a decision with a real alternative becomes an ADR, and `design.md`
  links to it instead of restating it. Its `context` points at `doc/adr/`
  instead of `INFECTIONS.md`, and the `rules.specs` naming rule stops citing
  `INFECTIONS.md` sections.
- **Contributor docs follow.** `AGENTS.md`, `CONTRIBUTING.md` (the catalogue
  pointer, Language, the four "Add an entry to `INFECTIONS.md`" steps,
  *Closing a change*), `.github/copilot-instructions.md`,
  `.claude/skills/backlog/SKILL.md`, `README.md` ("Where to next") and
  `MIGRATION.md`'s own two links point at `doc/adr/` or the new sections.
- **Citations in code follow.** The comments and docstrings in `poop/`,
  `tests/` and `pyproject.toml` that justify themselves by quoting
  `INFECTIONS.md` cite the ADR instead.
- **BREAKING (docs): `INFECTIONS.md` is deleted.**

No behaviour of the language changes.

## Capabilities

### New Capabilities
<!-- none -->

### Modified Capabilities
<!-- none: documentation, workflow configuration and comments; no
     spec-level behaviour. `.openspec.yaml` declares `skip_specs: true`. -->

## Impact

- New: `doc/adr/*.md`, `.adr-dir`.
- Deleted: `INFECTIONS.md`.
- Edited: `MIGRATION.md`, `README.md`, `AGENTS.md`, `CONTRIBUTING.md`,
  `openspec/config.yaml`, `.github/copilot-instructions.md`,
  `.claude/skills/backlog/SKILL.md`, `pyproject.toml` (one comment), and
  comments or docstrings in about 20 files under `poop/` and `tests/`.
- `tests/test_doc_counts.py` reads `README.md` and `examples/README.md` only;
  no test reads `INFECTIONS.md`, so a stale reference would pass silently. The
  closing task is a `git grep` that must come back empty.
- Every later `/openspec-propose` inherits the ADR rule through
  `openspec instructions design`.

## Out of scope

- **Rewriting archived changes.** `openspec/changes/archive/` is history; its
  mentions of `INFECTIONS.md` stay, as `backlog-to-openspec` left its own
  mentions of `proposals.md`.
- **A custom OpenSpec schema with an `adr` artifact.** A rule in
  `config.yaml` is enough and keeps the packaged `spec-driven` schema, which
  the `openspec schema` commands still call experimental.
- **Correcting `.github/copilot-instructions.md`.** It describes validator
  factories and a raising `ValidationError` that no longer match
  `CONTRIBUTING.md`; only its `INFECTIONS.md` line changes here. Bringing it
  up to date is its own change.
- **One ADR per ban.** Bans that only apply a principle (`no_len`, `no_abs`,
  …) are covered by that principle's ADR and a row in `MIGRATION.md`.
- **Installing adr-tools.** It is not on the machine; the files follow its
  format so the tool can be adopted later without renaming anything.
