# 3. Every basic type has a POOP wrapper

Date: 2026-04-21

## Status

Accepted

## Context

A Python program works with the builtin types (`int`, `str`, `list`, and the rest), and those types answer Python's methods, not POOP's messages. Python native types must not leak into POOP code.

## Decision

Every basic Python type has a POOP equivalent:

- `int` → `Int`, `float` → `Float`, `complex` → `Complex`
- `str` → `Str`, `bytes` → `Bytes`, `bytearray` → `ByteArray`, `memoryview` → `MemoryView`
- `bool` → `Boolean`, `NoneType` → `NoneClass`, `ellipsis` → `EllipsisClass`
- `list` → `List`, `tuple` → `Tuple`, `set` → `Set`, `frozenset` → `FrozenSet`
- `dict` → `Dict`, `frozendict` → `FrozenDict`
- `sentinel` → `Sentinel`

## Consequences

- ADR 2 rewrites each literal into one of these wrappers, so a program never holds the native value.
- A new basic type in Python needs a new wrapper before POOP can admit it.
