# Spec Delta

## ADDED Requirements

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
