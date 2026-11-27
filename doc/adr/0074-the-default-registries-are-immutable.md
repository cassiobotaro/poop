# 74. The default registries are immutable

Date: 2026-11-27

## Status

Accepted

## Context

Every interpreter starts from three module-level registries: `DEFAULT_VALIDATORS`, `DEFAULT_TRANSFORMERS` (built from `_TRANSFORMER_CLASSES`) and `DEFAULT_NAMESPACE`. They were a `list`, two lists and a `dict`. Nothing in the package changes them after import.

Because they could be changed, `Interpreter.__init__` copied the two lists, so that one interpreter's `append` would not change what every later interpreter starts from. `Interpreter.validators` then answered that copy, which a caller could still clear or append to from outside.

## Decision

We will build the validator and transformer registries as tuples, and expose `DEFAULT_NAMESPACE` as a `types.MappingProxyType` over the merged bindings. The proxy is used instead of Python 3.15's `frozendict` because POOP wraps `frozendict` as a type for programs, and the interpreter's own namespace should not be one of the language's values.

An `Interpreter` accepts any sequence of validators or transformers and any mapping as its namespace. It stores a tuple of each sequence and answers that tuple from `validators`. `new_namespace()` still gives each program its own `dict`.

## Consequences

No caller can change what a later interpreter starts from, or what an existing interpreter validates and transforms with.

This changes the Python API. `Interpreter.validators` answers a tuple, and the registries reject `append` and item assignment. Nothing in `poop/` or `tests/` relied on either.

The language and the CLI behave exactly as before.
