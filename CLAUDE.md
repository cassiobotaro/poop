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

Entry point is `poop/cli.py` (CLI via `typer`); `main.py` is a thin wrapper that calls `entry_point()` for the uninstalled `python main.py <file>` path. `poop` with no file argument starts the REPL. Pipeline: `parse → validate → transform → execute(namespace)`.

- `poop/parser.py` — wraps `ast.parse`
- `poop/validators/` — AST validators rejecting forbidden constructs (`if`, loops, `len`, `print`, 71 in all); source of truth: `DEFAULT_VALIDATORS` in `poop/validators/__init__.py`. `collect()` is the primitive: validators subclass `CollectingValidator` (`poop/validators/base.py`) and implement `collect()`; `validate()` derives from it by raising the first error. Collecting cannot be built from raising, and `--validators-only` needs every error.
- `poop/transformers/` — AST transformers rewriting literals and builtins before execution, plus namespace-only transformers that inject names into the namespace without rewriting AST (`try_`, `with_`); source of truth: `DEFAULT_TRANSFORMERS` and `DEFAULT_NAMESPACE` in `poop/transformers/__init__.py`. Order is load-bearing and commented where it matters (e.g. `UnpackTransformer` must run after `DictTransformer`).
- `poop/types/` — Smalltalk-style type wrappers (`object.py` is the root, `meta.py` the class side): one module per wrapped builtin and iterator; see the directory listing and the `INFECTIONS.md` catalog for the full inventory and the rules wrappers must follow
- `poop/executor.py` — compiles and executes AST with an injectable namespace
- `poop/interpreter.py` — orchestrates the full pipeline
- `poop/errors.py` — `PoopError` hierarchy and `format_error`, shared by the CLI and the REPL
- `poop/repl.py` — the interactive REPL

POOP is the language, not the library: it mirrors no stdlib module. If Python needs an `import` to reach something, POOP does not offer it — `DEFAULT_NAMESPACE` exposes exactly two names user code can name: `Try` and `With`, the constructs replacing the `try`/`except` and `with` keywords. (The dict itself is larger — every other key is a mangled `_poop_*` binding, including the exception classes, which reach user code by transformer rewrite rather than by being named directly.) User code also runs against a builtins allow-list (`_ALLOWED_BUILTINS` in `poop/executor.py`), so every Python builtin POOP does not own answers `NameError`. There is no file I/O and no async. Do not add a module mirror back without revisiting that decision.

Naming rules: injected names copy Python's exact casing — `Try` and `With` are classes, so PascalCase. Every other type wrapper (`Int`, `List`, ...) is bound under a mangled `_poop_*` name unreachable from user code; lowercase Python builtins (`int`, `list`, ...) get rewritten to those mangled names. The root class is reachable under **both** `object` and `Object`: `ObjectTransformer` rewrites either spelling to `_poop_object` in any position, so `Object.name()` and `object.name()` both answer `object`. It is the one wrapper user code can name directly — deliberately, since `class Foo(Object)` reads naturally and the raw wrapper is never exposed (the binding is still `_poop_object`; the names are only source spellings).

`examples/` contains valid POOP programs, organized into three subfolders: `basics/` (language fundamentals), `idiomatic/` (idiomatic POOP usage), and `patterns/` (Sandi Metz / GoF OO patterns). Files there use names injected at runtime (`True`→POOP boolean, etc.) so they are excluded from `ty` and ruff `F821` (pattern `examples/**/*.py` in `pyproject.toml`).
