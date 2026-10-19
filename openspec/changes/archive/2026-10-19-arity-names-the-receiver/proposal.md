# Proposal

## Why

POOP leaves the wrong-arity sentence to CPython on purpose (`_cloak.py`,
`_MethodBlock`, the wording sweep), with the callee renamed to a class a
program can write: `str.upper() takes 1 positional argument but 2 were
given`. CPython names the class that *defines* the method, so this is only
true when POOP's defining class is one CPython would name. A sweep of every
message on every wrapper, sent six arguments, found four shapes where it is
not:

- the shared mixins are cloaked as `object`, so `[1].map(1, 2)` blames
  `object.map()`, a class that does not answer `#map`;
- `bytearray` inherits `Bytes`'s methods and `frozendict` inherits `Dict`'s,
  so they blame `bytes.lower()` and `dict.keys()`, where CPython, whose two
  types define their own methods, names `bytearray` and `frozendict`;
- every class-side message is one function shared by all classes, so
  `int.hash(1)` answers `hash() takes …` with no class at all, where
  CPython's `int.mro(1)` names `int`.

`print` has a second defect: `end` and `flush` are positional, so
`(5).print("x")` prints `5x` silently, and `(5).print("x", end="")` answers
`object.print() got multiple values for argument 'end'`. In CPython the two
are keyword-only.

## What Changes

- **A mixin's message names the receiver's builtin**: `[1].map(1, 2)`
  answers `list.map() takes …`. This covers about 17 messages (`map`,
  `filter`, `do`, `reduce`, `iter`, `next`, …) on every collection, iterator
  and view.
- **`bytearray` and `frozendict` name themselves** for the messages they
  inherit from `bytes` and `dict` (47 and 10 messages).
- **The class side names the class**: `int.hash(1)` answers
  `int.hash() takes …`, and a program's own `Foo.print(1)` answers
  `Foo.print() takes …`.
- **`print` takes `end` and `flush` by keyword only**, as CPython's does,
  on every receiver: instances, sequences (with `sep`), exception instances
  and classes. `(5).print("x")` answers `object.print() takes 1 positional
  argument but 2 were given`. **BREAKING** for a program that passed `end`
  positionally. None in the repository does.
- **The wording sweep enforces the rule**: an arity sentence passes only
  when it names the class CPython would name.

Unchanged on purpose, because each already names the class CPython would:
- a message `Object` itself defines keeps `object`, as CPython's
  `(5).__reduce_ex__()` names `object` (`(5).repr(1)` answers
  `object.repr() takes …`);
- a program's subclass of a wrapper keeps the wrapper's name, as
  `class Stack(list)` makes `Stack().append()` blame `list.append()`;
- `Try(lambda: 1).except_(ValueError)` keeps `Try.except_() missing 1
  required positional argument: 'handler'`.

Out of scope, and why:
- **POOP-worded arity refusals already in place** (`Try()`, `With()`,
  `raise_`, `else_()`, `a_block`'s `got nothing`). Each replaced a sentence
  that named a dunder, an internal class or the wrong receiver. They are
  pinned by their own specs, and returning them to CPython's shape would be
  a separate decision.
- **Rewording the arity sentence itself.** Keeping CPython's shape is the
  established policy, and this change only corrects the name inside it.
- **Classmethods that CPython reports without a class**
  (`from_bytes() missing required argument`). POOP's `int.from_bytes()` is
  already named after its defining class, and making it nameless would
  follow CPython into a worse sentence.

## Capabilities

### New Capabilities

- `message-arity`: which class a message's wrong-arity sentence names, on
  the instance side and the class side.

### Modified Capabilities

- `object-type`: `print` takes `end`, `sep` and `flush` by keyword only; the
  existing "A positional end" scenario changes from the `end` refusal to the
  arity sentence.

## Impact

- `poop/types/block.py` (`_MethodBlock.__call__` renames the callee of a
  binding-time arity error).
- `poop/types/meta.py` (the `class_side` comment that called this
  unavailable), `poop/types/object.py`, `poop/types/_sequence.py` or
  wherever `sep` printing lives, `poop/types/exceptions.py` and
  `poop/types/meta.py` (`print` signatures).
- `tests/test_no_python_wording.py` (the arity check reads the callee),
  plus new tests per shape.
- `INFECTIONS.md` (*Builtin-mirroring method signatures* or *Object.print*,
  and the `_MethodBlock` arity paragraph). `README.md` shows no arity error.
