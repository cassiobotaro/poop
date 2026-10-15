# Spec Delta

## ADDED Requirements

### Requirement: at_put blames the argument at fault
`at_put(index, byte)` on a `ByteArray` SHALL refuse a non-int `byte` by
naming the byte, and a non-int `index` by naming the index.

#### Scenario: A str byte
- **WHEN** a program runs `bytearray(b"a").at_put(0, "x")`
- **THEN** a `TypeError` is raised reading `#at_put's byte must be an int, got a str`

#### Scenario: A float index
- **WHEN** a program runs `bytearray(b"a").at_put(1.5, 1)`
- **THEN** a `TypeError` is raised reading `bytearray.at_put expects an int index, got a float`
