# 18. Class machinery is accepted only where it was argued for

Date: 2026-04-22

## Status

Accepted

## Context

Four pieces of class-definition machinery have no message-passing substitute. `super()` is the standard way to delegate to a parent method in both Python and Smalltalk; without it, subclasses cannot extend parent behaviour and inheritance breaks. `property`, `classmethod` and `staticmethod` are class-definition decorators, not runtime operations on values: they define how a method is bound, not what it does, and blocking them would prevent idiomatic class definitions with no POOP substitute. The allowance for the three decorators rested on a distinction: a bare decorator is definition, a called one is a runtime operation.

Nothing checked the boundary of that allowance. `@` applies an arbitrary expression, which is a function call written as syntax rather than sent as a message, the shape `no_subscript`, `no_fstring` and `no_if` exist to remove. `@twice` on `def bar(): return 1` made `Foo.bar()` answer `2`, a method silently replaced by an unrelated block. Outside the `@` position the four names were reachable as plain names and answered Python rather than POOP:

    property.print()   ->  AttributeError: type object 'property' has no attribute 'print'
    super.print()      ->  AttributeError: type object 'super' has no attribute 'print'

which is the naked-native symptom the builtins allow-list was introduced to end. `p = property` and `property(getter)` both passed.

Two positions failed inside CPython. `(lambda: super().m())()` inside a method, the shape POOP pushes a reader towards, has no `__class__` cell to read, since a lambda owns none, and CPython answered a `RuntimeError` at run time about a cell the block cannot be given. `return 5` directly in `__init__` answered `TypeError: __init__() should return None, not 'int'`; the return transformer skips `__init__` because CPython checks that slot itself, so nothing else looked at it.

## Decision

`super`, `property`, `classmethod` and `staticmethod` are allowed, each only in the position its allowance was argued for. Two validators enforce the boundary.

- `no_decorator` (`poop/validators/no_decorator.py`) owns the `@` position. A `decorator_list` entry on a function or class is accepted only as a bare `ast.Name` among `staticmethod`, `classmethod` and `property`. `@property(...)`, `@a.b` and `@twice` are refused; `@property` is not.
- `no_class_machinery` (`poop/validators/no_class_machinery.py`) owns every other position. The three decorator names are refused outside a `decorator_list`, so `property(getter)` is refused for the reason `@property(...)` is. `super` keeps the call position instead, because a call is what its allowance is for: a bare `super` is refused (`super().method(...)`), and so is `super()` whose nearest enclosing function is a `lambda`. A `return` with a value directly in an `__init__` body is refused, since `__init__` builds the receiver and answers nothing.

The validator reads the enclosing functions off a stack to find the `lambda` case.

## Consequences

One distinction applies in both positions, so the allowance documented for the decorators is enforced rather than merely documented. A program that needs a parent's answer inside a block sends `super()` from the method and hands the block its answer. Of the six names `_ALLOWED_BUILTINS` admits, the two dunders (`__build_class__`, `__name__`) are already refused as a bare `ast.Name` by `no_dunder_name`, so all six now have a guard outside their argued position.
