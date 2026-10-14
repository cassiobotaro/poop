# bytes-type Specification

## Purpose

The messages a `Bytes` value and the `bytes` class answer in POOP, mirroring
CPython's `bytes` message for message and wording every refusal as a message
sent to an object.

## Requirements

### Requirement: The bytes class builds a 256-byte translation table with maketrans
The `bytes` class SHALL answer `maketrans(frm, to)` with a `Bytes` of length
256 mapping each byte of `frm` to the byte at the same position in `to`, as
`bytes.maketrans` does.

#### Scenario: Two equal-length byte strings
- **WHEN** a program sends `bytes.maketrans(b"ab", b"xy")`
- **THEN** the answer has length `256` and its first four bytes print `b'\x00\x01\x02\x03'`

#### Scenario: Unequal lengths keep CPython's refusal
- **WHEN** a program sends `bytes.maketrans(b"a", b"xy")`
- **THEN** a `ValueError` is raised whose message reads `maketrans arguments must have same length`

#### Scenario: A str argument is refused in POOP's wording
- **WHEN** a program sends `bytes.maketrans("a", b"x")`
- **THEN** a `TypeError` is raised whose message is the one the shared bytes-like guard gives for `#maketrans`, naming `str`, and never CPython's `a bytes-like object is required, not 'str'`

### Requirement: Bytes map their bytes through a table with translate
A `Bytes` SHALL answer `translate(table, delete=b"")` with a `Bytes`: each
byte mapped through the 256-byte `table`, or left as is when `table` is
`none`, after removing every byte in `delete`, as `bytes.translate` does.

#### Scenario: A maketrans table
- **WHEN** a program sends `b"abc".translate(bytes.maketrans(b"ab", b"xy"))`
- **THEN** the answer prints `b'xyc'`

#### Scenario: Deleting with no table
- **WHEN** a program sends `b"abc".translate(None, b"b")`
- **THEN** the answer prints `b'ac'`

#### Scenario: Table and delete together
- **WHEN** a program sends `b"abc".translate(bytes.maketrans(b"ab", b"xy"), delete=b"c")`
- **THEN** the answer prints `b'xy'`

### Requirement: translate refuses a bad table
`translate` SHALL keep CPython's `ValueError` for a table that is not 256 bytes
long, which names no construct POOP forbids, and SHALL refuse a non-bytes table
in POOP's wording.

#### Scenario: A short table
- **WHEN** a program sends `b"abc".translate(b"short")`
- **THEN** a `ValueError` is raised whose message reads `translation table must be 256 characters long`

#### Scenario: An int is no table
- **WHEN** a program sends `b"abc".translate(5)`
- **THEN** a `TypeError` is raised whose message is the one the shared bytes-like guard gives for `#translate`, naming `int`, and never CPython's `a bytes-like object is required, not 'int'`
