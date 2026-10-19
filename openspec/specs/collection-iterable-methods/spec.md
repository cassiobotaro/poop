# collection-iterable-methods Specification

## Purpose

The messages every POOP collection answers through the shared iterable
protocol: walking, mapping, folding and summing its elements.

## Requirements

### Requirement: sum never mutates an element or the start value
A collection's `sum()` SHALL add its elements with the binary `+` of the
running total, never with an in-place operation, so neither the first element
nor a `start` the program passed is changed by the sum, as `builtins.sum`
behaves.

#### Scenario: Summing lists leaves the first list alone
- **WHEN** a program runs `a = [1]`, `b = [2]`, `s = [a, b].sum()` and then `a.print()`
- **THEN** the output is `1`, and `s.is_identical(a).print()` prints `False`

#### Scenario: Summing with a start value leaves it alone
- **WHEN** a program runs `acc = [0]`, `[[1], [2]].sum(acc)` and then `acc.print()`
- **THEN** the output is `0`

#### Scenario: Numbers sum as before
- **WHEN** a program runs `[1, 2, 3].sum().print()`
- **THEN** the output is `6`

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
