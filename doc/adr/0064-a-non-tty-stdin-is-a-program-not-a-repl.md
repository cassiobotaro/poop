# 64. A non-tty stdin is a program, not a REPL

Date: 2026-10-15

## Status

Accepted

## Context

`poop` with no file started the REPL whatever its standard input was. A program piped into `poop` therefore got a banner and a prompt on stdout between its own lines, which is what `python3 < file` never does.

The `2026-10-15-cli-repl-streams` change considered keeping the REPL on a pipe with its prompts moved to stderr. That keeps `printf ':methods 5' | poop` working, but leaves the banner problem for every consumer that merges streams. Nothing in the test suite pipes meta-commands: the REPL tests drive `Repl` directly through `feed_input`.

## Decision

When standard input is not a terminal, `poop` reads it as a source file and runs it, with no banner and no prompt, as CPython does. `poop -` does the same explicitly. The REPL is what an interactive stdin gets.

`-c`, `-` and a non-tty stdin share `main`'s source-reading step in `poop/cli.py`: a `_source_from(file, code)` helper answers `(source, filename)` for a path, `-`, `-c` or a non-tty stdin, in that precedence, so the run paths below it are unchanged. When stdin is not a terminal, readline is not touched.

## Consequences

`echo 'x.print()' | poop` behaves like `python3 < file`, and a shell script can run `poop` on a pipe and parse its stdout.

Piping meta-commands into the REPL is removed on purpose; the README's REPL section documents it, and `poop -c` covers the one-liner case.
