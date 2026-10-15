# Spec Delta

## ADDED Requirements

### Requirement: index and rindex miss in the family's words
`index` and `rindex` on a `Str` SHALL refuse an absent substring with the
sentence every sequence's `index` uses, never `substring not found`.

#### Scenario: index misses
- **WHEN** a program runs `"ab".index("z")`
- **THEN** a `ValueError` is raised reading `str has no element equal to 'z'`

#### Scenario: rindex misses
- **WHEN** a program runs `"ab".rindex("z")`
- **THEN** a `ValueError` is raised reading `str has no element equal to 'z'`
