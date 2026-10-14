# Spec Delta

## Purpose

The messages a `Str` value and the `str` class answer in POOP, mirroring
CPython's `str` message for message and wording every refusal as a message
sent to an object.

## ADDED Requirements

### Requirement: A string fills its template from a mapping with format_map
A `Str` SHALL answer `format_map(mapping)` with the template filled from a POOP
mapping (`Dict`, `FrozenDict` or `MappingProxy`), as `str.format_map` does, and
SHALL apply the same field-access guard `format` applies.

#### Scenario: Named fields come from the mapping
- **WHEN** a program sends `"{a}-{b}".format_map({"a": 1, "b": 2})`
- **THEN** the answer prints `1-2`

#### Scenario: A format spec applies to a mapped value
- **WHEN** a program sends `"{x:.2f}".format_map({"x": 1.5})`
- **THEN** the answer prints `1.50`

#### Scenario: Field access stays refused
- **WHEN** a program sends `"{a.__class__}".format_map({"a": 1})`
- **THEN** the same refusal `format` gives for `"{0.__class__}".format(1)` is raised

### Requirement: format_map refuses a missing name and a non-mapping in POOP's wording
`format_map` SHALL raise `KeyError` for a name the mapping lacks, worded as
`format` words a missing named argument, and SHALL raise `TypeError` for an
argument that is not a mapping, never CPython's `'int' object is not
subscriptable`.

#### Scenario: A missing name
- **WHEN** a program sends `"{a}".format_map({})`
- **THEN** a `KeyError` is raised whose message begins `the template asks for 'a', which no argument named`

#### Scenario: A non-mapping is refused
- **WHEN** a program sends `"{a}".format_map(5)`
- **THEN** a `TypeError` is raised whose message reads `#format_map expects a mapping, got an int`

#### Scenario: A list is not a mapping
- **WHEN** a program sends `"{a}".format_map([1])`
- **THEN** a `TypeError` is raised whose message reads `#format_map expects a mapping, got a list`

### Requirement: The str class builds a translation table with maketrans
The `str` class SHALL answer `maketrans(x, y=none, z=none)` with a `Dict` as
`str.maketrans` does: one mapping argument of characters or ordinals to
ordinals, strings or `none`, with character keys converted to ordinals; or two
equal-length strings mapped position by position, with an optional third string
of characters mapped to `none`.

#### Scenario: Two strings map position by position
- **WHEN** a program sends `str.maketrans("abc", "xyz")`
- **THEN** the answer prints `{97: 120, 98: 121, 99: 122}`

#### Scenario: A third string deletes
- **WHEN** a program sends `str.maketrans("a", "b", "c")`
- **THEN** the answer prints `{97: 98, 99: None}`

#### Scenario: One mapping argument converts character keys
- **WHEN** a program sends `str.maketrans({"a": "x", 98: None})`
- **THEN** the answer prints `{97: 'x', 98: None}`

### Requirement: maketrans refuses bad arguments as CPython does, with POOP's wording for the type
`maketrans` SHALL raise CPython's own `ValueError` for strings of unequal
length and for a string key longer than one character, since those sentences
name no construct POOP forbids, and SHALL refuse a single argument that is not
a mapping with POOP's wording.

#### Scenario: Unequal strings
- **WHEN** a program sends `str.maketrans("ab", "xyz")`
- **THEN** a `ValueError` is raised whose message reads `the first two maketrans arguments must have equal length`

#### Scenario: A multi-character key
- **WHEN** a program sends `str.maketrans({"ab": "x"})`
- **THEN** a `ValueError` is raised whose message reads `string keys in translatetable must be of length 1`

#### Scenario: A single non-mapping argument
- **WHEN** a program sends `str.maketrans(5)`
- **THEN** a `TypeError` is raised whose message reads `#maketrans expects a mapping, got an int`

### Requirement: A string maps its characters through a table with translate
A `Str` SHALL answer `translate(table)` with a `Str` whose characters are
looked up by ordinal in `table`, a POOP mapping or sequence: a hit of `none`
deletes the character, a miss leaves it, as `str.translate` does.

#### Scenario: A maketrans table
- **WHEN** a program sends `"abc".translate(str.maketrans("abc", "xyz"))`
- **THEN** the answer prints `xyz`

#### Scenario: A mapping to none deletes
- **WHEN** a program sends `"a-b".translate({45: None})`
- **THEN** the answer prints `ab`

#### Scenario: A miss leaves the character
- **WHEN** a program sends `"abc".translate({97: 120})`
- **THEN** the answer prints `xbc`

### Requirement: translate refuses a table that is neither mapping nor sequence
`translate` SHALL raise `TypeError` in POOP's wording for a table that is not a
mapping or a sequence, and SHALL keep CPython's sentence for a mapped value of
the wrong kind, which names no construct POOP forbids.

#### Scenario: An int is no table
- **WHEN** a program sends `"abc".translate(5)`
- **THEN** a `TypeError` is raised whose message reads `#translate expects a mapping or a sequence, got an int`

#### Scenario: A mapped value of the wrong kind
- **WHEN** a program sends `"abc".translate({97: 5.5})`
- **THEN** a `TypeError` is raised whose message reads `character mapping must return integer, None or str`
