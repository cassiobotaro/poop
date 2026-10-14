# Proposal

## Why

"A method is a block, whichever way it is read" is a Principles bullet, and
it has two holes the parity check in `object-hooks-off-the-hot-path`
surfaced and left alone on purpose. A `staticmethod` read off an instance or
its class (`"".maketrans`, `str.maketrans`, `bytes.maketrans`) and a
`classmethod` read off its class (`int.from_bytes`, `float.fromhex`,
`dict.fromkeys`, `complex.from_number`, `str.is_subclass`) come back as
CPython's raw function or bound method, so `str.maketrans.print()` answers
`'function' object has no attribute 'print'` — CPython's word for a message,
naming the value `function`, which is `Block`'s own cloak — while
`str.get_attr("maketrans").print()` answers `<block>`. Same object, same
message, two answers: the exact shape the bullet was written to close for
instance methods.

## What Changes

- **A `staticmethod` or `classmethod` read off a wrapper answers a
  `_MethodBlock`**, from an instance or from the class, exactly as an
  instance method read off an instance does. The `message` descriptor
  already binds through the entry; it now wraps the bound result whenever
  that result is a function or a bound method, except for the one case the
  class side refuses anyway: a plain instance method read off the class,
  which stays the raw function so `PoopMeta.__getattribute__` keeps
  answering `#upper asks an instance; send it to one`.
- **Two reads of the same static or class method compare equal and hash
  alike**, as two reads of an instance method already do: `_MethodBlock`'s
  identity reads `__self__`/`__func__` when they exist and the function
  itself otherwise.
- **Calls and their arity wording are unchanged**: `str.maketrans("a", "b")`
  still answers `{97: 98}`, and `str.maketrans()` still answers CPython's
  cloaked `str.maketrans() missing 1 required positional argument: 'x'`,
  which `_MethodBlock.__call__` keeps on purpose.
- **`INFECTIONS.md`**: the Principles bullet gains the sentence that closes
  the two holes; the method-signature table rows that say "staticmethod" and
  "classmethod" are unchanged.

Out of scope, and why: `get_attr`'s `_as_block`, which answers a plain
`Block` with POOP's arity wording — a deliberate split `block-arity` specs
(reflection rewords, the written message keeps CPython's); the private
static helpers (`_gen`, `_call`, `_wrapping`, `_from_native`), which are not
messages; `class_side` on the metaclass, which already answers a
`_MethodBlock`.

## Capabilities

### New Capabilities
- `method-blocks`: what a method read off a POOP object or class answers — a
  block that prints, compares and calls — whichever kind of method it is and
  whichever side it is read from.

### Modified Capabilities

(none)

## Impact

- `poop/types/_descriptor.py` (`message.__get__`), `poop/types/block.py`
  (`_MethodBlock._identity`).
- Tests: `tests/test_types/test_block.py`, `tests/test_message_descriptors.py`
  (the staticmethod case flips from "stays native" to "wraps").
- Docs: `INFECTIONS.md` (one sentence in the Principles bullet).
  `README.md` counts are unchanged.
