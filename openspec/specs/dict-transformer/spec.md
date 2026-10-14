# dict-transformer Specification

## Purpose

How a `dict(...)` call and a `{...}` display are rewritten into POOP's
`Dict`, and what a keyword splat in that call answers.

## Requirements

### Requirement: A keyword splat in a dict call behaves as in any call
`dict(a, k=v, **b)` SHALL be built by the same `**` unpacking every call
goes through, so a non-string key and a duplicated keyword are refused as
CPython refuses them, and a well-formed call merges left to right.

#### Scenario: A splat with string keys merges
- **WHEN** a program runs `b = {"y": 2}` and then `dict({"x": 1}, **b).print()`
- **THEN** the output is `{'x': 1, 'y': 2}`

#### Scenario: A keyword overridden by a later splat
- **WHEN** a program runs `dict({"a": 0}, x=1, **{"x": 2})`
- **THEN** a `TypeError` is raised whose message reads `dict() got multiple values for keyword argument 'x'`

#### Scenario: A splat with a non-string key
- **WHEN** a program runs `dict(**{1: 2})`
- **THEN** a `TypeError` is raised whose message reads `keywords must be strings`, as `f(**{1: 2})` answers for any `f`

#### Scenario: A display with a splat is unchanged
- **WHEN** a program runs `b = {"y": 2}` and then `{"x": 1, **b}.print()`
- **THEN** the output is `{'x': 1, 'y': 2}`
