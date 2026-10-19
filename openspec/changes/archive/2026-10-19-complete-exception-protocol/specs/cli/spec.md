# Spec Delta

## ADDED Requirements

### Requirement: The run-time report lists the exception chain
When a program fails at run time, the report SHALL list, under the
`poop: <Kind>: <message>` line and its source line, one line per link of the
chain, final exception first: `caused by <Kind>: <message>` for an explicit
cause, otherwise `while handling <Kind>: <message>` for a context that was
not suppressed. A suppressed link SHALL end the chain.

#### Scenario: An exception raised inside a handler
- **WHEN** `poop prog.py 2>err` runs on `Try(lambda: 1 / 0).except_(ZeroDivisionError, lambda e: KeyError.raise_("outer")).run()`
- **THEN** `err` holds `poop: KeyError: outer`, then the source line, then `  while handling ZeroDivisionError: division by zero`, and the exit code is 4

#### Scenario: An explicit cause
- **WHEN** the handler in the same program runs `KeyError("outer").raise_from(e)` instead
- **THEN** the last line of `err` is `  caused by ZeroDivisionError: division by zero`

#### Scenario: A suppressed context
- **WHEN** the handler in the same program runs `KeyError("outer").raise_from(None)` instead
- **THEN** `err` holds only `poop: KeyError: outer` and the source line

#### Scenario: An error POOP composed
- **WHEN** `poop prog.py 2>err` runs on `[1].at(5)`
- **THEN** `err` holds only `poop: IndexError: list has no element at 5 — it has 1 element` and the source line, with no link naming CPython's own exception
