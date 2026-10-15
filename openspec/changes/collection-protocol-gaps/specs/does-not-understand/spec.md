# Spec Delta

## Purpose

The hint a `does not understand` refusal carries: the POOP spelling of a
Smalltalk selector, the substitute for a foreign-language name, or the
nearest message.

## ADDED Requirements

### Requirement: Common Smalltalk collection selectors are mapped
A refusal of `first`, `last`, `isEmpty`, `notEmpty`, `removeFirst`,
`removeLast`, `copyFrom`, `atIfAbsent`, `atIfAbsentPut`, `removeKey`,
`keysAndValuesDo`, `anySatisfy`, `allSatisfy`, `detectIfNone`, `asArray`,
`asSet`, `timesRepeat`, `toDo` or `ifNilIfNotNil` SHALL name the POOP
message or spelling that answers it.

#### Scenario: A selector whose twin is a spelling
- **WHEN** a program sends `first()` to `[1]`
- **THEN** an `AttributeError` is raised reading `list does not understand #first — Smalltalk's #first is .at(0) here`

#### Scenario: A selector whose twin is a message
- **WHEN** a program sends `isEmpty()` to `[1]`
- **THEN** an `AttributeError` is raised reading `list does not understand #isEmpty — Smalltalk's #isEmpty is #len here`

#### Scenario: A loop selector on an int
- **WHEN** a program sends `timesRepeat(lambda: 1)` to `(3)`
- **THEN** an `AttributeError` is raised reading `int does not understand #timesRepeat — Smalltalk's #timesRepeat is range(n).do(lambda i: …) here`

#### Scenario: A dict selector
- **WHEN** a program sends `atIfAbsent(1, 2)` to `{}`
- **THEN** an `AttributeError` is raised reading `dict does not understand #atIfAbsent — Smalltalk's #atIfAbsent is #get here`

### Requirement: A lazy view says how to materialise
A refusal of `len`, `at`, `reversed`, `includes` or `sorted` on a `map`,
`filter`, `zip` or `enumerate` SHALL say the view is lazy and name
`list(...)`.

#### Scenario: len on a map
- **WHEN** a program sends `len()` to `[1, 2].map(lambda x: x)`
- **THEN** an `AttributeError` is raised reading `map does not understand #len — a map is lazy; materialize it with list(...) first`

#### Scenario: at on a filter
- **WHEN** a program sends `at(0)` to `[1, 2].filter(lambda x: x)`
- **THEN** an `AttributeError` is raised reading `filter does not understand #at — a filter is lazy; materialize it with list(...) first`
