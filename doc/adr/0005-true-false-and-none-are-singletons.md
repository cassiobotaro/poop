# 5. `true`, `false` and `none` are singletons

Date: 2026-04-21

## Status

Accepted

## Context

POOP's comparisons and identity checks need exactly one `true`, one `false` and one `none`. A program can still reach their constructors. `class_()` hands each class out, and a class is callable.

Before this rule held for constructors, `None.class_()()` printed `None` and was neither identical nor equal to `None`, and calling the `Boolean` base answered CPython's abstract-class sentence naming a dozen dunders and private methods.

## Decision

`true`, `false` and `none` are unique objects. There is exactly one instance of each, and no constructor builds a second one. `NoneClass`, `EllipsisClass` and both boolean classes answer their existing instance from `__new__`, as CPython's `type(None)() is None` and `type(...)() is ...` do. The `Boolean` base answers `false`, as `bool()` does.

## Consequences

- All comparisons and identity checks can rely on the guarantee.
- Calling the class a singleton answers gives back that singleton, never a lookalike and never CPython's abstract-class refusal.
