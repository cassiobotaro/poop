# Proposal

## Why

Exercising the command line end to end found the two consoles `console.py`
exists for being bypassed in four places, two flags silently ignored, the
test suite rewriting the developer's own `~/.poop_history`, and three
affordances the REPL already has (`_`, Tab completion, history) documented
nowhere. A program piped into `poop` gets a banner and a prompt on stdout
between its own lines, which is what `python3 < file` never does.

## What Changes

- **Non-tty stdin runs as a program**: `echo 'x.print()' | poop` and
  `poop -` read standard input as a source file, with no banner and no
  prompt, as CPython does. The REPL is what an interactive stdin gets.
- **`--validators-only` / `--transformers-only` without a file is an
  error** (`typer.BadParameter`), not a silent REPL.
- **Every diagnostic goes to stderr, red when stderr is a terminal**: the
  `cannot read` line, `:explain`'s "no topic" sentence and the two `usage:`
  lines join `_error`'s contract.
- **`--version`, `-c "code"` and `--format json`** on `--validators-only`:
  a list of `{line, col, message, validator}` objects for editors and CI,
  and distinct exit codes — 2 for a parse error, 3 for validation, 4 for
  execution, 1 for an unreadable file — in both formats.
- **The history file is a `Repl` parameter**, defaulting to
  `~/.poop_history`, and the test fixture passes a temporary one; readline
  is not touched when stdin is not a terminal.
- **`:explain`'s known-constructs list is laid out by rich `Columns`** like
  `:methods`, and the stale comment about one-column pipes goes.
- **`python -m poop` works**: `poop/__main__.py` replaces the root
  `main.py`; `pyproject.toml` declares a build backend so `uv build` stops
  shipping `tests/`.
- **The REPL's existing affordances are documented**: `_` as the last
  result, Tab completion, history persistence, in `:help` and the README.
- **CI**: `setup-uv@v10` and `uv sync --locked --dev`.

Out of scope, and why: Smalltalk-browser meta-commands (`:hierarchy`,
`:source`, `:doc`) — a REPL feature set deserving its own proposal, not a
stream contract; piping *into the REPL* for meta-commands, which the
non-tty decision removes on purpose (CPython parity; the REPL tests drive
`Repl` directly through `feed_input`).

## Capabilities

### New Capabilities

- `cli`: what `poop` reads, where it writes, and how it exits.

### Modified Capabilities

- `repl`: diagnostics on stderr, the history file as a parameter, the
  documented affordances.

## Impact

- `poop/cli.py`, `poop/repl.py`, `poop/console.py` (a shared red-line
  writer), new `poop/__main__.py`, root `main.py` removed.
- `poop/errors.py`: `ValidationError` carries the validator's name for the
  JSON format (set in `ErrorCollector.report` from the owning validator).
- `pyproject.toml` (`[build-system]`, `[project.scripts]` unchanged),
  `.github/workflows/ci.yml`.
- Tests: `tests/test_cli.py` (stdout/stderr split asserted, exit codes, the
  pipe test no longer needs `/dev/stdin`), `tests/test_repl.py` (history
  fixture), `tests/_support.py`.
- Docs: `README.md` REPL section, `CONTRIBUTING.md` entry-point line,
  `MIGRATION.md` if it names `poop file`.
