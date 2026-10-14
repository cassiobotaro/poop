# Proposal

## Why

Every POOP value inherits two Python-level hooks from `Object`:
`__getattribute__`, which wraps a public bound method in a `_MethodBlock` so
`"abc".upper.print()` answers `<block>`, and `__setattr__`, which rewords
CPython's `no __dict__ for setting new attributes` when a program assigns an
attribute on a value. Both run far beyond the cases they exist for.
`__getattribute__` runs on every attribute read in the language, including
the library's own `self._value`, and costs a Python frame each time (401 ns
for `a._value` against 192 with the hook gone). `__setattr__` runs on every
object construction, since every wrapper writes its payload in `__init__`
(852 ns for `Int(3)`, 486 without it) — its own docstring says the cost is
"bounded ... nothing else hot", which the measurement contradicts: every
arithmetic result builds a value.

Prototyped in one session on the current tree, a message send `(5).abs()`
goes from 3568 ns to 2238 (-37 %), `Int + Int` from 2825 to 1719 (-39 %) and
`Int(3)` from 852 to 486 (-43 %), with no change to what anything answers.
This is the largest remaining performance item after `hot-path-imports`.

## What Changes

- **Messages become descriptors, and `Object.__getattribute__` goes.** Where
  a class is built (`PoopMeta.__new__`, and `_Mixin.__init_subclass__` for
  the mixins, which are not `PoopMeta` classes), every public entry whose
  function is a plain `FunctionType`, `classmethod` or `staticmethod` is
  wrapped in a small non-data descriptor. Read off an instance it binds the
  way the entry did and answers a `_MethodBlock` when the bound result is a
  `MethodType` — the exact test the hook makes today, so the same reads wrap
  and the same reads (staticmethods, properties) stay native. Read off the
  class it answers what the entry answered, so `PoopMeta.__getattribute__`'s
  instance-side refusal and `_instance_only` keep working with one unwrap.
  `_`-prefixed names and dunders are never wrapped and now resolve at C
  speed.
- **`Object.__setattr__` goes, and its sentence moves to `poop_message`.**
  The rewording of `'str' object has no attribute 'x' and no __dict__ for
  setting new attributes` into `str is a value — it holds no state of its
  own; only an object of a class you defined can be given one` becomes a
  pattern in `poop/types/_message.py`, beside the operator and hash patterns
  that already live there, read by `executor._describe` and `Error.message()`
  alike. `set_attr` and `del_attr` keep composing the sentence themselves
  through the same helper.
- **A deterministic guard and a recorded measurement.** A test asserts that
  `Object` defines neither hook and that every public method read off every
  sweep sample still answers a `_MethodBlock`; the before/after timings are
  recorded in `design.md`, with stop conditions.
- **`INFECTIONS.md`**: the Principles bullet on "a method is a block" names
  the descriptor instead of `__getattribute__`; a paragraph in the Object
  section records the two hooks, the measurement and the rule.

No observable behavior changes: every message answers what it answered, the
refusal sentences are the same words, and `skip_specs` is declared.

Out of scope, and why: rewriting `obj.m(args)` at the transformer level to
bypass the wrap (touches every call site, tracebacks and the arity wording
`cloak` provides; the two hooks above buy more for less); making
`_MethodBlock` construction bypass `type.__call__` (measured at ~150 ns once
`__setattr__` is gone, not worth a second code path); `PoopMeta.__setattr__`
and `PoopMeta.__getattribute__`, which run on class-side reads only.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

(none — performance-only refactor; `skip_specs: true`)

## Impact

- `poop/types/_message.py` (new `message` descriptor or a sibling module,
  the `no __dict__` pattern, `holds_no_state`), `poop/types/meta.py`
  (`__new__` installs descriptors, `_instance_only` unwraps),
  `poop/types/_mixin.py`, `poop/types/_cloak.py` (unwrap when renaming),
  `poop/types/object.py` (two hooks removed, `_holds_no_state` delegates),
  `poop/types/block.py` (the `class_side.__get__` comment that cites the
  hook).
- Tests: `tests/test_hot_paths_bind_late.py` (new operations), a new
  `tests/test_message_descriptors.py`, and any test that asserts the
  assignment refusal at the Python level moves to asserting it through
  `poop_message`.
- Docs: `INFECTIONS.md`. `README.md` counts are unchanged.
