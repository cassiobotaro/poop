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

## Architecture

Entry point is `main.py` (CLI via `argparse`). Pipeline: `parse → validate → transform → execute(namespace)`.

- `poop/parser.py` — wraps `ast.parse`
- `poop/validators/` — AST validators (reject forbidden constructs); registered in `DEFAULT_VALIDATORS`: `no_if`, `no_loops`, `no_free_functions`, `no_print`, `no_try`, `no_not`, `no_unary_minus`, `no_invert`
- `poop/transformers/` — AST transformers (rewrite nodes before execution); registered in `DEFAULT_TRANSFORMERS`: `boolean`, `int`, `float`, `none`, `str`
- `poop/types/` — Smalltalk-style types: `object.py` (root), `boolean.py`, `none.py`, `int.py`, `float.py`, `interval.py`, `string.py`, `transcript.py`
- `poop/executor.py` — compiles and executes AST with an injectable namespace
- `poop/interpreter.py` — orchestrates the full pipeline

`examples/` contains valid POOP programs. Files there use names injected at runtime (`Transcript`, `True`→POOP boolean, etc.) so they are excluded from `ty` and ruff `F821`.
