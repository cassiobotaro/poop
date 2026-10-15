# Design

## Context

See proposal.md - Why. What the refactor rests on:

- `DEFAULT_NAMESPACE` is built by `_merge_bindings` from every transformer's
  `BINDINGS`; a key nobody emits is dead weight in every program's namespace
  and in the completer's filter. `RESERVED_NAMES` is derived from the
  rewriters' `names`, not from `BINDINGS`, so removing a binding reserves
  nothing less.
- `List.__init__(self, *elements)`, `Tuple.__init__` and `Set.__init__` are
  variadic; `make_constructor(List)` returns a closure with the same
  signature. `_merge_bindings` cloaks a *function* binding by its spelling,
  and a class binding is already cloaked by `__init_subclass__`.
- `Range.__iter__` exists (`poop/types/range.py`), so `isinstance(r,
  Iterable)` is true.
- `CallNameValidator`, `NodeValidator` and `OpValidator` are the three shapes
  `CONTRIBUTING.md` tells a contributor to pick from; `no_builtin_shadow`
  imports `no_namespace_shadow`'s private `_Visitor`.

## Goals / Non-Goals

**Goals:**
- `DEFAULT_NAMESPACE` holds only names a rewrite emits or a program spells.
- Every transformer helper exists once, in `base.py` when two modules share
  it.
- Both shadow validators are two class attributes over one shared helper.

**Non-Goals:**
- Any change to what a program observes; those are in `fix-behaviour-leaks`.

## Decisions

- **Dead bindings are removed, not kept "for symmetry"**: a test
  (`tests/test_transformers/test_namespace.py`) asserts that every
  `_poop_*` key in `DEFAULT_NAMESPACE` is either emitted by some rewriter or
  named by `DEFAULT_NAMESPACE`'s two public entries, so the next dead key is
  caught at the gate rather than by a review.
- **`rebind(target: ast.expr, helper: str) -> ast.Assign`** takes the
  *target expression* so `unpack.py`'s attribute targets and `varargs.py`'s
  name targets go through one function; `varargs.py` builds its target with
  `name_at(name, node, ast.Store())`.
- **`range.py` normalises with a lookup by argument count**
  (`{1: (0, a, 1), 2: (a, b, 1), 3: (a, b, c)}`-style) and keeps POOP's
  zero-step refusal before building; `Range._from_native(range(...))` was
  considered and rejected because it would let CPython's `range() arg 3 must
  not be zero` through.
- **`ShadowValidator` carries `protected` and `message`** as `ClassVar`s,
  mirroring `CallNameValidator`'s `forbidden`/`message`; the REPL's
  `_explain_calls` reads `forbidden` only, so `protected` keeps these two out
  of `:explain`'s call topics as they are today.
- **`match` patterns only where a guard reads as a pattern**: `case
  ast.Call(func=ast.Name(id=name)) if self.is_builtin(name)` in
  `BuiltinRewriter.visit_Call`, `case ast.Call(func=ast.Name(id="super"))`
  in `_is_super_call`. `no_unary_minus` keeps `type(value) in (...)` because
  a class pattern would admit `bool`.

## Risks / Trade-offs

- [A test or example reads one of the seven bindings by name] → grep over
  `poop/`, `tests/` and `examples/` finds none; the namespace test pins it.
- [`__qualname__` vs `__name__` in a refusal: the cloak sets both, so
  output is identical today] → the choice is uniformity only; the wording
  sweep still passes.
