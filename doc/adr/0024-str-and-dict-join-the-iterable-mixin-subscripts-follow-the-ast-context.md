# 24. `Str` and `Dict` join the iterable mixin; subscripts follow the AST context

Date: 2026-04-22

## Status

Accepted

## Context

`no_map`, `no_filter`, `no_all`, `no_any`, `no_sum`, `no_loops`, `no_sorted`, `no_reversed` and `no_subscript` each name a message on the receiver as the substitute for the construct they ban. ADR 9 activates a validator only when its substitute exists, and several of these messages were missing, or meant something else, on some receivers:

- `Str` and `Dict` were the two receivers `_IterableMixin` did not reach. A string is the most-written receiver in the language, and iterating one meant driving the cursor by hand (`(lambda: it.has_next()).while_true(...)`) because `for` is banned.
- `Dict.do` answered `Tuple(key, value)` pairs, while `map`, `filter`, `sorted`, `min`, `max` and `iter` on the same receiver answered keys. One receiver gave two answers to "what is an element of a `dict`". The odd one out was the message `no_loops` names as the substitute for `for k in d`, which walks the keys in Python. `d.do(lambda k: k.upper())` answered `tuple does not understand #upper` while `d.map(lambda k: k.upper())` worked.
- `sorted` existed on `List` and `Tuple` only, while CPython's `sorted` takes any iterable, so `{2, 1}.sorted()`, `"ba".sorted()`, `range(3).sorted()`, `b"ba".sorted()`, `{"b": 1}.sorted()` and `d.keys().sorted()` were all banned with nowhere to go. The need is sharpest on a `Set`, the one receiver whose own iteration order a program must not rely on.
- `Str.reversed` answered a `List` of one-character `Str`s, the single message on a string that changed the type, so `s.reversed().upper()` failed where every other chain composes. `Bytes`, `ByteArray`, `MemoryView` and `Dict` answered no `reversed` at all. On `ByteArray` the hint pointed at the in-place `reverse`, a mutation offered as the substitute for a reversal that copies, and immutable `Bytes` had nothing.
- `no_subscript` named a reader whatever the program was doing, so `xs[0] = 9` and `d["a"] = 1` were answered with "use obj.at(key) instead", which sends a program that was trying to store to a value or a `KeyError`. `Dict` and `ByteArray` answered `at_put` and `List` did not, so the validator refused a list store with no substitute to name.
- `List.at` alone also took a `Slice`: `[1, 2, 3].at(slice(0, 2))` answered `[1, 2]`, while the same message on a tuple, a range and a str answered `tuple.at expects an int index, got a slice`. One message meant two things on four siblings.

## Decision

The substitute a ban names answers on every receiver the ban reaches, with that receiver's meaning:

- `Str` and `Dict` inherit `_IterableMixin` (`poop/types/_iterable_mixin.py`) and override the collisions.
  - `Str` keeps `find`, `count` and `index` with their string meaning, a search for a substring. Handed a block, all three answer `str's #find searches for a substring — it takes the text to look for, not a block`, where CPython said `find() argument 1 must be str, not function`. `Bytes` and `ByteArray` answer the same sentence with their own name and `subsequence` (`bytes's #count searches for a subsequence — it takes what to look for, not a block`), from `a_needle` in `poop/types/_argument.py`, which reads the name off the receiver. `Str.sum` is refused. `sum("ab")` is a `TypeError` in CPython, and adding the characters up would answer the string back, which is `join`'s job.
  - `Dict`'s mixin messages, `do` included, iterate the keys, as CPython does, so `d.map(block)` matches `map(f, d)`. `d.items().do(...)` and `d.items().map(...)` are the pair spellings. `Dict`'s own `do`, `enumerate` and `zip` are gone in favour of the mixin's, and the mixin's `do` brings its mutation guard.
- `sorted` lives on `_IterableMixin` and answers a `List`, as CPython's `sorted` always answers a `list`. `Tuple` alone overrides it to answer a `Tuple`, because a tuple can hold an order. All accept `key` and `reverse`.
- Every receiver answers `reversed` with its own kind: `List`, `Tuple`, `Range`, `Str`, `Bytes`, `ByteArray` and `MemoryView` each answer their own type. The dict views answer their reverse iterators, and `Dict` answers a `DictReverseKeyIterator` by delegating to `self.keys().reversed()`, which is what `reversed(d)` yields in CPython.
- `no_subscript` reads the context on the node. Under `ast.Load` the substitute is `obj.at(key)`, or `obj.slice(start, stop)` for a slice. Under `ast.Store`, which also covers `xs[0] += 1`, it is `obj.at_put(key, value)`. `List.at_put` exists.
- `at` reads one element on every receiver. `List.at` refuses a slice as its siblings do; `slice` is the substitute for `obj[1:3]` on all four.

## Consequences

- Iterating a string or a dict is a message on it, and every message on a `Dict` agrees that its elements are its keys.
- Messages chain on a reversed string: `s.reversed().upper()` works, and `list(s.reversed())` is the spelling for anyone who wants the characters. `"abc".slice(...)` and `"abc".at(0)` also answer a `Str`.
- `Bytes` and `ByteArray` keep their own `find` for subsequence search, a different meaning from the mixin's element-finding `find`.
- A slice write has no whole-slice substitute. Its refusal names `obj.at_put(index, value)`, one element at a time, rather than `slice`, which only reads.
