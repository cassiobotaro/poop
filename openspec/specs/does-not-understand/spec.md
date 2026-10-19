# does-not-understand Specification

## Purpose
The hint a `does not understand` refusal carries: the POOP spelling of a
Smalltalk selector, the substitute for a foreign-language name, or the
nearest message.

## Requirements

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
- **THEN** an `AttributeError` is raised reading `int does not understand #timesRepeat — Smalltalk's #timesRepeat is range(n).do(lambda item: …) here`

#### Scenario: A range selector with bounds
- **WHEN** a program sends `toDo(3, lambda i: i)` to `(1)`
- **THEN** an `AttributeError` is raised reading `int does not understand #toDo — Smalltalk's #toDo is range(a, b).do(lambda item: …) here`

#### Scenario: A search selector
- **WHEN** a program sends `detectIfNone(1, 2)` to `[1]`
- **THEN** an `AttributeError` is raised reading `list does not understand #detectIfNone — Smalltalk's #detectIfNone is .find(lambda item: …, default=…) here`

#### Scenario: A dict selector
- **WHEN** a program sends `atIfAbsent(1, 2)` to `{}`
- **THEN** an `AttributeError` is raised reading `dict does not understand #atIfAbsent — Smalltalk's #atIfAbsent is #get here`

### Requirement: A lazy view says how to materialise
A refusal of `len`, `at`, `reversed`, `includes`, `count` or `index` on a `map`,
`filter`, `zip` or `enumerate` SHALL say the view is lazy and name
`list(...)`.

#### Scenario: len on a map
- **WHEN** a program sends `len()` to `[1, 2].map(lambda x: x)`
- **THEN** an `AttributeError` is raised reading `map does not understand #len — a map is lazy; materialize it with list(...) first`

#### Scenario: at on a filter
- **WHEN** a program sends `at(0)` to `[1, 2].filter(lambda x: x)`
- **THEN** an `AttributeError` is raised reading `filter does not understand #at — a filter is lazy; materialize it with list(...) first`
