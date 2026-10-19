# no-try-validator Specification

## Purpose
The validator that refuses `try` statements before the program runs: what it
refuses, and the sentence it answers for each form.

## Requirements

### Requirement: try/except is refused with the Try substitute
The validator SHALL refuse a `try` statement, with any combination of
`except`, `else` and `finally` clauses, before the program runs, and SHALL
name `Try` as the substitute.

#### Scenario: A try/except
- **WHEN** a program contains `try:` / `pass` / `except ValueError:` / `pass`
- **THEN** validation fails with `try/except is forbidden — use Try(block).except_(ExcType, handler).run() instead` pointing at line 1

#### Scenario: A try/else
- **WHEN** a program contains a `try` statement with an `except` and an `else` clause
- **THEN** validation fails with the same sentence

### Requirement: try/except* is a definitive ban
The validator SHALL refuse a `try` statement with `except*` clauses with a
sentence that names no substitute, since nothing in POOP raises an exception
group.

#### Scenario: A try/except*
- **WHEN** a program contains `try:` / `pass` / `except* ValueError:` / `pass`
- **THEN** validation fails with `try/except* is forbidden — nothing in POOP raises an exception group` pointing at line 1
