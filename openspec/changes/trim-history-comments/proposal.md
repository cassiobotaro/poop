# Proposal

## Why

About 30% of the lines under `poop/` are prose: 1,827 comment lines and about
3,200 docstring lines out of 16,730. Much of it tells the story of an earlier
implementation or a fixed bug instead of explaining the code as it stands. For
example, `Object.__init_subclass__` says "It used to be a statement after the
class, 43 times", and `Object.format` counts "Two leaks in one method… The
third leak". `git grep -iE "used to|no longer|previously"` finds 57 such lines
in 51 files, and passages that say "X answered A while Y answered B" without
those words add more.

That story is already recorded in the commit that fixed the bug and, for every
real decision, in an ADR in `doc/adr/`. Kept next to the code, it goes stale
as the code moves on. It also hides the sentence a reader actually needs, the
reason the code is written the way it is today, under a paragraph about what
it once did wrong.

## What Changes

- **Comments and docstrings under `poop/` state the current reason only.** A
  passage that narrates a past bug or an earlier implementation is rewritten
  as the constraint it protects, in the present tense. A rejected alternative
  stays when a reader might reintroduce it ("`type`, not `ABCMeta`: …"), but
  not the story of when it was rejected. A passage whose reasoning is long and
  already lives in an ADR is shortened to the reason plus the ADR path.
- **A passage with nothing left after the history goes away.** This applies
  when the code below it is self-explanatory once the story is removed.
- **New ADR**, the next number in `doc/adr/`: a comment explains the code as
  it is, and the history of a change belongs to its commit and its ADR.
- **`CONTRIBUTING.md` gains the rule** in its comments guidance, so later
  changes do not add the pattern back.

No behaviour of the language changes. No error message, no public name and no
test assertion changes.

## Capabilities

### New Capabilities
<!-- none -->

### Modified Capabilities
<!-- none: comments, docstrings and contributor docs only; no spec-level
     behaviour. `.openspec.yaml` declares `skip_specs: true`. -->

## Impact

- Edited: comments and docstrings in about 50 files under `poop/`;
  `CONTRIBUTING.md`; a new `doc/adr/NNNN-*.md`.
- Docstrings under `poop/` are not user-visible. No `help` exists, and
  nothing reads `__doc__`. Only `tests/test_examples_docstring.py` reads
  docstrings, and it reads the ones in `examples/`, which this change leaves
  alone. The existing suite is therefore the behaviour gate, and it must pass
  unchanged.
- `README.md` and `MIGRATION.md` describe behaviour and are not edited.

## Out of scope

- **`tests/`.** A test's docstring often names the regression it pins, which
  is the one place where the history is the point. It is left as it is.
- **`examples/`.** Its docstrings are user-facing and carry the Smalltalk
  equivalent required by `AGENTS.md`.
- **Accepted ADRs and archived changes.** They are history by definition, and
  an accepted ADR is never edited.
- **Shortening prose that is current.** A long comment that explains today's
  constraint stays long. This change removes the narrative, not the reasoning.
- **The other items of the same review.** Moving the renderer out of
  `errors.py`, exit codes on the error classes, immutable registries and the
  smaller cleanups are separate changes, so each one can be reviewed on its own.
