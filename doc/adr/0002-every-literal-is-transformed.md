# 2. Every literal is transformed

Date: 2026-04-21

## Status

Accepted

## Context

Python source is full of literals: `1`, `3.14`, `"hello"`, `True`, `False`, `None`, `...`, `[1, 2]`, `(1, 2)`, `{1, 2}`, `{k: v}`, `b"..."`, `1+2j`. Left alone, each of them reaches runtime as a naked Python primitive, which is not a POOP object.

One kind of string literal is not a value in the program. `StrTransformer` first wrapped every `ast.Constant` whose value is a `str`, docstrings included, so the docstring of a class or function became an expression statement that built a `Str` on every call. The `2026-10-14-fix-behaviour-leaks` change found this and left the docstring as a raw constant, so CPython stores it as `__doc__`. It considered exempting the module docstring as well and did not: the REPL runs each input as a module, so `"abc"` at the prompt and `:methods "abc"` would have evaluated a raw Python `str`. `tests/test_repl.py` found that on the first run. A POOP program cannot read a module docstring anyway.

## Decision

A transformer rewrites every literal in Python source into its POOP equivalent before execution, so no naked Python primitive ever reaches runtime. Each wrapper type has its own transformer in `poop/transformers/` (for strings, `ast.Constant(value=str)` becomes `_poop_str(s)` in `poop/transformers/string.py`). The wrappers themselves are ADR 3.

The one exception is the docstring of a class or function: its first string statement is left as it is. Only that first statement is exempt; a later bare string in the same body is still a `Str`. A module's first string is not treated as a docstring and is wrapped like any other.

## Consequences

- Every value a program writes is a POOP object from its first appearance, which is what lets ADR 4 require that POOP methods answer POOP types.
- A docstring costs nothing per call and stays readable through `__doc__`.
- `VarargsTransformer` inserts its `*args`/`**kwargs` prologue after the docstring, for the same reason the docstring is kept.
- The REPL echoes `"abc"` as a POOP value, and `:methods "abc"` asks what that value answers.
