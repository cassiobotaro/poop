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

## Conventions and workflow

The contributor workflow and conventions (atomic commits, imports at top, English-only `proposals.md`, Smalltalk version in every example, etc.) are documented in [`CONTRIBUTING.md`](CONTRIBUTING.md). Follow them as if you were a human contributor.

AI-specific guidance:

- Before implementing a multi-part plan, confirm scope with the user — they may want only a subset implemented (e.g., `dir` as method but `help` as function).
- When fixing tests, verify expected values against actual language semantics (e.g., ascii repr quoting style, inclusive vs exclusive interval bounds, `__radd__` requirements for `builtins.sum`) before assuming the implementation is wrong.
- When implementing new types or features, ensure they are transparent to end users (e.g., use lambda transformers, `__call__`, or syntactic sugar) rather than exposing internal class names like `Block()`.

## Documentation Updates

- When fixing code, check whether `README.md` or related docs also need updates in the same commit.
- Validate documentation code snippets actually run before committing.

## Architecture

Entry point is `poop/cli.py` (CLI via `typer`); `main.py` is a thin wrapper that calls `entry_point()` for the uninstalled `python main.py <file>` path. Pipeline: `parse → validate → transform → execute(namespace)`.

- `poop/parser.py` — wraps `ast.parse`
- `poop/validators/` — AST validators rejecting forbidden constructs (`if`, loops, `len`, `print`, ~60 in all); source of truth: `DEFAULT_VALIDATORS` in `poop/validators/__init__.py`
- `poop/transformers/` — AST transformers rewriting literals and builtins before execution, plus namespace-only transformers that inject names into the namespace without rewriting AST; source of truth: `DEFAULT_TRANSFORMERS` and `DEFAULT_NAMESPACE` in `poop/transformers/__init__.py`
- `poop/types/` — Smalltalk-style type wrappers (`object.py` is the root): one module per wrapped builtin, stdlib namespace, and iterator; see the directory listing and the `INFECTIONS.md` catalog for the full inventory and the rules wrappers must follow
- `poop/executor.py` — compiles and executes AST with an injectable namespace
- `poop/interpreter.py` — orchestrates the full pipeline

Naming rules: injected names copy Python's exact casing — stdlib module mirrors stay lowercase (`math`, `random`, ...), POOP-specific entry points are PascalCase (`Try`, `With`, `Path`), and a module that also exposes a class (e.g., `random` ⊃ `Random`) binds both names. Every other type wrapper (`Int`, `List`, `Object`, ...) is bound under a mangled `_poop_*` name unreachable from user code; lowercase Python builtins (`int`, `list`, `object`, ...) get rewritten to those mangled names.

`examples/` contains valid POOP programs, organized into three subfolders: `basics/` (language fundamentals), `idiomatic/` (idiomatic POOP usage), and `patterns/` (Sandi Metz / GoF OO patterns). Files there use names injected at runtime (`True`→POOP boolean, etc.) so they are excluded from `ty` and ruff `F821` (pattern `examples/**/*.py` in `pyproject.toml`).
