# bytearray-type Specification

## Purpose

The messages a `ByteArray` answers in POOP, mirroring CPython's `bytearray`
message for message and wording every refusal as a message sent to an object.

## Requirements

### Requirement: A bytearray resizes in place with resize
A `ByteArray` SHALL answer `resize(size)` by changing its own length to `size`,
as Python 3.15's `bytearray.resize` does: a larger size appends zero bytes, a
smaller size drops the tail. It is a void mutator and SHALL answer `none`.

#### Scenario: Growing pads with zero bytes
- **WHEN** a program sends `resize(4)` to `bytearray(b"ab")`
- **THEN** the receiver prints `bytearray(b'ab\x00\x00')` and the answer is `none`

#### Scenario: Shrinking drops the tail
- **WHEN** a program sends `resize(1)` to `bytearray(b"ab")`
- **THEN** the receiver prints `bytearray(b'a')`

#### Scenario: Resizing to zero empties the receiver
- **WHEN** a program sends `resize(0)` to `bytearray(b"ab")`
- **THEN** the receiver has length `0`

#### Scenario: A boolean is the integer it stands for
- **WHEN** a program sends `resize(True)` to `bytearray(b"ab")`
- **THEN** the receiver prints `bytearray(b'a')`

### Requirement: resize refuses a non-integer size in POOP's wording
`resize` SHALL refuse a size that is not an integer with a `TypeError` worded
as the other integer arguments in the language are, and never CPython's
`'str' object cannot be interpreted as an integer`.

#### Scenario: A string size is refused
- **WHEN** a program sends `resize("a")` to a `bytearray`
- **THEN** a `TypeError` is raised whose message reads `#resize's size must be an int, got a str`

#### Scenario: A float size is refused
- **WHEN** a program sends `resize(2.0)` to a `bytearray`
- **THEN** a `TypeError` is raised whose message reads `#resize's size must be an int, got a float`

### Requirement: resize keeps CPython's refusal of a negative size
A negative size SHALL raise a `ValueError` with CPython's own sentence, since
it names no construct POOP forbids, and the receiver SHALL be left unchanged.

#### Scenario: A negative size is refused
- **WHEN** a program sends `resize(-1)` to `bytearray(b"ab")`
- **THEN** a `ValueError` is raised whose message reads `Can only resize to positive sizes, got -1` and the receiver still prints `bytearray(b'ab')`

### Requirement: The bytearray class builds a translation table with maketrans
The `bytearray` class SHALL answer `maketrans(frm, to)` exactly as the `bytes`
class does, answering a `Bytes` of length 256, since CPython's
`bytearray.maketrans` answers `bytes`.

#### Scenario: The table is bytes, not bytearray
- **WHEN** a program sends `bytearray.maketrans(b"ab", b"xy").class_name()`
- **THEN** the answer prints `bytes`

### Requirement: A bytearray maps its bytes through a table with translate
A `ByteArray` SHALL answer `translate(table, delete=b"")` with a new
`ByteArray`, mapping and deleting as `Bytes.translate` does, leaving the
receiver unchanged.

#### Scenario: The answer is a new bytearray
- **WHEN** a program sends `translate(bytes.maketrans(b"ab", b"xy"))` to `bytearray(b"abc")`
- **THEN** the answer prints `bytearray(b'xyc')` and the receiver still prints `bytearray(b'abc')`

#### Scenario: Deleting with no table
- **WHEN** a program sends `translate(None, b"b")` to `bytearray(b"abc")`
- **THEN** the answer prints `bytearray(b'ac')`

#### Scenario: A short table keeps CPython's refusal
- **WHEN** a program sends `translate(b"short")` to `bytearray(b"abc")`
- **THEN** a `ValueError` is raised whose message reads `translation table must be 256 characters long`

### Requirement: hex accepts a str or bytes separator only
A `ByteArray`'s `hex(sep)` SHALL accept a `Str` or a `Bytes` separator and
refuse any other, as `Bytes.hex` does and as CPython's `bytearray.hex` does.

#### Scenario: A bytes separator
- **WHEN** a program runs `bytearray(b"ab").hex(b":").print()`
- **THEN** the output is `61:62`

#### Scenario: A bytearray separator is refused
- **WHEN** a program runs `bytearray(b"ab").hex(bytearray(b":"))`
- **THEN** a `TypeError` is raised whose message reads `#hex expects a one-character separator, got a bytearray`

#### Scenario: The same refusal on bytes
- **WHEN** a program runs `b"ab".hex(bytearray(b":"))`
- **THEN** a `TypeError` is raised whose message reads `#hex expects a one-character separator, got a bytearray`
