# Design

## Context

See proposal.md for the motivation. The facts that shape the approach:

- `_cpython_name` (`poop/types/block.py`) names an instance receiver by the
  nearest wrapper in its MRO, read through `type(...)`. `Error` is a wrapper
  cloaked as `object` (`class Error(Object, name="object")`) whose `class_()`
  answers the wrapped exception's class, so the name read off its type is
  the one name the error does not answer to.
- The sweep's oracle (`_callees_cpython_would_name`,
  `tests/test_no_python_wording.py`) also reads `type(receiver).__name__`,
  so it accepted `object` for the error sample and missed the leak.
- `a_block` (`poop/types/_argument.py`) already answers `got nothing` when
  handed the `MISSING` sentinel. The collection messages declare
  `block: … | Missing = MISSING`. The branch family declares no default, so
  CPython's binding refuses before `a_block` is reached.
- `raise_` refuses extra arguments by hand on both sides:
  `_raise(self, *extra)` in `poop/types/exceptions.py` and
  `Error.raise_(self, *extra)`. Two tests pin those sentences:
  `tests/test_types/test_exceptions.py:482` and
  `tests/test_types/test_error.py:387`.
- `while_true` and `while_false` are in the sweep's `_UNSENDABLE` set
  because a sent condition block could loop. A missing *body* fails before
  either block is called, so the refusal is safe to test directly.

## Goals / Non-Goals

**Goals:**
- One rule decides whether POOP rewords an arity refusal: it does so only
  when the sentence carries a hint for what to write.
- Every name inside an arity sentence is one the receiver answers to.

**Non-Goals:**
- Making `while_true`/`while_false` sendable by the sweep. Their refusals
  are pinned by direct tests instead.
- Changing any hint's wording beyond giving the `bool` pairs both blocks.

## Decisions

### A caught error is named by its exception's class

`_cpython_name` names an `Error` receiver by `poop_class_of` of the
exception it wraps, which is what `e.class_()` and `e.class_name()` already
answer. The `Object`-owned branch is unchanged, so `e.repr(1)` still names
`object`. `Error` is imported lazily in `block.py`, with the `# circular:`
comment the package uses, because `error.py` imports `block.py`.

Alternatives considered:
- Asking every receiver for `class_()`: it would run a program's own
  `class_` override while a failure is being reworded, and every other
  wrapper already answers to its type's name.
- Renaming `Error`'s cloak: `name="object"` is what keeps `Error` itself
  out of a program's vocabulary, and the cloak is fixed per class while the
  exception kind varies per instance.

The sweep's oracle reads `receiver.class_().__name__` for an instance in
place of `type(receiver).__name__`. For every sample except the error the
two are the same, and for the error the oracle then expects `ValueError`.
That closes the blind spot without restating the implementation's rule.

### `raise_` loses its hand-written refusal

`_raise` and `Error.raise_` go back to taking no arguments. A call with one
fails at binding, and `_MethodBlock` names the class:
`ValueError.raise_() takes 1 positional argument but 2 were given` on both
sides (the error through the decision above). The two pinned tests change to
that sentence. `_count` stays imported in `exceptions.py` for `raise_from`.
`error.py` drops whatever it imported only for the refusal.

### The branch family takes `MISSING` defaults

Every block parameter of `if_true`, `if_false`, `if_true_if_false`,
`if_false_if_true`, `and_` and `or_` (on the abstract `Boolean` and on both
singletons' classes), `if_none`, `if_not_none` and the two pairs (on
`Object` and on `NoneClass`), and `while_true`/`while_false`'s `body` is
declared `… | Missing = MISSING`. These are the annotations `map` already
uses, and `a_block` turns a missing one into its `got nothing` sentence. A
pair checks both slots before running either, as it does today, so
`True.if_true_if_false(lambda: 1)` refuses the missing `false_block` and
runs nothing.

### The `bool` pairs spell both blocks

`if_true_if_false` and `if_false_if_true` pass `spelt="lambda: …, lambda:
…"` to `a_block`, as the null pairs pass `_PAIR`. The hint then shows the
shape of the call being written.

### The rule goes in INFECTIONS.md beside the arity paragraph

The rule is: an arity refusal is CPython's sentence with the right class
named, unless POOP has a hint to add, and then it is POOP's sentence
carrying that hint. It belongs in the bullet `arity-names-the-receiver`
added (*The arity sentence is CPython's, and so is the class inside it*),
together with the list of families that keep their own wording and why.

## Risks / Trade-offs

- [A `MISSING` default changes a branch message's signature as `get_attr`
  or a block made from it reports it] → A method fetched by name off an
  instance is a `_MethodBlock`, so it answers the message's sentence, not
  the `block expects …` one `block-arity` pins for classmethods fetched off
  a class. `True.get_attr("if_true")()` answers the hint, and
  over-supplying it answers `bool.if_true() takes from 1 to 2 positional
  arguments …`. A test in `test_block.py` checks `block-arity`'s
  requirement that applies here: no interpreter name reaches the program.
- [The lazy `Error` import fires on a hot path] → It is read only inside
  the `except TypeError` branch of `_MethodBlock.__call__`, which runs only
  for a failing call.
