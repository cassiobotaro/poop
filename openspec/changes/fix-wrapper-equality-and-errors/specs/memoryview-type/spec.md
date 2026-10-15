# Spec Delta

## ADDED Requirements

### Requirement: A memoryview finds a Boolean needle
`includes`, `count` and `index` on a `MemoryView` SHALL treat a `Boolean`
as the integer it stands for, as `bytes` and `bytearray` do.

#### Scenario: includes
- **WHEN** a program prints `memoryview(b"\x01").includes(True)`
- **THEN** it prints `True`

#### Scenario: count and index
- **WHEN** a program prints `memoryview(b"\x01\x01").count(True)` and `memoryview(b"\x00\x01").index(True)`
- **THEN** they print `2` and `1`
