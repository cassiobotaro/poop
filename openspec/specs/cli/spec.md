# cli Specification

## Purpose
What the `poop` command reads, where its output and its diagnostics go,
and how it exits, so a shell script, an editor or CI can drive it.

## Requirements

### Requirement: Non-tty standard input runs as a program
When standard input is not a terminal and no file is given, or when the
file argument is `-`, `poop` SHALL read standard input as a source file and
run it, writing no banner and no prompt.

#### Scenario: A piped program
- **WHEN** `printf '"x".print()\n' | poop` runs
- **THEN** stdout is exactly `x` followed by a newline, stderr is empty and the exit code is 0

#### Scenario: An explicit dash
- **WHEN** `poop - < prog.py` runs
- **THEN** it behaves as `poop prog.py` does

#### Scenario: An interactive terminal gets the REPL
- **WHEN** `poop` runs with a terminal on standard input
- **THEN** the banner `POOP 💩  — Python infected by Smalltalk. Ctrl+D to exit.` and the `>>> ` prompt appear

### Requirement: A mode flag needs a file
`--validators-only` and `--transformers-only` SHALL refuse to run without a
source, rather than starting the REPL.

#### Scenario: Flag with no file on a terminal
- **WHEN** `poop --validators-only` runs with a terminal on standard input
- **THEN** stderr carries `--validators-only needs a file or piped input` and the exit code is 2

### Requirement: Diagnostics go to stderr, values to stdout
Every line that reports a failure SHALL be written to stderr, prefixed
`poop:`, red when stderr is a terminal; program output and the
`No validation errors.` line SHALL go to stdout.

#### Scenario: An unreadable file
- **WHEN** `poop nope.py 2>err` runs
- **THEN** stdout is empty, `err` holds `poop: cannot read 'nope.py': No such file or directory` and the exit code is 1

#### Scenario: A validation error
- **WHEN** `poop prog.py 2>err` runs on a file containing `print(1)`
- **THEN** stdout is empty and `err` holds the `poop: print is forbidden` report with its source line and caret

### Requirement: Exit codes tell the failure kinds apart
`poop` SHALL exit 0 on success, 1 when the source cannot be read, 2 on a
parse error or a usage error, 3 when validation fails and 4 when the
program fails at run time.

#### Scenario: Each kind
- **WHEN** `poop` runs on a missing file, a file with `x = (`, a file with `print(1)` and a file with `(1).at(0)`
- **THEN** the exit codes are 1, 2, 3 and 4 respectively

### Requirement: --format json reports validation errors as data
With `--validators-only --format json`, `poop` SHALL write to stdout one
JSON array of objects with `line`, `col`, `message` and `validator` keys,
sorted by position, and an empty array when the file is clean.

#### Scenario: Two errors
- **WHEN** `poop --validators-only --format json prog.py` runs on a file whose line 1 is `print(1)` and line 2 is `x = len([])`
- **THEN** stdout parses as `[{"line": 1, "col": 0, "message": "print is forbidden — use obj.print() instead", "validator": "no_print"}, {"line": 2, "col": 4, "message": "len() is forbidden — use obj.len() instead", "validator": "no_len"}]` and the exit code is 3

#### Scenario: A clean file
- **WHEN** the same command runs on `"x".print()`
- **THEN** stdout is `[]` and the exit code is 0

### Requirement: --version and -c
`poop --version` SHALL print `poop <version>` from the installed package
metadata and exit 0; `poop -c "<code>"` SHALL run `<code>` as a program
named `<string>`.

#### Scenario: Version
- **WHEN** `poop --version` runs
- **THEN** stdout matches `poop \d+\.\d+.*` and the exit code is 0

#### Scenario: Inline code
- **WHEN** `poop -c '"abc".len().print()'` runs
- **THEN** stdout is `3` and the exit code is 0

### Requirement: python -m poop is the module entry point
`python -m poop …` SHALL behave exactly as `poop …` does.

#### Scenario: Running an example through -m
- **WHEN** `python -m poop examples/basics/hello_world.py` runs
- **THEN** stdout is `Hello, World!` and the exit code is 0
