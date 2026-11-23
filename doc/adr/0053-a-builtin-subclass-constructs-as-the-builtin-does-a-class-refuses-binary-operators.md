# 53. A builtin subclass constructs as the builtin does; a class refuses binary operators

Date: 2026-08-10

## Status

Accepted

## Context

A bare builtin name binds an alias class whose call is the converter, while the wrapper class it is built on means "build from these elements" (ADR 51). That convert-versus-build gap, and the two objects that both call themselves by the builtin's name, reappeared wherever a class is called, climbed, compared or handed to an operator.

- Calls at another arity. Every rewriter guarded its `visit_Call` on the arity its converter could handle and let anything else fall through to `visit_Name`, which renames the bare builtin to the variadic class. `list(1, 2)` answered `[1, 2]` where CPython raises `list expected at most 1 argument, got 2`, and `set(1, 2)` answered `{1, 2}`. `list(a, b)` is a plausible slip for `[a, b]`, and being accepted is the failure mode POOP's diagnostics work hardest to avoid. The scalar wrappers answered right but reported `__init__`: `str(b"ab", "utf-8")` answered `str.__init__() takes 2 positional arguments but 3 were given`, for a call CPython answers `"ab"` to.
- Subclasses. `_AliasMeta.__call__` read `_converter` off `cls.__dict__` and stopped there, so all thirteen constructors disagreed with themselves for `class Stack(list)`, the spelling `_alias.py` names as legal. Seven did so silently (`Stack([1, 2])` held one list; `class N(int)` then `N(4.9)` held 4.9) and six refused in Python's words: `dict.__init__() takes 1 positional argument but 2 were given`, `__str__ returned non-string (type int)`, `cannot use 'list' as a set element`. A subclass whose `__init__` never passed its arguments up came back with no payload, and the first message answered `N does not understand #_value`. `bool` as a base failed at the first instance with `Can't instantiate abstract class Flag without an implementation for abstract methods '__bool__', '__str__', …`.
- `super().__init__(...)`. `no_dunder_attribute` carves out exactly this dunder call, and it reached the wrapper's variadic `__init__`: `class S(list)` calling `super().__init__(xs)` held one list, and `class D(dict)` answered `dict.__init__() takes 1 positional argument but 2 were given`.
- Class-side constructors. `fromhex` and `from_bytes` are classmethods, so `cls` was the alias and its call converted a finished Python value: `bytes.fromhex("6162")` answered `'int' object has no attribute '_value'`, and `int.from_bytes(…)` and `float.fromhex(…)` answered `cannot convert int to int` / `cannot convert float to float`.
- Operators on a subclass. `_SetAlgebraMixin` built results with `type(self)`, the class built on the alias, so `Bag() | {1}` read as "convert `1` to a set" and answered `cannot convert int to set`, on all eight forward set operators of `set` and `frozenset`. CPython's `Bag() | {1}` is a `set`.
- `slice`. It was the one constructor bound to its class, so `s = slice; s(5)` and `class S(slice): pass; S(5)` silently answered `slice(5, None, None)`, where the call by name answers `slice(None, 5, None)`.
- The ladder and equality. `int.superclass()` answered a class calling itself `int`, `int.superclass().is_identical(int)` denied it, and `object` was two steps up. `PoopMeta` defined no `==`, so `int == int` handed a raw Python `bool` to user code (`'bool' object has no attribute 'print'`), and `(5).class_() == int` was `False`.
- Operators on a class. An operator handed a class answered with the metaclass: `int | 5` read `_AliasMeta does not understand #| with an int` and `Object | 1` read `PoopMeta does not understand #|`. `type` answered `|` itself with a `typing.Union`, a value for annotations, which POOP does not write.

## Decision

A builtin's name, its alias, the wrapper and a program's subclass of it construct and compare as the one builtin class does, and every class refuses binary operators under its own name.

- Every `<builtin>(...)` reaches its converter, which refuses over-supply through `refuse_extra_arguments` (`poop/transformers/_arity.py`): `list is built from at most one collection, got 2 arguments — write a literal for elements`. `_poop_str_from` grew CPython's decoding form, delegating to `Bytes.decode`. The `visit_Name` rename stays for a bare name used as a value, unreachable by a call.
- `_AliasMeta.__call__` looks the converter up along the MRO and rebuilds its answer as `cls`, slot by slot, with `_payload_slots` reading the slots off the `__slots__` declarations; the payload is copied. A subclass declaring its own `__init__` is built by it, and `bool` passes its converter's answer through.
- `_endow` gives a subclass its payload as CPython's `__new__` does: one positional argument and no keywords converts, anything else gets the wrapper's empty value, and a wrapper with no empty value (`int`) cannot be built that way. `bool` is refused as a base, where CPython refuses it.
- The alias carries an `__init__` that converts and fills the payload, which the MRO places where `super()` looks (`S.__mro__` is `(S, <alias>, List, …)`).
- `_alias.wrapped_instance` builds class-side constructors through the wrapper; a program's `class B(bytes)` still gets a `B` from `B.fromhex(…)`. `ByteArray.fromhex` is added.
- The set mixin has the `_rewrap` hook `_BytesLikeMixin` has, so an operator on a subclass answers the builtin. The messages (`union`, `isdisjoint`, ...) stay written on each class, because a wrong-arity call is reported under the function's `__qualname__`.
- `_poop_slice_cls` is the `slice` alias; a rebound name refuses four arguments with the literal's sentence.
- `PoopMeta.superclass` skips a base that `unalias` maps to the receiver. `PoopMeta.__eq__` / `__ne__` answer a `Boolean` and read both sides through `unalias`. `is_identical` does not unalias, since it asks identity. `__hash__` is re-declared as `type.__hash__`, since `NATIVE_TO_POOP` keys on classes.
- `PoopMeta` carries every binary slot, forward and reflected (`poop/types/meta.py`, `_CLASS_SIDE_OPERATORS`), raising with the class in its own slot: `int does not understand #| with an int`, `list does not understand #+ with the class list`. `|` is refused with the rest. Equality stays identity, as CPython's is.

## Consequences

`list(xs)`, `Sub(xs)` and `super().__init__(xs)` agree. Over-supply answers what the direct call answers: `super().__init__(*xs)` says `list is built from at most one collection, got 2 arguments`, CPython's own reply to `list.__init__(self, 1, 2)`.

A new wrapper is covered by declaring `__slots__`, with no table to update.

A program's `class Stack(list)` has `list` as its superclass, the name it wrote.

The package spells its own runtime unions as tuples (`isinstance(x, (Int, Float))`), since `|` on a class is refused. The ordering comparisons have no reflected dunder, so `5 < int` reaches `__gt__` on the class and the sentence names that slot.

The wording sweep's operator half pairs three class receivers (`int`, `ValueError`, `Object`) with every operand and bans the metaclass names outright.
