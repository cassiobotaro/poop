# 31. `Object` is the implicit base of every class

Date: 2026-05-12

## Status

Accepted

## Context

Python 3 makes every class implicitly inherit from `object`. POOP's `Object` holds the methods every POOP object answers, and a user-defined class written without a base would not reach them. A rewrite that names `Object` needs a binding the rewritten AST can resolve, and every POOP-internal binding lives under a mangled `_poop_*` name user code cannot reach.

## Decision

The class transformer (`poop/transformers/class_.py`) injects POOP `Object` as the base class of every user-defined class that has no explicit base, mirroring Python 3's implicit `object`. An explicit root spelling resolves to the same class:

- `class Foo:` becomes `class Foo(_poop_object):`;
- `class Foo(object):` becomes `class Foo(_poop_object):`;
- `class Foo(Object):` becomes `class Foo(_poop_object):`, kept for explicit Smalltalk-style declarations;
- `class Foo(Bar):` is unchanged, since it already has a base.

`Object` is injected into `DEFAULT_NAMESPACE` as `_poop_object`, so the rewritten AST resolves it at run time. The mangled name is reserved by `no_poop_prefix`.

## Consequences

- User-defined classes gain every `Object` method without declaring it: `print()`, `is_none()`, `not_none()`, `assert_()`, `class_name()`, `get_attr()`, and the rest.
- `object` and `Object` are two spellings of the same root class.
