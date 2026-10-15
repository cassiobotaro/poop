# Design

## Context

See proposal.md — Why. The current shape:

- `cli.main` branches on `file is None` before reading the mode flags, and
  every `PoopError` exits 1 through `_poop_errors`. `report(err, source,
  console)` renders the gutter and caret; `_unreadable` writes through
  `_write`, which does not colour.
- `Repl.__init__` calls `_setup_readline`, which reads `_HISTORY_FILE` and
  registers an `atexit` saver once per process. `_error` is the one
  red-stderr writer; `_say` is stdout. Meta-commands dispatch by name to
  `_meta_*`.
- `ValidationError` carries message, line and column; nothing names the
  validator that raised it. `ErrorCollector.report` is the one place every
  validator's error is built.
- `tests/test_cli.py` runs the root `main.py` as "the uninstalled entry
  point" and asserts on `result.output`, the interleaved stream.

## Goals / Non-Goals

**Goals:**
- A shell script can run `poop` on a pipe and parse its stdout; an editor
  can parse `--format json`; CI can branch on the exit code.
- The test suite leaves the developer's home directory untouched.

**Non-Goals:**
- New meta-commands; changes to the error gutter's prose format.

## Decisions

- **Non-tty stdin is a program, not a REPL with prompts on stderr.**
  CPython parity (`python3 < file`), one code path (`_read_source` on
  `sys.stdin`), and it makes `poop -` free. The alternative — prompts on
  stderr — keeps `printf ':methods 5' | poop` working but leaves the banner
  problem for every consumer that merges streams. REPL tests already drive
  `Repl` through `feed_input`, so nothing in the suite pipes meta-commands.
- **Exit codes by error class** at the `_poop_errors` boundary: the
  handler already knows the class; a `dict[type[PoopError], int]` maps it.
  Usage errors (`BadParameter`) are typer's 2, which parse errors share
  deliberately: both say "this is not a program".
- **`--format json` is a `typer.Option` with `Literal["text", "json"]`**,
  rejected unless `--validators-only` is set. `ValidationError` gains a
  `validator: str` attribute filled by `ErrorCollector.report` from
  `type(self).__module__.rsplit(".", 1)[-1]`, so each validator module
  name (`no_print`) is the identifier — the same string `:explain` uses as
  a topic. `json.dumps` with `ensure_ascii=False` keeps the em-dash.
- **`Repl(interpreter, *, history: Path | None = None)`**: `None` means the
  default path when stdin is a tty, and no readline at all otherwise. The
  `atexit` saver captures the path it was given. The `repl` fixture passes
  `tmp_path / "history"`.
- **One red-line writer in `console.py`** (`error_line(console, text)`)
  used by `cli._unreadable`, `cli.report`'s header and `Repl._error`, so
  the colour decision lives beside the consoles.
- **`poop/__main__.py`** is two lines; `tests/test_cli.py._run_main` runs
  `sys.executable -m poop`. `[build-system]` uses `uv_build`, the backend
  uv ships; `tests/`, `setup.cfg` and the egg-info stop appearing in the
  sdist.
- **`-c` and `-` share `main`'s source-reading step**: a `_source_from(file,
  code)` helper answers `(source, filename)` for a path, `-`, `-c` or a
  non-tty stdin, in that precedence, so the three run paths below it are
  unchanged.

## Risks / Trade-offs

- [Exit codes change from 1 for every failure] → the README documents the
  table; no CI in the repo branches on `1`.
- [A user who piped meta-commands into the REPL loses that] → documented in
  the README's REPL section; `poop -c` covers the one-liner case.
- [`uv_build` requires a `src`-less layout to be declared] → `module-name =
  "poop"` and `module-root = ""` in `[tool.uv.build-backend]`; verified by
  `uv build` and installing the wheel in a scratch venv in task 3.2.
