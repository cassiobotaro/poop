# Proposal

## Why

A refusal's hint shows the call to write (`— write .map(lambda item: …)`),
and the name it gives a block's argument is part of what it teaches. The
names disagree with each other in two places where they describe the same
thing:

- `find` uses two names for its own argument. A missing block answers
  `.find(lambda item: …)`, and a positional default answers
  `.find(lambda x: …, default=…)`. The Smalltalk near-miss hint for
  `detectIfNone` says `x` too.
- The null tests pass the receiver's own value, and call it `item` in
  `if_not_none` (`.if_not_none(lambda item: …)`) but `x` in both pairs
  (`.if_none_if_not_none(lambda: …, lambda x: …)`). Neither name is the one
  `Try.else_` already uses for a value handed on, `value`.

The Smalltalk hints for `timesRepeat` and `toDo` say `lambda i: …` for an
element of a range, the one place a collection element is not `item`.

## What Changes

A hint names a block's argument by its role:

- **`item` for an element of a collection**, a range included. `find`'s
  positional-default refusal and the `detectIfNone` hint say `.find(lambda
  item: …, default=…)`, and the `timesRepeat` and `toDo` hints say
  `range(n).do(lambda item: …)` and `range(a, b).do(lambda item: …)`.
- **`value` for the receiver's own value**: `.if_not_none(lambda value: …)`,
  `.if_none_if_not_none(lambda: …, lambda value: …)` and
  `.if_not_none_if_none(lambda value: …, lambda: …)`, on `None` and on
  every object, matching `.else_(lambda value: …)`.

Unchanged, because each already names its role and no other hint names the
same role differently: `lambda e: …` (a caught error), `lambda resource: …`
(`With`), `lambda a, b: …` (`reduce`), and every hint with no argument.

Out of scope, and why:
- **Code examples in `README.md`, `INFECTIONS.md` and `examples/`** that
  write `lambda x: …`. They are programs, not hints, and a program names
  its parameters as it likes.
- **Changing any sentence around the placeholder.** Only the name changes.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `none-type`: the paired test's non-block refusal hints `lambda value: …`.
- `object-type`: the same, on every object.
- `message-arity`: the missing-block refusal of a null pair hints `lambda
  value: …`.
- `collection-iterable-methods`: `find`'s positional-default refusal hints
  `lambda item: …`.
- `does-not-understand`: the `timesRepeat` hint says `lambda item: …`.

## Impact

- `poop/types/object.py` (`_PAIR`, `_PAIR_SWAPPED`, `if_not_none`'s
  `a_block` call), `poop/types/none.py` (`if_not_none`), and
  `poop/types/_iterable_mixin.py` (`find`'s refusal).
- `poop/types/_selectors.py` (`detectIfNone`, `timesRepeat`, `toDo`).
- The tests that pin the old hints: `tests/test_types/test_object.py`,
  `test_none.py`, `test_list.py`, `test_message_arity.py`,
  `test_does_not_understand.py`.
- `INFECTIONS.md`, where it quotes a hint sentence.
