# 33. Dunder access is banned by rule, at runtime too; `__init__` only on a `super()` receiver

Date: 2026-07-15

## Status

Accepted

## Context

Dunder attributes reopened what other bans close. `vars(obj)` is banned, but `obj.__dict__` *is* `vars(obj)`, and the attribute spelling reached a raw CPython `dict` at run time. `x.__class__`, `A.__mro__` and `A.__bases__` reconstruct the `type(x)` that `no_type` bans, and `x.__class__.__name__` answers a raw `str`.

- A list of names was rejected. The obvious four (`__dict__`, `__class__`, `__mro__`, `__bases__`) were already incomplete before the ban was written, since nobody had listed `__name__`. Enumerating invites the next omission.
- Raw dunder calls are included. CPython forces `__len__` to answer a real `int` and coerces `__contains__` to a real `bool`, so those two can never honour "no naked Python primitive ever reaches runtime". `__abs__` already answers a POOP `Int`, but sparing it would restore the exception list the rule exists to avoid, and `.abs()` costs nothing.
- `super().__init__(...)` is an `ast.Attribute` with a dunder attribute, and `super` is allowed, because without it inheritance breaks and there is no message-passing substitute. A carve-out on the name alone applied to every receiver, so `s.__init__("zap")` re-ran the constructor on a live value and `"abc"` printed as `zap`. `Str`, `Int` and `Tuple` were all mutable that way, and a `Dict` keyed on one was left holding an entry reachable under neither spelling.
- `no_getattr` offers `get_attr` / `has_attr` / `set_attr` / `del_attr` as its substitute, so `get_attr("__dict__")` reopened what the validator closes, and `get_attr("__dict" + "__")` puts the spelling beyond any static validator. Sharing the syntax's carve-out, `s.get_attr("__init__")("ZAP")` re-initialized a live `Str` in place.
- The metaclass carried undotted twins. When `PoopMeta` derived from `ABCMeta`, `Foo.mro()` answered the same raw list as `.__mro__`, holding the Python `object` that `superclass` stops short of, under a spelling no validator reading `ast.Attribute` can see. `Foo.register(Bar)` made `is_instance` answer true for a class that never inherited from the receiver.
- Bare dunder names leaked too: `__builtins__.clear()` used to run clean through every validator and corrupt the interpreter; `__loader__` and `__spec__` are naked Python natives and an import surface `no_import` bans; `__name__`, `__package__` and `__debug__` are raw Python values.

## Decision

Dunder access is banned by rule, statically and at run time, with one message:

- `no_dunder_attribute` (`poop/validators/no_dunder_attribute.py`) rejects any `__dunder__` in `ast.Attribute` position. Where a substitute exists the sentence names it (`.__class__` → `obj.class_()`, `.__name__` → `Klass.name()`, `.__mro__` / `.__bases__` → `Klass.superclass()`, `.__len__()` → `obj.len()`, `.__contains__(x)` → `col.includes(x)`, `.__abs__()` → `n.abs()`, `.__hash__()` → `obj.hash()`). `.__dict__` has none. The ban is the decision. Anything else names its scope (`dunder globals`, `dunder class attributes`, `dunder locals`).
- `__init__` is carved out for the syntax only, on a `super()` receiver, checked by `_is_super_call(node.value)`.
- `no_dunder_name` (`poop/validators/no_dunder_name.py`) is the `ast.Name` half: any `__dunder__` spelled as a bare name, load or store. It has no `__init__` carve-out, because a bare `__init__` name has no `super()` use.
- `_reject_dunder` (`poop/types/_attr_guard.py`) guards the four attribute accessors at run time with `dunder_message(name, allow_init=False)`, so `get_attr("__init__")` answers `__init__ is forbidden — use Klass(...) instead`. A forbidden name is refused before a `get_attr` default is consulted.
- The three sites read the same `dunder_message`; the bare-name validator passes `dotted=False`, so a bare name is not reported as an attribute the program never wrote.
- On the class side, `mro` and `register` stopped answering. `mro` refuses only once the class has a `__mro__`, because CPython calls the metaclass's `mro` to compute a new class's MRO and an outright ban breaks every `class` statement. `register` left with `ABCMeta`.

## Consequences

- A new dunder needs no new entry; the rule covers it.
- The static and runtime halves cannot drift, since both read `dunder_message`.
- The executor supplies its own `__builtins__`, so the bare name no longer names CPython's whole namespace. `no_dunder_name` stays because it is the half that teaches. It refuses the program before it runs and names the ban, rather than answering `dict does not understand #clear` at run time.
- `Foo.register(Bar)` is now an ordinary message not understood, and "is a" cannot move into a side table no reader of the class can see.
- Raw dunder access is the opposite call to chained comparison (ADR 27). Both have a substitute, but a dunder also leaks a raw Python primitive.
