# Tasks

## 1. Decision

- [x] 1.1 Write the ADR with the `adr` skill: the next number in `doc/adr/`, dated the day it is written, status Accepted. It records that a POOP error carries its own exit code, which a subclass inherits, rather than looking it up in a table in the CLI, and that the codes are named by what they mean to a script. Run the `unslop` skill on it. Verify: the filename carries the next number, and the record cites no change name (CONTRIBUTING.md, *Closing a change*).

## 2. Implementation

- [x] 2.1 In `poop/errors.py`, add `ExitCode(IntEnum)` with `UNREADABLE = 1`, `NOT_A_PROGRAM = 2`, `REFUSED = 3` and `FAILED = 4`. Add `exit_code: ClassVar[ExitCode] = ExitCode.FAILED` on `PoopError`, and override it with `NOT_A_PROGRAM` on `ParseError` and `REFUSED` on `ValidationError`. `TransformError` and `ExecutionError` keep the inherited `FAILED`, set explicitly on each so that a reader of the class sees it. In `tests/test_errors.py`, add a test that each of the four classes, and a subclass of each defined in the test, answers the expected `exit_code`. Verify: `uv run pytest tests/test_errors.py` exits 0 with its summary line read.
- [ ] 2.2 In `poop/cli.py`, replace `exit_code(exc)` and `exit_code(errors[0])` with `exc.exit_code` and `errors[0].exit_code`, exit `_unreadable` with `ExitCode.UNREADABLE`, and remove `UNREADABLE`, `EXIT_CODES` and `exit_code()`. Move the comment that explains which failures share a code onto `ExitCode`. Verify: `git grep -nE "EXIT_CODES|UNREADABLE\b|exit_code\(" -- poop tests` is empty, and `uv run pytest tests/test_cli.py` exits 0, including `test_cli_exit_codes_tell_the_failure_kinds_apart`.

## 3. Integration

- [ ] 3.1 Run the full gate: `uv run pytest` (95% floor, summary line read), `uv run ruff check`, `uv run ruff format --check` and `uv run ty check poop/ tests/`. Also run `uv run poop nope.py; echo $?` and `printf 'print(1)\n' | uv run poop -; echo $?`. Verify: every command exits 0, and the two runs print `1` and `3`.

## Workflow follow-up

- Archive with the `openspec-archive-change` skill (CONTRIBUTING.md, *Closing a change*).
