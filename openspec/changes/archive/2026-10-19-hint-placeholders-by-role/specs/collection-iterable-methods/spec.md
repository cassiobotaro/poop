# Spec Delta

## MODIFIED Requirements

### Requirement: find answers a default on a miss
`find(block, default=…)` SHALL answer `default` when no element satisfies
the block, and the first satisfying element otherwise, so a program can tell
"nothing matched" from "matched `none`"; without `default`, a miss SHALL
answer `none` as before.

#### Scenario: A miss with a default
- **WHEN** a program prints `[1, 2].find(lambda x: x > 5, default=0)`
- **THEN** it prints `0`

#### Scenario: A match that is none
- **WHEN** a program prints `[None, 1].find(lambda x: x.is_none(), default="missing")`
- **THEN** it prints `None`

#### Scenario: A miss without a default
- **WHEN** a program prints `[1, 2].find(lambda x: x > 5)`
- **THEN** it prints `None`

#### Scenario: default is keyword-only
- **WHEN** a program sends `find(lambda x: x, 0)` to `[1]`
- **THEN** a `TypeError` is raised reading `#find takes a block and an optional default= — write .find(lambda item: …, default=…)`
