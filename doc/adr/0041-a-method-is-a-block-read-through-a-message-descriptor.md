# 41. A method is a block, read through a `message` descriptor

Date: 2026-07-25

## Status

Accepted

## Context

A block is POOP's only callable value (ADR 28), and a method read off an object answered CPython's bound method instead: callable, yet understanding no message. `"abc".get_attr("upper").print()` raised Python's own `AttributeError`. `_as_block` (`poop/types/block.py`) closed that for `get_attr` only, the spelling almost nobody writes, so `"abc".get_attr("upper").print()` answered `<block>` while `"abc".upper.print()` answered `'function' object has no attribute 'print'`: CPython's word for a message, naming the value `function`, which is `Block`'s own cloak.

The ordinary spelling, `[1, 2].len`, is `ast.Attribute` syntax in `Load` position, which a validator cannot tell from a state read without runtime types (`self.count` is a plausible field name that is also a message). The only hook that sees a successful lookup is `__getattribute__`, which every message send goes through. Wrapping there first measured 1.12 s → 2.02 s on 200k sends, +81% on the central operation of the language, and broke nine wrong-arity diagnostics by making them blame the wrapper instead of the receiver, so the leak was first accepted.

The first version that closed it was an `Object.__getattribute__` anyway, next to an `Object.__setattr__` that reworded CPython's `'str' object has no attribute 'x' and no __dict__ for setting new attributes`. Each did one job and ran far beyond it. `__getattribute__` ran on every attribute read in the language, including the library's own `self._value` (401 ns against 192 on 3.15). `__setattr__` ran on every object construction, since every wrapper writes its payload in `__init__` (`Int(3)` 846 ns, 483 without it). The `2026-10-14-object-hooks-off-the-hot-path` change replaced both.

That change kept parity and left two holes, closed by `2026-10-14-method-blocks`: a `staticmethod` read off an instance or its class and a `classmethod` read off its class came back raw, so `str.maketrans.print()` and `int.from_bytes.print()` answered `'function' object has no attribute 'print'` while `str.get_attr("maketrans").print()` answered `<block>`.

## Decision

A method is a block whichever way it is read, and a block on a class is a method.

- Every public method is a `message` descriptor (`poop/types/_descriptor.py`), installed where the class is built: `PoopMeta.__new__` wraps every public function, `classmethod` or `staticmethod` in the namespace, and `_Mixin.__init_subclass__` does the same for the mixins, which are not `PoopMeta` classes. It is a non-data descriptor that keeps the innermost function in `__func__`, the convention `classmethod` set, so `cloak`'s renaming and the class side's instance-only refusal unwrap it without a special case.
- The descriptor wraps on the shape of the bound result: it answers a `_MethodBlock` when the result is a `MethodType` (an instance method off an instance, a classmethod off either side) or the entry is a `staticmethod`. A plain instance method read off the class stays the raw function, so the class side keeps refusing it with `#upper asks an instance; send it to one` (ADR 37).
- `_`-prefixed names and dunders are never messages and resolve at C speed.
- A `_MethodBlock` keeps CPython's arity wording, which `cloak` has already worded for a message (`str.upper() takes 1 positional argument…`); `Block`'s rewording would replace the message's name with the word `block`. Two reads of the same method compare equal and hash alike.
- Reflection answers a plain `Block` through `_as_block`, used by `Object.get_attr` and the class side, with `Block`'s arity wording. State, a `default` fallback and a POOP class pass through it untouched. `PoopMeta._reflected` reads the MRO dicts and binds the raw entry past a `message`, keeping that split.
- `Block.__get__` makes a block installed on a class bind to the receiver, so `C.set_attr("greet", lambda self: "hi")` works. Defining only `__get__` makes it a non-data descriptor, so a block held as state in an instance's `__dict__` reads back as itself.
- `Object` has no Python-level hook on its instance side. A per-value refusal is a pattern in `poop_message`; the assignment refusal there answers `str is a value — it holds no state of its own; only an object of a class you defined can be given one`, read by the executor's report and by `Error.message()`, and `set_attr` and `del_attr` compose the same sentence themselves.

## Consequences

- `[1, 2].len` answers a block, as `get_attr("len")` does. The two reads differ only in arity wording: `int.from_bytes()` keeps the method's cloaked sentence, `int.get_attr("from_bytes")()` answers `block expects 1 to 2 arguments, got 0`.
- Measured in one session, best of five: `(5).abs()` 3536 → 2404 ns, `a._value` 402 → 200, `Int(3)` 846 → 483, `Int + Int` 2857 → 1713, `Int < Int` 3061 → 1547, `xs.map(block)` 5156 → 2889.
- The wrap still costs frames on every send: two of the six Python frames per message send are `_MethodBlock.__call__`, about a third of the recursion ceiling, which ADR 61 sizes the limit for.
- A tool that walks `vars(cls)` meets a descriptor where it expected a function and must unwrap `__func__`; the REPL completer does, which also gives a `classmethod` entry its `(`.
- `tests/test_message_descriptors.py` asserts neither hook is back on `Object` and that every public read on every sweep sample still answers a `_MethodBlock`.
