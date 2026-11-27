# 71. A comment states the current reason; history lives in the commit

Date: 2026-11-26

## Status

Accepted

## Context

About 30% of the lines under `poop/` are prose: 1,827 comment lines and about 3,200 docstring lines out of 16,730. Much of it narrates an earlier state of the code instead of the code as it stands: "It used to be a statement after the class, 43 times", "Two leaks in one method… The third leak". `git grep -iE "used to|no longer|previously"` finds 57 such lines in 51 files.

The commit that fixed each bug already records that history, and the ADRs in `doc/adr/` record each real decision. A copy kept next to the code goes stale as the code changes. A reader also has to get through it to reach the sentence they need, which says why the code is written this way today.

## Decision

We will write comments and docstrings under `poop/` about the code as it is. A passage states the constraint the code protects, in the present tense. A rejected alternative a reader might write again stays, phrased as why it fails today ("`type`, not `ABCMeta`: …"), without the story of when it was rejected. Counts of call sites, ordinals of fixes, and before-and-after accounts of a bug go in the commit message. When an ADR already holds the long reasoning, the comment gives one sentence and the ADR's path.

Test docstrings in `tests/` are exempt. There the regression is what the test pins, so naming it is the current reason.

## Consequences

The provenance of a line is no longer visible where the line is. A reader who wants to know what the code used to do, or which bug a guard closed, runs `git log -S` or `git blame`.

The existing comments and docstrings under `poop/` are rewritten to follow the rule. `CONTRIBUTING.md` states the rule so that later changes do not bring the pattern back.
