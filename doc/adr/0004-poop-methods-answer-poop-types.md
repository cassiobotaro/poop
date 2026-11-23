# 4. POOP methods answer POOP types

Date: 2026-04-21

## Status

Accepted

## Context

A wrapper (ADR 3) is only useful if what it answers is a wrapper too. A method that hands back a raw Python `int`, `bool`, `str` or `list` puts a native value back into the program, and that value answers none of POOP's messages.

Python itself needs native answers in some places. `if`, `dict`, `len()` and `str()` only work when `__bool__`, `__hash__`, `__len__`, `__str__`, `__int__`, `__float__`, `__contains__` and `__repr__` return native types.

Native values also enter through paths no method writes:

- A void function answers raw `NoneType`.
- CPython's `UNPACK_EX` builds the rest-collection of `c, *rest = xs` as a raw `list`.
- A variadic parameter receives a raw `tuple` or `dict`.
- Python's `**` demands raw `str` keys and a POOP `Dict` holds `Str`. A splat therefore answered CPython's own words about a POOP object: `A().m(**{"a": 1})` raised `TypeError: keywords must be strings`. Three of the four splat positions already worked (`f(*xs)` because a `Tuple` is iterable, `def m(**kw)` by the variadic prologue, `{**a, **b}` through `_poop_dict_merge`), and `DictTransformer` had already met the same constraint for `dict(**other)`. Only the general call was left.

## Decision

Every explicitly named method on every POOP type answers a POOP object, never a raw Python `int`, `bool`, `str`, `list` or the like. The rule covers `len()`, `hash()`, `not_()`, `includes()`, `tobytes()` and every other named message. Returning a native type is a bug.

The exception is the Python protocol dunders listed above, which return native types because Python requires it.

Transformers keep the implicit paths on the POOP side:

- `ReturnTransformer` (`poop/transformers/return_.py`) turns a bare `return` into `return _poop_none`, and appends `return _poop_none` to a function body that does not end in `return` or `raise`.
- `VarargsTransformer` (`poop/transformers/varargs.py`) gives a method with `*args` / `**kwargs` a prologue (`args = _poop_tuple_from(args)`, `kw = _poop_dict_from_kwargs(kw)`), so `args` is a POOP `Tuple` and `kw` a POOP `Dict` with `Str` keys. A variadic lambda wraps its body in a nested lambda that receives the converted values.
- `VarargsTransformer` also wraps each call-site `**d` as `**_poop_kwargs_from(d)`, the inverse of `_poop_dict_from_kwargs`: keys unwrap, values stay POOP objects, and a `**kw` parameter on the far side re-wraps them into a `Dict` unchanged.
- `UnpackTransformer` (`poop/transformers/unpack.py`) appends `target = _poop_list_from(target)` after each assignment with a `*target`, one per starred name, including nested (`a, (b, *inner) = …`) and attribute (`a, *self.rest = …`) targets.

## Consequences

- A void method answers the `none` singleton instead of raw `NoneType`. `__init__` is skipped, since CPython requires it to return real `None`.
- A `MappingProxy` splats too, and the call-site rewrite covers `MyError.raise_(**kw)` without extra work.
- Splat failures reach CPython raw through the faithful-unwrap idiom: `f(**{1: 2})` still answers `keywords must be strings`, now about a key the program wrote, and `f(**5)` answers `Value after ** must be a mapping, not int`.
- The call-site rewrite must run after `DictTransformer`; the declaration order guarantees it.
- What a void mutator answers is ADR 29.
