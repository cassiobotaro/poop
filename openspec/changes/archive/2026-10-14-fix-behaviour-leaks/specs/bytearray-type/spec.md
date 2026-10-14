# Spec Delta

## ADDED Requirements

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
