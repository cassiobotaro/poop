# 36. `does_not_understand` answers with layered hints

Date: 2026-07-15

## Status

Accepted

## Context

An unknown message in Python answers `'int' object has no attribute 'frobnicate'`, which names neither a message nor what to write instead. Smalltalk answers `doesNotUnderstand:`, and a programmer arriving from either language brings selectors POOP spells differently.

String similarity cannot do all the work. It cannot map `size` to `len`, because the two share no letters. The first Smalltalk table stopped at seventeen rows, the ones whose twin POOP spells as a single name, so the most common collection selectors fell through to difflib: `[1].first()` answered `try :methods`. The lazy views answer the consuming messages and not the sequence ones, so `xs.map(f).len()` answered `try :methods`, which is true and useless.

Python 3.15's `AttributeError` carries a table of names programmers bring from JavaScript, Java, Ruby and C# (`traceback._CROSS_LANGUAGE_HINTS`): `[1].push(4)` answers `Did you mean '.append'?`. POOP never saw it, because the wrapper's `__getattr__` routes to `explain` before CPython composes anything, so every one of those answered `try :methods`. CPython keeps that table private. Two of its rows name constructs POOP forbids: `put` → `Use d[k] = v.` and `contains` → `Use 'x in list'.`. Python 3.15 also looks one level in (`Did you mean '.inner.area' instead of '.area'?`).

## Decision

An unknown message answers `MessageNotUnderstood`, naming the receiver's class and the selector, and adds the best hint it has. The layers are consulted in this order:

1. The Smalltalk table (`poop/types/_selectors.py`). A row is either a message (`#isEmpty is #len here`, shown only when the receiver has it) or a `(spelling, needs)` pair shown as written when the receiver answers `needs` (`#first is .at(0) here`, `#detectIfNone is .find(lambda item: …, default=…) here`), or always, for the loop selectors whose twin is a `range` (`#timesRepeat is range(n).do(lambda item: …) here`). A row per lazy view and sequence message (`len`, `at`, `reversed`, `includes`, `count`, `index`) says `a map is lazy; materialize it with list(...) first`.
2. The foreign table, `CROSS_LANGUAGE_HINTS`, copied from CPython's, keyed by selector and receiver and matched through the MRO as CPython's `isinstance` is, so a program's `class Stack(list)` gets the list rows. The `put` and `contains` rows say `#at_put` and `#includes`. The float rows (`__or__` and its siblings) are left out, since a dunder never reaches the hook. `add` on a list is the Smalltalk row's `#append`, consulted ahead of CPython's `use a set?`.
3. A close match for a typo (`did you mean #upper?`).
4. One level in: when no table and no near-miss answers, `explain` asks whether one of the receiver's attributes answers the selector and says `did you mean #inner.area?`. CPython's bounds are kept (twenty attributes, one level), and so is its rule that nothing runs while composing the hint: a descriptor on the class is skipped and the inner object is asked statically. A `__slots__` member is read anyway, because reading it runs no code and every POOP class declares its state that way.
5. Otherwise, a pointer at `:methods`.

Overriding `does_not_understand(name)` answers an unknown message instead of refusing it. The override answers a callable, which is the only way to reach the arguments, since attribute lookup runs before the call.

Three implementation constraints hold:

- `MessageNotUnderstood` inherits `AttributeError`, because `hasattr` and three-argument `getattr` swallow that and nothing else; `Object.has_attr` and `get_attr(name, default)` depend on it.
- Dunder names never reach the hook, since Python probes any object for `__copy__`, `__getstate__` and friends, and a proxy would otherwise answer those probes.
- `__getattr__` is hidden behind `if not TYPE_CHECKING`, because a visible one answers `Any` for every name.

## Consequences

- The tables carry vocabulary, and what is left for similarity is typos.
- Every Smalltalk and foreign row is tested to name a message the receiver answers.
- The hook is the metaobject protocol that makes real proxies possible.
- Statically an unknown message is still an error, so `ty` keeps catching typos across the codebase; the hook changes what happens when one is sent, not what is knowable before.
- The foreign table is copied rather than imported, because CPython keeps it private.
