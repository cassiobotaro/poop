# Design

## Context

See proposal.md - Why. What the approach rests on, verified on the tree:

- `Object.__getattribute__` (hidden from ty under `if not TYPE_CHECKING`)
  does one thing: `type(value) is MethodType and not name.startswith("_")`
  then `_METHOD_BLOCK(value)`. `Object.__setattr__` does one thing: catch
  `AttributeError` from `object.__setattr__` and raise `_holds_no_state`.
- Every POOP class is made by `PoopMeta.__new__` (wrappers, user classes
  via `ClassTransformer`, exception mirrors through `PoopExcMeta`, aliases
  through `_AliasMeta`); the shared mixins (`_Mixin` subclasses) are plain
  classes with their own `__init_subclass__` that calls `cloak`. Functions a
  class owns are visited once already, by `cloak._rename_own_functions`,
  which unwraps `classmethod`/`staticmethod` through `__func__`.
- `PoopMeta.__getattribute__` refuses an instance-side method read off the
  class by testing `type(value) is FunctionType` and `_instance_only`, which
  reads `vars(klass)[name]`. `class_side` is already a descriptor on the
  metaclass whose `__get__` answers a `_MethodBlock` for the class side.
- `poop_message` in `_message.py` rewords two CPython shapes by regex; both
  `executor._describe` and `Error.message()` read through it, so a sentence
  reworded there is the same in the report and in a `Try` handler.
- Baseline, this machine, best of five, 20 000 iterations: `(5).abs()` 3568
  ns, `a._value` 401, `Int(3)` 852, `Int + Int` 2825.

## Goals / Non-Goals

**Goals:**
- No Python-level `__getattribute__` or `__setattr__` on `Object`.
- Every read that answered a `_MethodBlock` still does; every read that
  answered a native (staticmethod, property, `_`-name, dunder) still does.
- The assignment refusal reads the same words through the interpreter and
  through `Error.message()`.

**Non-Goals:**
- Changing what a `_MethodBlock` is or answers.
- Class-side lookup (`PoopMeta.__getattribute__`, `class_side`).
- Asserting timings in CI.

## Decisions

**1. A `message` descriptor, installed where the class is built.** A small
class with `__slots__ = ("__func__",)` holding the original entry (function,
`classmethod` or `staticmethod`), defining only `__get__` (non-data, like
`Block.__get__`, so an instance `__dict__` entry on a user class still wins).
`__get__(None, owner)` answers `self.__func__.__get__(None, owner)` for a
`classmethod`/`staticmethod` and the raw function for a plain one, so the
class side sees exactly what it saw. `__get__(inst, owner)` binds through
the entry and wraps the result in a `_MethodBlock` when `type(bound) is
MethodType` — the hook's own test, kept so staticmethods (plain functions
when bound) stay native as they are today. Installed by `PoopMeta.__new__`
over the namespace before `type.__new__` runs, and by `_Mixin.__init_subclass__`
over `vars(cls)`, for names `is_message` accepts. Named `__func__` so
`_rename_own_functions`'s existing `getattr(attr, "__func__", attr)` unwraps
it with no change. *Alternative*: install in `cloak`. Rejected: user classes
are never cloaked, and their methods must wrap too.

**2. `_instance_only` unwraps the descriptor; `PoopMeta.__getattribute__` is
otherwise unchanged.** It reads `type(getattr(entry, "__func__", entry)) is
FunctionType`, so `str.upper()` still answers `#upper asks an instance; send
it to one`. `_reflected` (the `get_attr` path on a class) reads the MRO dicts
and unwraps the same way, answering the unbound function as it does today.

**3. `Object.__setattr__` is deleted; the sentence is composed in one place.**
`holds_no_state(class_name)` moves to `_message.py`; `set_attr` and
`del_attr` call it, and `poop_message` gains `_NO_STATE = re.compile(r"^'(.+?)'
object has no attribute '.+?' and no __dict__ for setting new attributes$")`
answering `holds_no_state(match.group(1))`. The class name CPython prints is
the cloaked one (`cloak` sets `__name__`), so the sentence reads `str is a
value`, as it does today. *Alternative*: keep the hook but call
`object.__setattr__` from each wrapper's `__init__`. Rejected: 40 call sites
to keep honest, and the hook would still run on user-class stores.

**4. Wrapping order inside `_MethodBlock` is unchanged; construction stays
through `type.__call__`.** With `__setattr__` gone, `Block.__init__`'s one
slot write is C-speed; the remaining ~150 ns of `type.__call__` is not worth
a second construction path.

**5. The guard is structural, the measurement is recorded.**
`tests/test_message_descriptors.py` asserts `"__getattribute__" not in
vars(Object)` and `"__setattr__" not in vars(Object)`, that for every sweep
sample every `is_message` name whose MRO entry wraps a function or
classmethod answers a `_MethodBlock`, that a staticmethod (`str.maketrans`
read off `"abc"`) answers a plain function as before, that a user class
method reads as a `_MethodBlock` and `super()` inside one still works, and
that the assignment refusal reads the same words through `poop_message` and
through `set_attr`. The timings run once, in this change, and land under
*Measured*.

## Risks / Trade-offs

- [`super().m()` inside the library now binds through the descriptor and
  pays a `_MethodBlock`] → it already did through `__getattribute__`; the
  counter test and the full suite cover it; measured, not assumed.
- [A tool walking `vars(cls)` meets a descriptor where it expected a
  function: `_rename_own_functions`, `_instance_only`, `_reflected`,
  `__dir__`, `test_slots`, the wording sweep's `dir()`] → `__func__` is the
  unwrap convention `classmethod` already set; `dir()` and `__dir__` list
  names, not values; `test_slots` reads `__slots__`. Each named site is a
  task.
- [A `classmethod` read off an instance stops wrapping] → it binds to a
  `MethodType`, so it wraps exactly as today; pinned by the new test.
- [The `__dict__` sentence shows up through a path that does not read
  `poop_message`] → `pytest.raises(AttributeError, match=...)` at the Python
  level does; such tests move to `poop_message(exc)` or to the interpreter,
  which is what a program sees.
- [The gain is smaller than the prototype] → stop conditions: `Int + Int`
  and `Int(3)` at least 30 % faster, `(5).abs()` at least 25 %, `a._value` at
  least 40 %; otherwise stop and report before archiving.

## Measured

Same script, same session, best of five runs of 20 000 iterations, ns/op.

| Operation | Before | After | Change |
|---|---|---|---|
| `(5).abs()` | 3536 | 2404 | -32 % |
| `a._value` | 402 | 200 | -50 % |
| `Int(3)` | 846 | 483 | -43 % |
| `Int + Int` | 2857 | 1713 | -40 % |
| `Int < Int` | 3061 | 1547 | -49 % |
| `Int == Int` | 2473 | 1209 | -51 % |
| `Int * Float` | 3548 | 2188 | -38 % |
| `an_int(Int)` | 1126 | 888 | -21 % |
| `List.at` | 4448 | 2999 | -33 % |
| `Str.len` | 3610 | 2562 | -29 % |
| `true.if_true` | 2420 | 1792 | -26 % |
| `xs.map(block)` | 5156 | 2889 | -44 % |

Every stop condition held: `Int + Int` and `Int(3)` cleared 30 %, `(5).abs()`
25 %, `a._value` 40 %.

Two things the apply found that the design had not named: `set_attr` relied
on the hook to compose its refusal (it called `setattr` and let
`__setattr__` reword), so it now catches the `AttributeError` and composes
the sentence itself, as `del_attr` already did; and ty, no longer seeing a
custom `__setattr__`, checks slot writes and flagged `_MappingMixin._wrapping`'s
`wrapped._data = data`, where the slot belongs to the concrete class — one
`ty: ignore[missing-slot]` with the reason.

A third thing CI found that the local gate had hidden (its summary line was cut
from the output): the REPL completer reads class-dict entries through
`inspect.getattr_static` and appended `(` when the entry was callable, so a
`message` descriptor lost `n.abs` its parenthesis. It unwraps `__func__` now,
which also gives a `classmethod` entry (`n.from_bytes`) the `(` it never had.

A pre-existing leak the parity check surfaced, out of scope here: a
`staticmethod` read off an instance (`"".maketrans`) is a plain function
before and after, so `"".maketrans.print()` answers CPython's `'function'
object has no attribute 'print'`. The descriptor preserves this on purpose
(parity); closing it is a wording finding for a change of its own.
