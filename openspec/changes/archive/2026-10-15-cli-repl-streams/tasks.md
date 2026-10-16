# Tasks

## 1. Streams and exit codes

- [x] 1.1 Add `error_line(console, text)` to `poop/console.py` and use it from `cli._unreadable`, `cli.report` and `Repl._error`; route `:explain`'s no-topic sentence and the two `usage:` lines through `_error`; in `tests/test_cli.py` assert `result.stdout == ""` on every diagnostic test and `result.stderr == ""` on the clean run, and in `tests/test_repl.py` assert the three sentences land on the err buffer; verify `uv run pytest tests/test_cli.py tests/test_repl.py -q` passes.
- [x] 1.2 Map `PoopError` classes to exit codes 2/3/4 in `_poop_errors`, keep 1 for `_unreadable`, and add a parametrised `tests/test_cli.py` case over the four failure kinds; verify it passes and `README.md` gains the exit-code table.
- [x] 1.3 Refuse `--validators-only` / `--transformers-only` with no source via `typer.BadParameter`, and add `_source_from(file, code)` reading a path, `-`, `-c` or a non-tty stdin; replace the `/dev/stdin` pipe test with a `-` and a bare-pipe case; verify `uv run pytest tests/test_cli.py -q` passes and `printf '"x".print()\n' | uv run poop` prints only `x`.
- [x] 1.4 Add `--version` (reading `importlib.metadata.version("poop")`) and `-c`; add tests; update `README.md`'s run block; verify `uv run poop --version` and `uv run poop -c '"abc".len().print()'` answer as the spec says.
- [x] 1.5 Add `validator` to `ValidationError`, filled in `ErrorCollector.report`, and `--format json` on `--validators-only`; add tests for the two-error and clean cases parsing stdout with `json.loads`; verify `uv run pytest tests/test_cli.py tests/test_validators -q` passes.

## 2. REPL hygiene

- [x] 2.1 Make the history path a `Repl` keyword parameter, skip readline on a non-tty stdin, have the `repl` fixture pass `tmp_path / "history"`, and add a test asserting `_setup_readline` is not called when stdin is not a tty; verify `stat -c %Y ~/.poop_history` is unchanged across `uv run pytest tests/test_repl.py -q`.
- [x] 2.2 Lay out `:explain`'s known-constructs list with `Columns` as `:methods` does, drop `textwrap`, fix the one-column comment; verify `uv run pytest tests/test_repl.py -q` passes and `printf ':explain banana\n' | uv run poop -` is no longer the way to reach it (use `feed_input` in the test).
- [x] 2.3 Document `_`, Tab completion and history in `_META_HELP` and `README.md`'s REPL block; add a test that `:help` names all three; verify `uv run pytest tests/test_repl.py tests/test_doc_counts.py -q` passes.

## 3. Packaging and CI

- [x] 3.1 Add `poop/__main__.py`, delete root `main.py`, point `tests/test_cli.py._run_main` at `-m poop`, and update `CONTRIBUTING.md`'s mention of the entry point; verify `uv run python -m poop examples/basics/hello_world.py` prints `Hello, World!` and `uv run pytest tests/test_cli.py -q` passes.
- [x] 3.2 Declare `[build-system]` with `uv_build` and the module settings in `pyproject.toml`; verify `uv build` succeeds and `tar tzf dist/*.tar.gz | grep -c '^poop-[^/]*/tests/'` prints `0`.
- [x] 3.3 Bump `astral-sh/setup-uv` to `@v10` and use `uv sync --locked --dev` in `.github/workflows/ci.yml`; verify `uv sync --locked --dev` passes locally and CI is green after push.

## 4. Integration

- [x] 4.1 Run `uv run ruff check && uv run ruff format --check && uv run ty check poop/ tests/ && uv run pytest`, reading the `N passed` line, and `openspec validate cli-repl-streams --strict`; verify every step exits 0 and coverage stays at or above 95%.

## Workflow follow-up

- One commit per task; push, check CI.
- Archive with `/opsx:archive`; commit the archive.
