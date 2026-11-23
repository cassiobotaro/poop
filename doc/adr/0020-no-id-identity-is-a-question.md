# 20. No `id`: identity is a question

Date: 2026-04-22

## Status

Accepted

## Context

`id(x)` is a free function with a procedural look, and it hands out an address POOP has no business handing out. `Object` once answered an `id` message with `id(self)`, CPython's address, the raw pointer POOP otherwise never admits exists. That answer was leaky and also wrong: CPython recycles addresses, so an object created after another was collected claims the same identity, which is not a behaviour Smalltalk's `identityHash` has. It also collapsed onto `hash` for anything that does not hash by value, since `__hash__` returned the same number: two distinct messages, one answer, and that answer an address.

The alternative was a POOP-owned identity. It would need an `_identity` slot on `Object`, a pointer on every object in a language where every integer is one, to buy a message whose only power over `is_identical` is keying a `Dict` by identity, which no example asks for.

## Decision

POOP has no `id`, neither as a builtin nor as a message. `no_id` (`poop/validators/no_id.py`) refuses `id(x)` and names `a.is_identical(b)` as the substitute, which answers the identity question without materialising a number.

`hash` stays, because `Dict` and `Set` key on `__hash__` and value types must hash by value for them to work at all. `Object.__hash__` answers Python's own identity hash rather than the address verbatim.

## Consequences

A program can ask whether two references are the same object, and cannot obtain a number for an object's identity. Keying a `Dict` by identity is the one thing given up.
