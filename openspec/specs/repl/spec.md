# repl Specification

## Purpose

The process-wide state the REPL changes for the length of a session and
puts back when it ends.

## Requirements

### Requirement: The REPL leaves sys.ps1 and sys.ps2 as it found them
When a session ends, `sys.ps1` and `sys.ps2` SHALL hold what they held before
it, and SHALL be absent when they were absent before, so a library that asks
`hasattr(sys, "ps1")` to detect an interactive interpreter is answered as it
was before the session.

#### Scenario: A process that had no prompts
- **WHEN** a REPL session is run in a process where `hasattr(sys, "ps1")` is `False` and `hasattr(sys, "ps2")` is `False`
- **THEN** after the session both answer `False` again, and `sys.displayhook` is the one from before

#### Scenario: A process that had prompts
- **WHEN** a REPL session is run in a process where `sys.ps1` is `"P> "`
- **THEN** after the session `sys.ps1` is `"P> "`
