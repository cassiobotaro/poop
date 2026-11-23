# 45. Arity refusals keep CPython's sentence and name POOP's class

Date: 2026-07-27

## Status

Accepted

## Context

A wrong-arity call has three possible wordings in POOP: CPython's own sentence with the callee renamed by `cloak` (ADR 14), a block's sentence, and a sentence POOP writes for a particular message.

For a block literal, CPython reported the failure against the raw lambda, `<lambda>() takes 1 positional argument but 2 were given`, naming the Python class POOP cloaks as `function` and prints as `<block>`, in a calling convention a block does not have. Blocks are POOP's only control flow, so this is one of the most-read messages in the language.

For a message, CPython names the class that defines the method: `object` for one inherited from `object`, `list` for `class Stack(list)`'s `append`, `bytearray` and `frozendict` for their own, and the class a class-side method is read off (`int.mro(1)` names `int`). `cloak` froze the definer's name, which was right only where POOP's definer is one CPython would name. The `2026-10-19-arity-names-the-receiver` change found four shapes where it was not: the shared mixins are cloaked as `object`, so `[1].map(1, 2)` blamed `object.map()`, a class that does not answer `#map`; `ByteArray` reuses `Bytes`'s functions and `FrozenDict` `Dict`'s, so they blamed `bytes.lower()` and `dict.keys()`; and one class-side function serves every class, so `int.hash(1)` blamed a bare `hash()`. A caught error blamed `object` too (`e.message(1)` answered `object.message() takes …`), because `Error` is cloaked as `object`. The wording sweep had exempted the arity shape wholesale and never read the name inside it. Renaming at definition is impossible for a definer shared by several receivers.

Some messages already worded their own refusal. The `2026-10-19-arity-refusals-teach` change found that they split in two: the ones that teach (`#map expects a block, got nothing — write .map(lambda item: …)`), and `raise_`'s `#raise_ takes no argument once the exception is built`, which existed only because CPython's sentence named `Exception.raise_()` or `object.raise_()`. Meanwhile the branch family, POOP's substitutes for `if`, `and`/`or` and `while`, had no default for its blocks and answered `bool.if_true() missing 1 required positional argument: 'block'`.

## Decision

An arity refusal is CPython's sentence with the right class named in it. POOP rewords an arity refusal only when it has a hint to give.

- `_MethodBlock.__call__` (`poop/types/block.py`) renames the callee at the call, where the receiver is in hand, and only for a binding failure: one whose traceback has no frame below the call. A `TypeError` a method body raises passes through whatever it says. The rewritten sentence is raised as a mirror `TypeError` from `None`.
- A class receiver is named by its own name (`int.hash()`, `Foo.print()`). For an instance, a message `Object` itself defines keeps `object` (`object.repr()`), a program's own class keeps its name, and otherwise the nearest wrapper in the receiver's MRO is named (`list.map()`, `bytearray.lower()`, `list` for `class Stack(list)`). A `staticmethod` has no receiver, so the `message` descriptor hands over the class it was read through, which is how `bytearray.maketrans` names `bytearray`. A caught error names its exception's class (`ValueError.message() takes …`).
- A block literal answers its own sentence: `block expects 1 argument, got 2`, stating the arity exactly (`0 arguments`, `1 to 2 arguments`, `at least 1 argument`), and `block does not accept 3 arguments` for a callable CPython cannot introspect. A signature mismatch stops at `Block.__call__` while a body failure has the block's own frame below, which is how the two are told apart.
- Four families keep their own sentence because each tells the reader what to write: the converters (`range is built from a stop, … — write range(stop) or range(start, stop, step)`), `Try()` and `With()` (`— write Try(lambda: …)`), a missing block (`#map expects a block, got nothing — write .map(lambda item: …)`), and `raise_from` (`an exception or None`).
- The branch family takes `MISSING` defaults for its blocks, so a missing one answers the hint, and the two `bool` pairs show both blocks (`.if_true_if_false(lambda: …, lambda: …)`).
- `raise_` returns to CPython's shape: `ValueError.raise_() takes 1 positional argument but 2 were given`.

## Consequences

- Every name inside an arity sentence is one the receiver answers to, and it is the one CPython would name.
- A successful send pays nothing, since a `try` costs nothing on 3.15 when nothing is raised.
- One divergence is left: `bool` names itself where CPython's inherits from `int`, because `Boolean` re-supplies the int side and is not an `Int`.
- A binding failure that is not about arity, such as an unknown keyword, carries the same prefix and is renamed too.
- The wording sweep checks the callee against an oracle read off the receiver (`class_()` rather than the type, so a caught error is expected to name its exception) and sends six arguments, since over-supplying is the one arity failure no sentinel default catches. With the rename disabled it reports 563 leaks.
