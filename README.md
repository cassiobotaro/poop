# POOP

**P**ython **O**bject **O**riented **P**rogramming

A Python interpreter infected by Smalltalk.

## Development

Requires Python 3.14 and [uv](https://docs.astral.sh/uv/).

```bash
# Install dependencies
uv sync --dev

# Run
uv run python main.py

# Lint and format
uv run ruff check --fix
uv run ruff format

# Type check (examples/ excluded — uses runtime-injected names)
uv run ty check poop/ tests/

# Tests with coverage
uv run pytest
```

Git hooks are managed by [prek](https://prek.j178.dev) and run ruff and ty on every commit.

## Usage

```bash
poop examples/hello_world.py
```
