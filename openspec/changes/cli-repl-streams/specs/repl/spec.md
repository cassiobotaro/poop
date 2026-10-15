# Spec Delta

## ADDED Requirements

### Requirement: Every REPL diagnostic goes to stderr
A sentence the REPL writes about a failure or a misuse — an unknown
meta-command, a missing argument, an unknown `:explain` topic — SHALL go to
stderr prefixed `poop:`; only values, listings and help go to stdout.

#### Scenario: An unknown explain topic
- **WHEN** `:explain banana` is entered and stderr is discarded
- **THEN** stdout holds only the `Known constructs:` listing, and stderr (when kept) holds `poop: no :explain topic for 'banana'.`

#### Scenario: A missing argument
- **WHEN** `:methods` is entered with no argument
- **THEN** stderr holds `poop: usage: :methods <expr>` and stdout holds nothing for that input

### Requirement: The history file is the session's, not the process's
The REPL SHALL read and write the history file it was given, defaulting to
`~/.poop_history`, and SHALL touch no history and no readline state when
standard input is not a terminal.

#### Scenario: A test session leaves the user's history alone
- **WHEN** a `Repl` is built with a temporary history path and run to completion
- **THEN** `~/.poop_history` has the same content and modification time as before

### Requirement: :help names the affordances the REPL has
`:help` SHALL list `_` as the last answered value, Tab completion of
messages, and the persisted history alongside the meta-commands.

#### Scenario: help lists the three
- **WHEN** `:help` is entered
- **THEN** the output contains `_` with `last result`, `Tab` with `complete`, and `history`
