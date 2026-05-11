# Proposals

## 1. Refactoring — `_ValueEqMixin` for `__eq__`/`__ne__` boilerplate

Seventeen POOP types repeat the same shape:

```python
def __eq__(self, other: object) -> Boolean:
    if isinstance(other, X):
        return true if self._value == other._value else false
    return false

def __ne__(self, other: object) -> Boolean:
    if isinstance(other, X):
        return false if self._value == other._value else true
    return true
```

**Affected.** `Int`, `Float`, `Complex`, `Str`, `Bytes`, `ByteArray`, `MemoryView`, `List`, `Tuple`, `Set`, `FrozenSet`, `Dict`, `Slice`, `Path`, `MappingProxy`, `DictKeys`, `DictItems` — about 14 lines × 17 types.

**Proposal.** Either a class-decorator `@value_equality(attr="_value")` injecting both methods, or a small mixin that uses an `_eq_attr: ClassVar[str]` to know which field to compare. Collection types (`List`, `Tuple`, `Set`, `FrozenSet`, `Dict`) already follow the same pattern but compare `self._items` / `self._data` instead of `self._value` — the helper needs to be configurable per type.

**Risk.** Low. The pattern is fully mechanical and tests already pin every operator.

**Out of scope.** Types with extra equality logic (`Slice` checks step nullability, `DictKeys`/`DictItems` compare against multiple types, `MappingProxy` accepts both `Dict` and `MappingProxy`).

## 2. Refactoring — Path-to-pathlib coercion helper

`poop/types/path.py` repeats `other._path if isinstance(other, Path) else _pathlib.Path(other._value)` (or its variants) at 5 sites: `rename` (l. 125), `replace` (l. 131), `joinpath` (l. 136, list-comp), `relative_to` (l. 149), `__truediv__` (l. 213, drops the `_pathlib.Path` wrap).

**Proposal.** Extract `_to_pathlib(other: Str | Path) -> _pathlib.Path` as a module-private helper. The `__truediv__` site stays slightly different (it relies on pathlib's `/` accepting a raw string), but the helper still covers the other 4.

**Risk.** Trivial — pure refactor.

## 3. Bug — `_poop_zip` silently drops invalid `strict` kwarg

`poop/transformers/zip.py:8-12`:

```python
def _poop_zip(*sources: object, strict: object = None) -> Zip:
    s = None if strict is None else (strict if isinstance(strict, Boolean) else None)
    return Zip(*sources, strict=s)
```

If a user passes `strict=Int(1)` (or anything non-`Boolean`), the value is silently swallowed and the zip runs in non-strict mode. Surprising and undebuggable.

**Proposal.** Raise `TypeError(f"strict must be Boolean, got {type(strict).__name__}")` when `strict` is not None and not a `Boolean`. Mirrors how `_poop_complex_from` and `_poop_int_from` validate their args.

**Risk.** Could break code that relied on the silent fallback, but that code was already buggy.

## 4. Polish — `Block.__str__` shows raw Python lambda

```python
>>> Block(lambda x: x + 1)
Block(<function <lambda> at 0x7c85c289f320>)
```

The other lazy types print as `<map>`, `<filter>`, `<zip>`, `<enumerate>`. `Block` should follow the same convention.

**Proposal.** `f"<block at {hex(id(self))}>"` or just `"<block>"`. The lambda body is generally not interesting to the user; if it is, they can introspect via `dis`.

**Risk.** Negligible. Affects display only.

## 5. Docs — `NoLoopsValidator` message predates Block

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
