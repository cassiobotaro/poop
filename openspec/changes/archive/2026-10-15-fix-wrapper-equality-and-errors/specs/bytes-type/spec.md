# Spec Delta

## ADDED Requirements

### Requirement: index and rindex miss in the family's words
`index` and `rindex` on a `Bytes` or a `ByteArray` SHALL refuse an absent
subsequence with the sentence every sequence's `index` uses, never
`subsection not found`.

#### Scenario: bytes index misses
- **WHEN** a program runs `b"ab".index(b"z")`
- **THEN** a `ValueError` is raised reading `bytes has no element equal to b'z'`

#### Scenario: bytearray rindex misses
- **WHEN** a program runs `bytearray(b"ab").rindex(b"z")`
- **THEN** a `ValueError` is raised reading `bytearray has no element equal to b'z'`
