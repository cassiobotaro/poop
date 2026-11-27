# Design

## Context

See proposal.md, *Why*. The decision that the registries are immutable, and
that the interpreter holds an immutable copy, is recorded in the new ADR
(task 1.1). This document keeps only what is specific to the change.

`_merge_bindings` builds `DEFAULT_NAMESPACE` as a `dict` and cloaks the
helpers in it. `RESERVED_NAMES` is already a `frozenset`, which makes it the
model for this change.

## Goals / Non-Goals

**Goals:**
- No caller can change what a later `Interpreter()` starts from, or what an
  existing interpreter validates and transforms with.

**Non-Goals:**
- Making `Interpreter` itself frozen. Its attributes are private, and the
  change is about what it hands out.

## Decisions

1. **`MappingProxyType` over a frozen `dict` subclass or `frozendict`.**
   The proxy is the stdlib's read-only view and needs no new type. Python
   3.15's builtin `frozendict` is the type POOP wraps for programs, and the
   interpreter's own namespace would then be one more value a reader could
   confuse with the language's. `dict(proxy)`, which `new_namespace()`
   already calls, gives a plain `dict` back for `exec`.
2. **`Interpreter` stores `tuple(...)` of what it is given.** The defensive
   copy stays, now as the conversion to the immutable type, so a caller's
   list passed as `validators=` can change later without changing the
   interpreter. The comment that explains the copy changes to say this.
3. **The parameters widen to `Sequence` and `Mapping`.** Every caller passes
   a list or a dict, which still type-checks, and the defaults are now a
   tuple and a proxy.

## Risks / Trade-offs

- **[`ty` rejects a `Mapping` where `dict` was annotated]** → `self._namespace`
  is read only by `new_namespace()`, which copies it. Task 2.2 runs `ty` on
  both `poop/` and `tests/` before the commit.
- **[A `tuple` annotation hides a `list` default somewhere]** → Task 2.1
  checks with `git grep` that no `DEFAULT_*: list` or `dict[str, object] =
  _merge_bindings` annotation is left.
