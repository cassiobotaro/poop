# Proposals

## 1. Bug — `_poop_zip` silently drops invalid `strict` kwarg

`poop/transformers/zip.py:8-12`:

```python
def _poop_zip(*sources: object, strict: object = None) -> Zip:
    s = None if strict is None else (strict if isinstance(strict, Boolean) else None)
    return Zip(*sources, strict=s)
```

If a user passes `strict=Int(1)` (or anything non-`Boolean`), the value is silently swallowed and the zip runs in non-strict mode. Surprising and undebuggable.

**Proposal.** Raise `TypeError(f"strict must be Boolean, got {type(strict).__name__}")` when `strict` is not None and not a `Boolean`. Mirrors how `_poop_complex_from` and `_poop_int_from` validate their args.

**Risk.** Could break code that relied on the silent fallback, but that code was already buggy.

## 2. Polish — `Block.__str__` shows raw Python lambda

```python
>>> Block(lambda x: x + 1)
Block(<function <lambda> at 0x7c85c289f320>)
```

The other lazy types print as `<map>`, `<filter>`, `<zip>`, `<enumerate>`. `Block` should follow the same convention.

**Proposal.** `f"<block at {hex(id(self))}>"` or just `"<block>"`. The lambda body is generally not interesting to the user; if it is, they can introspect via `dis`.

**Risk.** Negligible. Affects display only.

## 3. Docs — `NoLoopsValidator` message predates Block

`poop/validators/no_loops.py:21` suggests:

```
(lambda: cond).while_true(lambda: body)
```

But `while_true` lives on `Block`, and the `BlockTransformer` wraps every lambda automatically — so the user-facing idiom in real POOP code is:

```
Block(lambda: cond).while_true(Block(lambda: body))
```

The current message technically works (because lambdas get wrapped), but it doesn't match how examples in `INFECTIONS.md` and `MIGRATION.md` write loops, and it leaves the reader wondering where `while_true` comes from.

**Proposal.** Update the message to spell out `Block(lambda: ...)`. Same pattern for `visit_For` if a `Block`-flavoured suggestion exists.

**Risk.** None — message-only.
