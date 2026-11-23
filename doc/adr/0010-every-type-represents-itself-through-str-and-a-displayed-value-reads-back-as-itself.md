# 10. Every type represents itself through `__str__`, and a displayed value reads back as itself

Date: 2026-04-22

## Status

Accepted

## Context

Every printed message goes through some representation of the object, and a program has two ways to see one: printing it, and seeing it inside a container's displayed form.

`List`, `Tuple` and `Dict` build their displayed form from `repr` of each element. `Slice` (`poop/types/slice.py`) takes its components as they are, since `slice` accepts any object and the sequence being sliced resolves each one, and it displayed them with `str`. So `slice(None, "a", None)` printed `slice(None, a, None)`, whose stop is the name `a`, and `slice(None, "", None)` printed `slice(None, , None)`, which is not source at all. `Slice` was the one container that did not use `repr`, and the difference only showed on a non-`Int` component, where the two spellings differ.

## Decision

All POOP types implement `__str__`, and `Object`'s `__repr__` delegates to it. `Object.print` calls `str(obj)` internally, so every printed message goes through the type's own representation.

A displayed value reads back as itself: a composite value builds its displayed form from `repr` of each component, as `List`, `Tuple`, `Dict` and now `Slice` do.

## Consequences

- A new composite type builds its displayed form from `repr` of its components.
- `slice(None, "a", None)` prints `slice(None, 'a', None)`, which is source for the same value.
