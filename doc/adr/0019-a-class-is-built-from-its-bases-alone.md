# 19. A class is built from its bases alone

Date: 2026-04-22

## Status

Accepted

## Context

A `class` statement can carry more than its bases, and the extra parts reached CPython's class-creation machinery without a validator reading them. Nothing read `ClassDef.keywords`. `metaclass=type` happened to be refused, because `no_type` bans the name, and every other keyword reached `type.__new__`, answering CPython's sentences: `X.__init_subclass__() takes no keyword arguments`, `metaclass conflict: …`.

PEP 695 type parameters went unvalidated and answered two different leaks. `class X[T]:` reached CPython's generic-class intrinsic, which imports `typing` through a builtin the allow-list withholds, and died with an internal `KeyError: '__import__'`. `def m[T](self): return T` handed the program a raw `typing.TypeVar`, answering `'typing.TypeVar' object has no attribute 'print'`. Both are the naked-native symptom the allow-list exists to end. A `type X = int` alias creates an alias for a Python builtin type, which is incompatible with POOP's runtime types. The `2026-10-15-close-raw-python-leaks` change closed the keyword and type-parameter doors.

## Decision

A POOP class is built from its bases alone.

- `no_class_keyword` (`poop/validators/no_class_keyword.py`) refuses every `ast.keyword` on an `ast.ClassDef`: `class X(foo=1)`, `class X(metaclass=M)`, `class X(**opts)`. It reports one error per keyword, at the keyword's position, and its sentence names the keyword as written.
- `no_type_alias` (`poop/validators/no_type_alias.py`) refuses `type X = int` and every PEP 695 type parameter (`class X[T]`, `def m[T](self)`, `type X[T] = …`), because POOP has no static types. The sentence names the parameter as the program wrote it: `drop the [T]`, `[*Ts]`, `[**P]`.

## Consequences

A program that meant to configure a subclass sees the keyword to remove. What it wanted is a class-side message on the parent, which `PoopMeta` already answers. The class-creation dunders a class body could define instead are refused by ADR 17.
