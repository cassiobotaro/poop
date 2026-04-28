# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

POOP (Python Object Oriented Programming) is a Python 3.14 interpreter infected by Smalltalk, managed with `uv`.

## Commands

```bash
# Install dependencies
uv sync --dev

# Run
poop <file.py>
uv run python main.py <file.py>  # alternativa sem instalar

# Lint and format
uv run ruff check --fix
uv run ruff format

# Type check (examples/ excluded — uses runtime-injected names)
uv run ty check poop/ tests/

# Run tests with coverage
uv run pytest

# Run a single test
uv run pytest tests/test_file.py::test_name
```

## Tooling

- **ruff** — linting and formatting (configured in `pyproject.toml` under `[tool.ruff]`)
- **ty** — type checking
- **pytest-cov** — test coverage reporting for the `poop` module (`tests/`)
- **prek** — git hook runner using `.pre-commit-config.yaml`; hooks run `ruff check --fix`, `ruff format`, and `ty check` on every commit

## Workflow

Após cada funcionalidade ou correção implementada, fazer commit das mudanças com mensagem descritiva. Cada commit deve ser atômico — um validator, um tipo, um bug fix — nunca agrupar mudanças não relacionadas.

Before implementing a multi-part plan, confirm scope with the user — they may want only a subset implemented (e.g., `dir` as method but `help` as function).

## Testing

When fixing tests, verify expected values against actual language semantics (e.g., ascii repr quoting style, inclusive vs exclusive interval bounds, `__radd__` requirements for `builtins.sum`) before assuming the implementation is wrong.

## Language Design Principles

When implementing new types or features, ensure they are transparent to end users (e.g., use lambda transformers, `__call__`, or syntactic sugar) rather than exposing internal class names like `Block()`.

## Conventions

Always verify GitHub Action versions are current and use the actual current year (2026) in license files, copyright notices, and dates.

## Architecture

Entry point is `main.py` (CLI via `argparse`). Pipeline: `parse → validate → transform → execute(namespace)`.

- `poop/parser.py` — wraps `ast.parse`
- `poop/validators/` — AST validators (reject forbidden constructs); registered in `DEFAULT_VALIDATORS`: `no_if`, `no_loops`, `no_comprehension`, `no_free_functions`, `no_print`, `no_assert`, `no_raise`, `no_try`, `no_type_alias`, `no_with`, `no_not`, `no_unary_minus`, `no_invert`, `no_is`, `no_in`, `no_global`, `no_yield`, `no_walrus`, `no_match`, `no_len`, `no_abs`, `no_ascii`, `no_hash`, `no_isinstance`, `no_issubclass`, `no_callable`, `no_id`, `no_all`, `no_any`, `no_min`, `no_max`, `no_map`, `no_filter`, `no_round`, `no_bin`, `no_breakpoint`, `no_chr`, `no_divmod`, `no_enumerate`, `no_exec`, `no_exit`, `no_format`, `no_getattr`, `no_hasattr`, `no_input`, `no_introspection`, `no_iter`, `no_open`, `no_pow`, `no_repr`, `no_setattr`, `no_slice`, `no_sorted`, `no_reversed`, `no_subscript`, `no_sum`, `no_del`
- `poop/transformers/` — AST transformers (rewrite nodes before execution); registered in `DEFAULT_TRANSFORMERS`: `boolean`, `none`, `complex`, `bytes`, `byte_array`, `memory_view`, `int`, `float`, `str`, `range`, `list`, `tuple`, `dict`, `set`, `frozen_set`, `raise_`, `class_`
- `poop/types/` — Smalltalk-style types: `object.py` (root), `boolean.py`, `none.py`, `complex.py`, `bytes.py`, `byte_array.py`, `memory_view.py`, `int.py`, `float.py`, `interval.py`, `string.py`, `range` (via `interval.py`), `list.py`, `tuple.py`, `dict.py`, `set.py`, `frozen_set.py`, `error.py`, `try_.py`, `with_.py`
- `poop/executor.py` — compiles and executes AST with an injectable namespace
- `poop/interpreter.py` — orchestrates the full pipeline

`examples/` contains valid POOP programs. Files there use names injected at runtime (`True`→POOP boolean, etc.) so they are excluded from `ty` and ruff `F821`.
