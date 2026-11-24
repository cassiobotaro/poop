# 16. One `is_message` predicate serves every discovery surface

Date: 2026-04-22

## Status

Accepted

## Context

`dir(obj)` is banned as a free function, with `obj.dir()` as its substitute. CPython's `dir()` is exhaustive, and an exhaustive list would surface every name the encapsulation rules hide (ADR 14, ADR 15).

Four surfaces ask "may user code send this name?": `dir()`, `:methods`, the near-miss hint, and the REPL's tab-completion. Three carried their own copy of the rule. The fourth, `_PoopCompleter._attr_matches`, spelt it `not name.startswith("__")`. Pressing Tab on `x._` therefore offered `x._value`, the raw Python `str` behind the wrapper, along with `_abc_impl` and `_eq_group`, POOP internals with no meaning in the language. The completer was teaching the spelling plain attribute access still reached. `_name_matches` filtered `_poop_`-prefixed keys only. The completer also read candidate attributes off the instance with `getattr(obj, name)`, which runs a `property` getter, so pressing Tab could execute program code.

The label of a receiver had the same split: `:methods` printed `PoopExcMeta understands 30 messages` for `ValueError`, because `type(cls)` is the metaclass.

## Decision

`is_message` (`poop/types/_selectors.py`) is the one predicate for the message surface, and every discovery surface calls it: `obj.dir()` and the class-side `Klass.dir()`, `:methods`, the near-miss hint and tab-completion. It filters every `_`-prefixed name: dunders, privates and the mangled `_poop_*` bindings. `_name_matches` filters every `_` name as well.

`receiver_label`, in the same place, is the one rule for naming a receiver. Under it, a class answers its own name. `explain` and `:methods` both use it.

The completer reads candidates with `inspect.getattr_static`, which resolves no descriptor.

## Consequences

POOP's `dir()` is deliberately not exhaustive, and it matches the REPL's `:methods`. The substitute never surfaces what the encapsulation rules hide, and a new surface that asks the question has one function to call.

Pressing Tab no longer runs program code. Reading through `getattr` on the type was not an option, because once the class side refused instance messages, `getattr(Int, "abs", None)` answered the default and every message lost its `(` in the completion.
