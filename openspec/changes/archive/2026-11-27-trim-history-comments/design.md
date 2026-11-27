# Design

## Context

See proposal.md, *Why*. The decision itself, that a comment explains the code
as it is and history belongs to the commit and the ADR, is recorded in the new
ADR (task 1.1). This document keeps only how the sweep is done.

The keyword search (`used to`, `no longer`, `previously`) is a starting point,
not the inventory. The same narration also appears as a contrast between two
spellings ("`x.foo()` answered A while `foo(x)` answered B"), as a count ("43
times", "nine receivers"), and as an ordinal ("the third leak"). Each file is
therefore read in full, not only at the grep hits.

`leak` is POOP's own term for a native Python message or name reaching a
program. A sentence that says what the code prevents ("a bare `getattr` here
would leak the native class") is current reasoning and stays. Only a sentence
about a leak that once happened is history.

## Goals / Non-Goals

**Goals:**
- Every comment and docstring under `poop/` reads true against the code
  beside it, with no reference to a past state.
- The diff touches prose only. `git diff -w` shows no change to any code
  token.

**Non-Goals:**
- Rewording current reasoning for style. A long but current passage is left
  as it is (proposal, *Out of scope*).

## Decisions

1. **The rewrite rule, applied to each passage.** Ask what constraint the
   story protects, and write that constraint in the present tense. Three
   outcomes:
   - *Keep the constraint.* "A `Str`, not the raw name: the hook is the one
     place a program receives a selector."
   - *Keep a rejected alternative.* Keep it when a reader could plausibly
     write it again, phrased as why it fails today ("not `ABCMeta`: …"),
     without "it used to be".
   - *Drop the passage.* Drop it when, once the story is gone, it only
     restates the code.

   A count or an ordinal is dropped ("43 times", "the third leak"). A
   before-and-after example with two spellings stays only when it shows the
   current rule. Then it is rewritten so both lines show today's answers.

2. **ADR citation over restatement.** When an ADR in `doc/adr/` already
   carries the long reasoning, the comment keeps one sentence of reason and
   the ADR path, in the form the code already uses
   (`` `doc/adr/0034-….md` ``). New ADRs are not written for passages that
   have none. If a passage holds a decision that no ADR records, the comment
   keeps its present-tense reason, and the missing ADR is noted in the task
   as a follow-up rather than written here.

3. **One commit per package area, in file order.** The areas are core
   (`cli`, `errors`, `executor`, `interpreter`, `repl`, `console`),
   `transformers/`, `validators/`, and `types/`, which is split into
   sub-groups because it holds most of the hits. The subject is
   `docs(<area>): state the current reason, not the history`. A commit that
   changes a token outside a comment or docstring is a mistake, and the
   `git diff -w` check in each task catches it.

4. **The ADR and the contributor rule come first.** Each later commit then
   applies a rule that is already written down. The rule goes in
   `CONTRIBUTING.md` under *Conventions*, as a *Comments* subsection beside
   *Imports* and *Language*.

## Risks / Trade-offs

- **[A removed sentence was the only record of a decision]** → Before a
  passage is dropped, `git log -S` on its key phrase confirms the commit that
  introduced it explains the same thing. If neither the commit nor an ADR
  does, the reason stays in the comment in present tense.
- **[A docstring edit changes code]** → A docstring is a string constant.
  Removing a whole docstring from a function whose body is only `...` or
  `pass` would change the AST. Each task checks `git diff -w` and runs the
  full suite, and a docstring is shortened, never removed, where it is the
  only statement in the body.
- **[Review fatigue across ~50 files]** → Commits by area keep each diff
  small enough to read, and prose-only diffs are cheap to review.
