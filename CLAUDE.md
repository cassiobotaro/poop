# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

POOP (Python Object Oriented Programming) is a Python 3.14 interpreter infected by Smalltalk, managed with `uv`.

## Commands

```bash
# Install dependencies
uv sync --dev

# Run
uv run python main.py

# Lint and format
uv run ruff check --fix
uv run ruff format

# Type check
uv run ty check

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

Entry point is `main.py` with a `main()` function. The project is in early stages.
