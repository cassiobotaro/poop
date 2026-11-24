# 37. The class side is data descriptors on a `type` metaclass and refuses instance messages

Date: 2026-07-15

## Status

Accepted

## Context

Classes are objects and answer messages, as in Smalltalk. In Python they did not: `Foo.print()` answered `Object.print() missing 1 required positional argument: 'self'`, which is Python failing to bind a method, not POOP refusing a message. The bans then contradicted themselves: `hash(Foo)` answers "use `obj.hash()` instead" while `Foo.hash()` answered a binding error, naming a substitute that did not exist on that receiver.

A metaclass cannot simply define those messages. Attribute lookup on a class searches the class's own MRO before the metaclass, so a plain `PoopMeta.print` would never be reached. `Object.print` would win and answer the unbound function. Only a data descriptor is consulted first.

The first fix covered `Object`'s protocol only. The wrapper's own messages still bound badly from the class: `str.upper()` answered `str.upper() missing 1 required positional argument: 'self'`, naming `self`, a receiver POOP never spells, and "positional argument", which the wording sweep bans outright. 64 of the 90 names `str.dir()` listed answered that, 32 of 58 on `list`, 30 of 57 on `dict`.

Discovery missed the class side. CPython's `type.__dir__` walks the class's own MRO only, so `Foo.dir()` answered no `name` and no `superclass`, and `ValueError.dir()` no `raise_`.

`PoopMeta` used to derive from `ABCMeta` for one class, `Boolean(Object, ABC)`, and every `isinstance` against a POOP class then went through `ABCMeta.__instancecheck__`: `isinstance(5, Int)` took 422 ns instead of 86, and a loop-heavy benchmark ran about a quarter slower.

Smalltalk's `Foo class` answers the metaclass. `PoopMeta` is not itself a POOP class (`type(PoopMeta)` is `type`), so handing it back would leak the raw class object the class side exists to remove, and answering `Foo` would make `class_name` mean one thing on an instance and another on a class.

## Decision

`PoopMeta` (`poop/types/meta.py`) derives from `type`, not `ABCMeta`. Nothing declares it, because `ClassTransformer` routes every user class through `Object`, and a metaclass is inherited.

Every class-side message is a `class_side` data descriptor, and all of `Object`'s protocol is answered class-side, each message by its own descriptor: `name`, `superclass`, `has_attr`, `print`, `does_not_understand`, `hash`, `is_none` / `not_none`, `not_`, `repr` / `ascii`, `callable`, `dir`, `format`, `is_identical` / `not_identical`, `is_instance`, `get_attr` / `set_attr` / `del_attr` (dunder guard included), `assert_`, and `if_none` / `if_not_none`. `Foo.superclass()` answers the superclass object, and `Object superclass` answers `none`, mirroring Smalltalk's `nil`, which keeps the raw Python `object` at the root out of reach.

A class is an object answering this class side. `int.name()` answers `int` and `int.superclass()` answers `object`. `obj.is_instance(T)` takes the class itself. `Foo.is_instance(Object)` is `false`, since a class is an instance of its metaclass and not of its bases; `Foo.is_subclass(Object)` is the "descends from" question.

The class side refuses:

- An instance message. `PoopMeta.__getattribute__` refuses a plain `FunctionType` found on the class's own MRO with `#upper asks an instance; send it to one`. It is narrow on purpose, because `staticmethod.__get__` answers the wrapped function and would otherwise look identical. `get_attr` / `has_attr` read past the refusal through `_reflected`, because asking a class for a method by name is reflection.
- `Foo.class_()` and `Foo.class_name()`, which name `#name` instead.
- Rebinding. The descriptor owns assignment and deletion: `Foo.name = 5` and `Foo.set_attr("name", 5)` answer `#name is answered by every class — it cannot be rebound`, and `__delete__` refuses with the same sentence through one `_rebound`.

`PoopMeta.__dir__` merges the `class_side` descriptors found on `type(cls).__mro__`, nearest metaclass first, so `raise_` is listed for a mirror and not for a plain class. It leaves out a refusing descriptor (marked by the `class_side_refusal` flag), the instance-only messages, and `class_` and `class_name`, and dedupes the result. The merge lives in `__dir__` rather than in the `dir` message because `:methods`, the REPL completer and the near-miss hint all call Python's `dir`.

The class side words `del_attr`, `format` and `print` through the helpers their instance twins use (`text_like`, `_template_refusal`, `a_text`).

`Foo new` is not provided. `Foo()` already builds an instance and is not forbidden, so a `new` message would be Smalltalk parity rather than a substitute for anything.

## Consequences

- Instances are unaffected: instance lookup never consults the metaclass, so `Foo().print()` still finds `Object.print`.
- Every ban that names a substitute names one the class also answers.
- `:methods str` describes one receiver instead of two, and every name `str.dir()` lists can be read off the class without a refusal. `print` is dropped by the instance-only filter and restored by the merge, because it is both a plain method on `Object` and a `class_side` message.
- `Boolean` has no instance of its own to protect (its `__new__` answers `false`), so its protocol methods are plain ones that raise `NotImplementedError`.
- A wrong-arity call on the class side names the class (ADR 45).
- The wording sweep samples a class as a receiver.
- `tests/test_cloak.py`'s sweep for public `property` objects does not reach the class-side descriptors, which live on the metaclass.
