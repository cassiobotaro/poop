# 14. Wrappers are mangled and cloaked as builtins

Date: 2026-04-22

## Status

Accepted

## Context

POOP's types are wrapper classes (`Int`, `List`, …) that must pass for the Python builtins they stand for. Two things can betray them: a program reaching a wrapper by its own name, and a wrapper answering a name that is not the builtin's.

The name a wrapper answers is set in three attributes, `__module__`, `__name__` and `__qualname__`, and patching them one by one let one be forgotten. `__qualname__` was the one left out, and CPython prefers it in several of its own messages: Python 3.14's unhashable-key error put both spellings in a single sentence (`cannot use 'List' as a dict key (unhashable type: 'list')`). The leak reached every wrapper at once. It also reached one frame further in. CPython builds a call-signature error from the function's `__qualname__`, frozen when the class body ran, so `"abc".upper(1)` blamed `Str.upper()` and `[1, 2].map()` blamed `_IterableMixin.map()`, a private name a program is kept from spelling. The rewriter helpers leaked the same way: `range(1, 2, 3, 4)` blamed `_poop_range()`, a spelling `no_poop_prefix` would refuse if the reader typed it back. The factory-built collection helpers answered `make_iterable_from.<locals>._from()`. Some messages composed a type name by hand (`"ByteArray"`), half in POOP's vocabulary and half in the wrapper's.

Rebinding a name the rewriters own was the other hazard. An assignment target is an `ast.Name`, so `ValueError = 5` became `_poop_ValueError = 5` and clobbered the mirror for the rest of the program. A parameter and a class name are not, so they kept their spelling while every read of them in the body still rewrote to the mirror: `def hold(self, ValueError): return ValueError` answered the class and never saw its argument, and `class KeyError(Object)` defined a class no program could then name. After `Ellipsis = 5`, the literal `...` itself answered `5`. The rewriters' reserved names were once a hand-written table of twenty names in the validator, while its own comment argued that the mirrors had to be derived so a new one could not ship without its reservation.

## Decision

Every wrapper class is bound in `DEFAULT_NAMESPACE` under a mangled `_poop_*` key (`_poop_int`, `_poop_list_cls`, `_poop_object`, …), and `no_poop_prefix` refuses any `ast.Name`, `ast.Attribute`, `ast.arg`, `ast.FunctionDef` or `ast.ClassDef` naming one. The bare builtin (`int`, `list`, `object`, …) is rewritten at parse time to its mangled name. The root is the one class a program names directly, as either `object` or `Object`, and `ObjectTransformer` rewrites both to `_poop_object` in any position.

Each wrapper is cloaked through `cloak(cls, name)` (`poop/types/_cloak.py`), which sets `__module__ = "builtins"`, `__name__` and `__qualname__` together. `Object.__init_subclass__` applies it from the `name=` class keyword (`class Int(_NumericCompareMixin, Object, name="int")`), so a wrapper cannot be defined with the cloak forgotten. `cloak` also renames the functions a class owns. The shared mixins (`_IterableMixin`, `_PeekMixin`, `_ValueEqMixin`, `_OrderedMixin`, `_NumericCompareMixin`, `_DictView`, `_DictItemIteratorBase`) and `Error` are cloaked as `object`, because no single builtin name is true for every wrapper that inherits them. `_BytesLikeMixin`, inherited by `bytes` and `bytearray` alone, is cloaked as `bytes`. Its twin `cloak_callable(fn, name)` covers the rewriter helpers and is applied centrally in `_merge_bindings` (`poop/transformers/_registry.py`), so the mangled key stays and `range(1, 2, 3, 4)` blames `range()`. A message that names a type composes it from `type(x).__qualname__` and `poop_type.__name__`, never from a literal.

The non-builtin wrappers follow the same rule: `Block` answers `function`, `Try` and `With` keep their names but drop the module path, and `Error` answers the exception it wraps (`e.class_name()` is `IndexError`, through a `class_()` that delegates to `kind()`). The only user-facing entry points are `Try` and `With`, both PascalCase because they are classes; no lowercase name is injected.

Reserved names are derived, never listed. `no_namespace_shadow` protects every non-`_poop_*` entry of `DEFAULT_NAMESPACE`, computed when the validator is built. `no_builtin_shadow` reuses its visitor over every name a transformer rewrites in any position. Each rewriter declares `names`, every spelling it claims (`{builtin}` by default, `object` and `Object` on the root's, `Ellipsis` on the ellipsis rewriter). `RESERVED_NAMES` in `poop/transformers/_registry.py` unions them, and the mirror half is derived from `MIRRORS`. A rebinding, whether assignment, class name or `def`/`lambda` parameter, is refused with `'<name>' is a POOP builtin name; it cannot be rebound`.

## Consequences

`repr(Int)` reads `<class 'int'>` and `Int(5).class_name()` answers `Str("int")`. POOP builtins answer to the names Python builtins do, and no wrapper leaks a `poop.types.*` path or an internal name through `class_()` or `class_name()`. Patching one attribute and forgetting the others is not representable. `tests/test_cloak.py` sweeps every POOP class rather than asserting per wrapper, since the leak reached all of them at once.

A new entry point or a new mirror protects itself without a change to either shadow validator. Using the reserved names as constructors (`int("5")`), as bases (`class MyErr(ValueError)`) or as message receivers (`ValueError.raise_(…)`) is unaffected. `no_namespace_shadow` does not catch method names inside classes (`class Calc: def Try(self): …`), which bind as attributes, not in the namespace scope.
