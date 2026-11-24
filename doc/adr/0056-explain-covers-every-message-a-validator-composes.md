# 56. `:explain` covers every message a validator composes

Date: 2026-08-11

## Status

Accepted

## Context

The REPL's `:explain` (`poop/repl.py`) shows, for a topic, a snippet that triggers the validator of that name, so the reader sees the refusal and its substitute. The topic list is derived from the validators, and a per-validator reachability test already existed. Reachability does not give coverage. A validator can compose more than one message, and a test that only asks whether each validator is reachable from some snippet passes while a message is never shown.

That gap was hit. `no_subscript` grew a second message for a *store*, and the `subscript` snippet stayed `x[0]`, a load. A reader who wrote `xs[0] = 9` was told to use `obj.at_put(key, value)`, typed `:explain subscript`, and was shown the *reading* substitute, the one the store message exists to stop them getting.

## Decision

Every message a validator composes is reported by some `:explain` snippet, not merely every validator. The `subscript` snippet is all four spellings of a subscript.

A test reads the literal messages out of `poop/validators/` and requires the snippets to report them all, in the shape `test_doc_counts.py` uses for the README's numbers.

## Consequences

A validator that gains a message fails the test until its `:explain` snippet is extended to trigger that message, so `:explain` cannot drift into showing one substitute for a refusal that names another.

The test reads messages as literals in the validator sources; it holds the snippets to what the validators say.
