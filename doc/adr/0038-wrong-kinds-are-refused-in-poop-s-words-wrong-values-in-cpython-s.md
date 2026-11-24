# 38. Wrong kinds are refused in POOP's words, wrong values in CPython's

Date: 2026-07-17

## Status

Accepted

## Context

A wrapper holds its Python payload in an internal slot such as `_value`. A method that unwrapped a mandatory argument inline as `arg._value` failed when handed a POOP value that carries no `_value`, such as a `List`, `Set`, `Dict` or `Tuple` passed where a `Str`, `Bytes` or `Int` was expected. `arg._value` routed through `does_not_understand` and answered `list does not understand #_value`, exposing the internal slot name. Operators did the same: `Str.__add__`, `Bytes.__add__` and `ByteArray.__add__` read `other._value`, so `("a" + [1])` answered `list does not understand #_value`. `startswith` / `endswith` read `._items` off a non-`Tuple` affix.

The first fix was the faithful-unwrap idiom, which hands a foreign argument to the underlying Python call raw so that CPython raises its own `TypeError`. That stopped the internal name leaking, but a wrong type then answered in CPython's terms. For a type refusal those terms often name something POOP forbids: a `translate` table that is not a mapping answered `'int' object is not subscriptable`, the protocol `no_subscript` bans. CPython's sentences for a wrong value of the right type, on the other hand, often name nothing POOP forbids: `the first two maketrans arguments must have equal length`, `string keys in translatetable must be of length 1`, `character mapping must return integer, None or str`, `Format string contains positional fields`, and `bytearray.take_bytes`'s `can't take 5 bytes outside size 2`.

## Decision

POOP refuses a wrong kind of argument in its own words and leaves a wrong value of the right kind to CPython's sentence, unless that sentence names a construct POOP forbids.

- A method never reads an internal slot off an argument it has not checked. `_faithful(arg)` in `poop/types/_raw.py` (a thin `getattr(arg, "_value", arg)` in a leaf module, so the guards in `_argument.py` can import it) and its optional-argument twin `_unwrap(arg, default)` are the only unwrapping idioms.
- The type of an argument is checked by a guard that words the refusal as a message: `a_mapping` and `translation_table` answer `#translate expects a mapping or a sequence, got an int`; `an_int` answers `#take_bytes's n must be an int, got a str` and `#resize's size must be an int, got a str`; `"abc".count([1])` answers `#count expects a str, got a list`.
- An operator handed a foreign operand guards it and answers `NotImplemented`, so the refusal reads as every other operator's does. The byte-like guards admit either wrapper, since CPython concatenates `bytes + bytearray` both ways; the four ordering dunders on `Bytes` and `ByteArray` take the same `Bytes | ByteArray` operand their `__add__` does.
- A value refusal whose CPython sentence names nothing POOP forbids passes through unchanged: `take_bytes`'s `IndexError` and `resize`'s `Can only resize to positive sizes, got -1` are not reworded.

## Consequences

- No refusal names an internal slot, for any argument on any receiver.
- The same sentence reads the same on every receiver that takes the same kind of argument.
- `startswith` / `endswith` on `Str`, `Bytes` and `ByteArray` share `affix_needle` (`poop/types/_affix.py`). `Int.min` / `Int.max` / `Float.min` / `Float.max` delegate to `builtins.min` / `max` over the operands themselves, which also made `(1).min(True)` answer 1, since `bool` is an `int` subclass.
- `Int` / `Float` / `Complex` arithmetic already routed foreign operands to `NotImplemented` (via `_num_value` / `_integral_value` / `_coerce`) and needed no change.
- A mixed `bytes` / `bytearray` `sorted` works, and a foreign operand is still refused.
