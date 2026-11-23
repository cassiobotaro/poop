# 66. Decisions live in `doc/adr/`, replacing `INFECTIONS.md`

Date: 2026-11-23

## Status

Accepted

## Context

`INFECTIONS.md` was a single 1486-line file doing three jobs. It recorded why each design decision was made, it was the reader's catalogue of what is banned and what to write instead, and it was the API reference for the types.

The reasoning was the expensive part to keep. Every change that touched a validator, transformer or type had to rewrite a paragraph in place, so a decision's reasoning was edited, extended and occasionally contradicted over time, and nothing recorded what it had said before. Extracting it into this log found passages the code had already moved past: `Range.slice` said to answer a `List`, a bare method attribute said to stay a native leak, classes said not to be objects of their own.

The other record of decisions, the `design.md` of each archived OpenSpec change, is immutable but scattered, and cannot be found by topic. The `2026-10-14-backlog-to-openspec` change, in its decision 4, kept `INFECTIONS.md` as the record of *why* and rejected moving that reasoning out, on the ground that it would end up scattered across archived `design.md` files.

## Decision

We will record each decision as an ADR in `doc/adr/`, in the format of ADR 1: one decision per file, immutable once accepted, and a changed mind recorded as a new ADR that supersedes the old one. ADRs 2 to 65 are the decisions already made, extracted from `INFECTIONS.md` and the archived `design.md` files, numbered and dated in the order they were made.

The reference moves to `MIGRATION.md`: *Banned constructs* (one row per ban, with its substitute), *Type reference* and *Rewrites*, as tables without rationale. The specs under `openspec/specs/` keep recording observable behaviour.

OpenSpec uses the log through a rule in `openspec/config.yaml`, not a forked schema: a decision with a real alternative is written as an ADR in the same commit as the code, and the change's `design.md` names the ADR instead of restating it.

`INFECTIONS.md` is deleted. This reverses decision 4 of `2026-10-14-backlog-to-openspec`: the log is one directory indexed by number and title, not reasoning scattered across archived changes.

## Consequences

- A decision's reasoning is no longer rewritten in place; what a superseded decision said stays readable in its own file.
- `MIGRATION.md`'s tables still need a row when a validator or type is added. They are rows, not paragraphs.
- Code, tests and documents cite an ADR by its path, which does not move once accepted.
- No test reads the log or `MIGRATION.md`, so a stale reference to either passes silently.
- The archived changes keep their mentions of `INFECTIONS.md` as history.
