# 29. Void mutators answer `none`

Date: 2026-05-05

## Status

Accepted

## Context

Many POOP methods mirror Python methods that return `None`, such as `list.append`, `set.add`, `dict.update` and `bytearray.reverse`. Such a mutator could answer either `none` or `self`. A Python programmer expects `result = lst.append(x)` to leave `result` as `None`.

## Decision

A mutator named after a Python method that returns `None` answers POOP `none`, not `self`.

POOP-specific methods with no Python equivalent, such as `Dict.at_put`, `ByteArray.at_put` and `List.at_put`, may answer `self` for chaining.

## Consequences

- The Python mirror contract holds: `result = lst.append(x)` leaves `result` as `none`.
- Mutators that mirror Python cannot be chained; the POOP-only mutators can.
