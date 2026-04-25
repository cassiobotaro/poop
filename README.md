# POOP 💩

**POOP** is an acronym for **P**ython **O**bject **O**riented **P**rogramming.

A Python interpreter infected by Smalltalk.

## Development

Requires Python 3.14 and [uv](https://docs.astral.sh/uv/).

```bash
# Install dependencies
uv sync --dev

# Run
poop <file.py>
uv run python main.py <file.py>  # alternative without installing

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

## Type annotations

Type annotations (`x: int`, `def f(x: int) -> str:`) are not evaluated at
runtime in Python and do not cause errors in POOP programs. However, they are
misleading: POOP transforms all literals to its own types (`Int`, `Str`, …),
so a variable annotated as `int` will hold an `Int` at runtime.

Avoid type annotations in POOP programs. The `type` keyword (`type X = int`)
is explicitly banned by the validator pipeline.
