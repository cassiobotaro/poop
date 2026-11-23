# 15. Single-underscore internals are unreachable

Date: 2026-04-22

## Status

Accepted

## Context

Every wrapper declares its state in `__slots__` under single-underscore names (`_value`, `_items`, `_data`, `_fn`), and those hold raw Python values. `no_poop_prefix` reserved the mangled runtime names (ADR 14), but the single-underscore internals were the ones a program could actually reach. Two spellings of the act were guarded and the third, the one a reader would type, was not:

```
"abc".get_attr("_value")   # _value is private — POOP objects do not expose their internals
"abc"._value               # 'abc', a Python str
"abc"._value.print()       # 'str' object has no attribute 'print'
```

That handed a naked Python primitive out on request, against ADR 2, and what came back answered in CPython's vocabulary, the sentence `does_not_understand` exists to replace, from a two-token expression. The REPL completer had once offered `x._value`; it stopped offering the spelling and the spelling kept working. `examples/patterns/memento.py` shows `saved = editor._content` as the procedural Python POOP exists to prevent, in its own comment.

The runtime guard had its own gaps. `Object` and the class side (`PoopMeta`) kept two copies of it, and the class side's kept the `super().__init__` carve-out the instance side had closed, so `str.get_attr("__init__")(s, "ZAP")` re-ran the constructor on a live `Str` and stranded the entry a `Dict` held under it. `has_attr` once skipped the guard entirely.

## Decision

A single-underscore name is unreachable from a program, both statically and at runtime.

- `no_private_attribute` (`poop/validators/no_private_attribute.py`) refuses an `ast.Attribute` whose `attr` starts with a single `_`. Its sentence names what to send a message to, `send other a message that answers it`, rather than `obj.get_attr(name)`, because `get_attr` refuses a private name by design.
- Three receivers stay legal, because an object reaching its own state is not reaching into anything: `self`, `cls`, and the enclosing class by its own name.
- `_reject_private` (`poop/types/_attr_guard.py`) refuses every `_`-prefixed non-dunder name passed to `get_attr`, `has_attr`, `set_attr` and `del_attr`. All four accessors call it and `_reject_dunder` on both receivers, `Object` and `PoopMeta`, through one `_checked_name`.
- Dunders belong to `no_dunder_attribute` and `_poop_*` names to `no_poop_prefix`; this validator does not refuse them too, which would answer two sentences for one spelling.

## Consequences

The enclosing-class allowance exists for one site, `Transaction._commit` in `examples/patterns/execute_around.py`, where a `@staticmethod` has neither `self` nor `cls` to write. A sweep over `examples/` reports no other case, so the rule costs one allowance and no rewrites. With one `_checked_name`, the instance side and the class side cannot keep different carve-outs.
