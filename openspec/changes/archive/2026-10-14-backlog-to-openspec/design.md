# Design

## Context

See proposal.md - Why. Facts the approach rests on:

- `proposals.md` is empty. Its history: 132 `docs: close proposal N` commits,
  the last audit (`86e2a14`) opened 20 items at once and 11 closed in one
  commit (`525caa7`). Items were proposal-shaped: problem, measured evidence,
  "Fix." steps — the content of an OpenSpec `proposal.md` plus `tasks.md`.
- `INFECTIONS.md` is 1370 lines: 45 of principles, 71 rationale paragraphs
  carrying most of its 29k words, 369 table rows of reference (AST node →
  rewrite, Smalltalk message → POOP idiom, method signatures), 114 sections.
  Nothing in `poop/` or `tests/` reads it; source comments cite it.
- `openspec/config.yaml` is the scaffold with every key commented out. The
  three changes so far were written without project context; the English rule
  and the "everything is a message" principle were applied from memory.
- The four main specs are named `float-type`, `complex-type`, `bytearray-type`
  and `block-arity`; no rule says why.
- The `backlog` skill is four lines that begin "Read proposals.md".

## Goals / Non-Goals

**Goals:**
- One backlog, described the same way in every document an agent or
  contributor reads.
- Every new change starts with the project's constraints in hand.
- A spec and the catalogue section about the same thing are findable from
  each other by name.

**Non-Goals:**
- Converting `INFECTIONS.md` into specs. Requirement-and-scenario is the
  wrong shape for 369 reference rows and has no home for 71 rationale
  paragraphs; a bulk rewrite would leave a worse catalogue and the *why*
  scattered across archived `design.md` files.
- Migrating closed proposals into `openspec/changes/archive/`. The git log is
  the changelog (CONTRIBUTING, Versioning) and already holds them.
- Changing how `INFECTIONS.md` is maintained: the same-commit rule stays.

## Decisions

**1. Delete `proposals.md` rather than leave a pointer stub.** A stub is a file
every reader opens to learn it is empty. The README's "Where to next" and
CONTRIBUTING's "Open backlog" line point at `openspec/changes/` instead, which
is where the content is.
*Alternative*: keep a one-paragraph `proposals.md` redirect. Rejected: two
places again, one of them permanently empty.

**2. The backlog is the active-change list; closing is archiving.** No numbers:
a change has a kebab-case name, `openspec list` shows task progress, and the
archive directory carries the date. The closing commit is the archive commit
(`chore(openspec): archive <name>`), which the three archived changes already
use.

**3. One change per theme, one task per finding.** An audit yields one change
whose `tasks.md` has a checkbox per finding; a single idea is a change with few
tasks. This is the pattern the old backlog converged on (items 1–11 closed
together) and it keeps `openspec/changes/` readable. CONTRIBUTING states it
so the next agent does not open twenty directories.

**4. `INFECTIONS.md` keeps the *why*; `openspec/specs/` holds the *what*, by
delta only.** The two have different jobs and different shapes. The join is a
naming rule (decision 5) and the existing same-commit rule. Only one sentence
in the catalogue changes, the one that names `proposals.md`.
*Alternative*: seed `openspec/specs/` from the reference tables. Rejected for
now: large, lossy, and nothing enforces specs (the wording sweep and
`test_doc_counts` enforce the code and the README), so the migration would buy
a parallel document, not a check.

**5. Capability names mirror the catalogue's sections.** `<builtin>-type` for a
wrapper (`float-type`, matching `### Float` under Active types),
`<name>-validator` (`no-len-validator`, matching `### no_len`),
`<name>-transformer`, and a plain noun for a cross-cutting behavior
(`block-arity`). Flat layout, as the four existing specs are. The rule lives
in `config.yaml` under `rules.specs`, where `openspec instructions specs`
hands it to whoever writes a delta.

**6. `config.yaml` context points, it does not copy.** The context names where
the principles live (INFECTIONS.md, Principles), the English rule, the
same-commit docs rule and decision 3. It does not paste the principles: they
are 45 lines that change, and OpenSpec would feed a stale copy into every
artifact.

**7. The `backlog` skill is rewritten, not deleted.** `/opsx:*` are the
mechanics; the skill is the project's loop around them and keeps the two rules
the old one carried: discuss trade-offs with the user before implementing,
confirm scope (which tasks) before applying. It becomes: `openspec list`, pick
a change with the user, `/opsx:apply`, full gate, `/opsx:archive`, commit the
archive.

## Risks / Trade-offs

- [An agent reading an old clone or a cached guide still writes to
  `proposals.md`] → the file does not exist; the AGENTS.md bullet names the
  replacement, and `git status` shows the stray file.
- [Issues on GitHub become the only place for ideas that are not yet changes]
  → that is already CONTRIBUTING's alternative ("or via an issue"); a change
  can be scaffolded from an issue when it is ready.
- [Context in `config.yaml` drifts from the documents it points to] → it
  points by name, not by content; the documents stay the source.
