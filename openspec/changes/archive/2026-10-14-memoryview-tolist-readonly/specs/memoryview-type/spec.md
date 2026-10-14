# Spec Delta

## Purpose

The messages a `MemoryView` answers in POOP, mirroring CPython's `memoryview`
over a one-dimensional byte view and wording every refusal as a message sent
to an object.

## ADDED Requirements

### Requirement: A memoryview materializes its bytes as a list with tolist
A `MemoryView` SHALL answer `tolist()` with a `List` holding one `Int` per
byte of the view, in order, as `memoryview.tolist` does for a byte view. It
takes no argument.

#### Scenario: A view over bytes
- **WHEN** a program sends `memoryview(b"ab").tolist()`
- **THEN** the answer is the list `[97, 98]`, whose `class_name()` prints `list` and whose `print()` prints `97 98`, as a `List` prints

#### Scenario: A view over a bytearray
- **WHEN** a program sends `memoryview(bytearray(b"hi")).tolist()`
- **THEN** the answer is the list `[104, 105]`

#### Scenario: A sliced view lists only its own bytes
- **WHEN** a program sends `memoryview(b"abc").slice(1).tolist()`
- **THEN** the answer is the list `[98, 99]`

#### Scenario: An empty view
- **WHEN** a program sends `memoryview(b"").tolist()`
- **THEN** the answer is the empty list `[]`, whose `len()` is `0`

### Requirement: A memoryview says whether its bytes can change with readonly
A `MemoryView` SHALL answer `readonly()` with a `Boolean`: `true` when the
view is over `bytes`, `false` when it is over a `bytearray`, as CPython's
`memoryview.readonly` reports. It is a message, not an attribute, like every
other accessor in the language.

#### Scenario: A view over bytes is read-only
- **WHEN** a program sends `memoryview(b"ab").readonly()`
- **THEN** the answer prints `True`

#### Scenario: A view over a bytearray is not
- **WHEN** a program sends `memoryview(bytearray(b"ab")).readonly()`
- **THEN** the answer prints `False`

#### Scenario: A slice keeps the answer of the view it came from
- **WHEN** a program sends `memoryview(bytearray(b"abc")).slice(1).readonly()`
- **THEN** the answer prints `False`

#### Scenario: The uncalled spelling is the message itself, not the answer
- **WHEN** a program sends `memoryview(b"ab").readonly.print()`
- **THEN** the output is `<block>`, as for any message read off an object without being sent, and no `Boolean` is answered
