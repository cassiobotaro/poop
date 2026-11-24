# 46. Text codecs are limited to four encodings, constructors included

Date: 2026-07-27

## Status

Accepted

## Context

`encode` and `decode` handed the codec name straight to CPython, so `"a".encode("rot13")` answered `'rot13' is not a text encoding; use codecs.encode() to handle arbitrary codecs`. No POOP program can follow that advice, since `import` is forbidden and `_ALLOWED_BUILTINS` has no route to a module. The `errors=` argument was a second way in, since `namereplace` and `backslashreplace` are the same codec machinery reached under another name. The table lookup lowercases what it is handed, so a non-text encoding answered `'int' object has no attribute 'lower'`, the wrapper naming the Python method it happens to call, and a non-text handler was reported as an unknown value (`unknown error handler 1`) rather than a wrong kind.

The converters went around the guard. `bytes(text, encoding)` in `poop/transformers/bytes.py` reached into `_value` and called `str.encode` itself, so `bytes("ab", "rot13")` answered the sentence `_codec.py`'s docstring quotes as the reason it exists, pointing at a module `no_import` forbids. Three other choices came with that path. The encoding was optional and invented (`bytes("ab")` was `b'ab'`, utf-8 chosen on the program's behalf). A wrong-typed encoding was ignored (`bytes("ab", 5)` fell back to utf-8). The failure was CPython's (`'ascii' codec can't encode character…`), under a class no program can spell. `ByteArray` mirrors `Bytes` message for message, and `bytearray("ab")` fell through the `Iterable` branch to answer `'str' object cannot be interpreted as an integer`, a message about integers for an argument that is text. The decoding half already went through the guard.

`encode` and `decode` can fail on the text they are given, which raises the question of the `Unicode*` exception family. Mirroring those classes would have meant reproducing a five-argument constructor whose `__str__` composes the `codec` sentence `_codec.py` exists to keep out. Left unmirrored and unreworded, `poop_class_of` answered the nearest mirrored ancestor, so a handler was told `ValueError` while the uncaught report printed `UnicodeEncodeError`, one failure under two names.

## Decision

`poop/types/_codec.py` is the one place an encoding or an error handler is accepted, and every text and byte message and converter goes through it.

- It accepts four text encodings, `utf-8`, `utf-16`, `latin-1` and `ascii`, plus the spellings a reader would reasonably type (`utf8`, `latin1`, `iso-8859-1`, `us-ascii`), case-insensitively. It accepts the three codec-independent error handlers, `strict`, `ignore` and `replace`.
- Anything else is refused with `unknown encoding 'rot13' — POOP encodes utf-8, utf-16, latin-1 and ascii`.
- Both arguments pass `_argument.text_like`, narrowed to `str` alone (`kinds=(str,)`), before the table is read.
- An encode or decode failure is reworded as a `ValueError`, which is what `UnicodeError` is in CPython's tree: `ascii cannot encode 'é' at position 1`, `utf-8 cannot decode byte 0xff at position 0`. POOP does not mirror the `Unicode*` classes.
- The text branch of the `bytes` converter delegates to `Str.encode` and requires the encoding, as CPython does. `ByteArray` has the same two- and three-argument form (`poop/transformers/byte_array.py`).

## Consequences

This applies to codecs the argument `poop/types/exceptions.py` already makes: a language with no I/O and no codecs cannot reach the `OSError` subtree or the `Unicode*` family. A codec failure has one class a program can spell, and the handler and the uncaught report agree on it.

Accepting `b"utf-8"` as an encoding would only move the refusal one branch down, so bytes are refused as a wrong kind. The same narrowing fixes `byte_order`, where `b"big"` used to reach the `ValueError` branch.

A constructor can no longer choose an encoding for the program or ignore a wrong one: `bytes("ab")` and `bytes("ab", 5)` are refused where they used to answer utf-8 bytes.
