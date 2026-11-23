# Design

## Context

Facts the approach rests on:

- `INFECTIONS.md` is 1486 lines, created 2026-04-19 (`0c1d5142`). It holds 35
  *Principles* bullets (about 5k words), 393 table rows, and long rationale
  paragraphs under the type and transformer sections (`Str` alone about 2.6k
  words, `Object` 2k, `PoopExcMeta` 1.5k). Its tables are of three kinds: ban
  tables (AST node or builtin → reason and substitute), API reference
  (Smalltalk message → POOP method → behaviour, builtin-mirroring signatures,
  collection methods, `Range`, `Slice`), and rewrite tables (literal → wrapper).
- Nothing in `poop/` or `tests/` reads `INFECTIONS.md`; about 20 comments and
  docstrings cite it as their justification, and `pyproject.toml:203` does too.
  `tests/test_doc_counts.py` reads `README.md` and `examples/README.md` only.
- The 23 archived `design.md` files number their decisions in two formats
  (`**N. …**` and `### …`). About half of those decisions are implementation
  detail (lint ignores, type-checker casts, dependency floors).
- `openspec/config.yaml` points its `context` at `INFECTIONS.md` *Principles*
  and its `rules.specs` naming rule at `INFECTIONS.md` section headings.
- adr-tools is not installed. The `adr` skill in this environment writes the
  same file format and enforces numbering and supersession.

## Goals / Non-Goals

**Goals:**
- Each decision is one immutable file, findable by number and title, with the
  reasoning that was in `INFECTIONS.md` and nothing invented.
- A reader still has one place to look up what is banned and what to write
  instead, and what each type answers.
- Every new OpenSpec change that makes a decision produces an ADR, prompted by
  `openspec instructions design`.
- No document, comment or skill points at `INFECTIONS.md` afterwards.

**Non-Goals:**
- Rewording decisions. Extraction moves text; it does not re-argue it.
- Converting rationale into specs. Specs hold behaviour; the existing 39
  capabilities stay as they are.
- Touching `openspec/changes/archive/`.

## Decisions

**1. Nygard format, file-compatible with adr-tools, in `doc/adr/`.** Files are
`NNNN-slug.md`, the slug derived from the title; each has `# N. Title`,
`Date: YYYY-MM-DD`, and the sections `## Status`, `## Context`,
`## Decision`, `## Consequences`, spelled in English exactly, since adr-tools
and Structurizr's `!adrs` importer parse those literals. `.adr-dir` at the
root holds `doc/adr`. The records are written in English like every other
repository document.
*Alternative*: MADR, which has an explicit *Considered options* section.
Rejected: the user chose the adr-tools layout, and Nygard's *Context* already
carries the rejected alternative in the paragraphs being extracted.

**2. One ADR per decision, a decision being a choice with a real
alternative.** A section that holds several decisions (`Str` holds the
template surface, the f-string ban and the text mirrors) yields several ADRs.
A ban that only applies a principle (`no_len`, `no_abs`, `no_hash`, …) yields
no ADR of its own; the principle's ADR lists it. Measurements, before/after
examples and the quoted refusal sentences go into *Context* and *Decision*
verbatim, because the wording is the behaviour.
*Alternative*: one ADR per theme (12-15 larger records). Rejected by the
user: a theme record would be edited as decisions inside it changed, which is
the maintenance cost this change removes.

**3. Retroactive records are numbered in the order the decisions were made,
and dated when they were made.** `0001` is adr-tools' seed, *Record
architecture decisions*, verbatim and dated the day it is committed; the
record of why POOP replaces `INFECTIONS.md` is the last one, dated the day
it lands. The retroactive ADRs follow from `0002` in date order (ties broken by theme, then by position in the source). The date
of a decision extracted from an archived change is that archive's date
prefix. The date of a decision extracted from `INFECTIONS.md` is the date of
the commit that introduced its paragraph:
`git log -S '<distinctive phrase>' --format=%ad --date=short -- INFECTIONS.md | tail -1`.
All records get status `Accepted`. Because numbering needs every date first,
the inventory (task 1) is complete before any ADR is written.
*Alternative*: number by theme. Rejected: a log whose numbers do not follow
time reads as if `0040` were decided before `0003`, and every later ADR is
appended by date anyway.

**4. A decision that was already reversed is one ADR, not a fabricated
supersession.** Several paragraphs narrate an earlier state ("Before,
`None.class_()()` printed `None`…"). There is no earlier record to
supersede, so the earlier state goes into the ADR's *Context*. Supersession
starts with the first change made after this one.

**5. `MIGRATION.md` gets two sections, without rationale.** *Banned
constructs*: one row per construct, `Python | POOP substitute | validator`,
built from the ban tables; where `INFECTIONS.md` gives no substitute
(definitive bans) the cell says so and links the ADR. *Type reference*: the
API tables moved as they are, under one heading per type. The existing
*Quick reference* table and recipes stay; the intro's "full reference … see
`INFECTIONS.md`" sentence and the § link at line 185 point at the new
section and the ADR.
*Alternative*: a separate `doc/reference.md`. Rejected by the user.

**6. The OpenSpec rule lives in `config.yaml`, not in a forked schema.**
`rules.design` gains: a decision with a real alternative is written as an ADR
in `doc/adr/` (next number, status `Accepted`, `Superseded by` on the record
it replaces) in the same commit as the code; `design.md` names the ADR and
keeps only what is specific to the change. `context` replaces the
`INFECTIONS.md` pointer with "decisions live in `doc/adr/`; bans and the type
reference in `MIGRATION.md`; specs hold behaviour". `rules.specs` names
capabilities after the type, validator or transformer itself (`float-type`
for `float`, `no-len-validator` for `no_len`), with the same examples and no
`INFECTIONS.md` heading.
*Alternative*: `openspec schema fork spec-driven` with an `adr` artifact.
Rejected: a project-owned copy of an experimental schema that drifts from the
packaged one on every OpenSpec release.

**7. Code cites the ADR by path.** A comment that read "the argument
`INFECTIONS.md` makes for `super`" reads "the argument `doc/adr/NNNN-….md`
makes". A path is greppable and clickable, and an accepted ADR does not move.
This is consistent with `CONTRIBUTING.md`'s "cite commits, not change names":
an ADR is a document, not a change.

**8. Order: add, repoint, delete.** ADRs and the `MIGRATION.md` sections land
first, while `INFECTIONS.md` is still the source each is checked against.
Then config, docs, skill and code citations are repointed. `INFECTIONS.md` is
deleted last, in a commit whose gate is an empty
`git grep -n INFECTIONS -- ':!openspec/changes/archive' ':!openspec/changes/adopt-adr-log' ':!doc/adr'`.
`doc/adr/0001` is excluded because its *Context* names the file it replaces.

## Risks / Trade-offs

- [Extraction drops a decision nobody listed] → task 1's inventory is checked
  against every `INFECTIONS.md` section heading, and the deletion task diffs
  the section list against the inventory plus `MIGRATION.md` before removing
  the file.
- [Between the first ADR commit and the deletion, two sources exist] → the
  change is applied in one sitting; `INFECTIONS.md` is not edited during it,
  and any other change in flight waits.
- [`MIGRATION.md` reference tables still need upkeep] → accepted: they are
  rows, not paragraphs, and `CONTRIBUTING.md`'s steps name exactly which
  table a new validator or type adds a row to.
- [About 70 commits] → one concern per commit, as `AGENTS.md` asks; each ADR
  is independent and reviewable alone.
- [The `git log -S` date is when a paragraph reached `INFECTIONS.md`, not when
  the code changed] → close enough for a retroactive record; *Context* can
  name the code commit when the two differ by more than a day.
