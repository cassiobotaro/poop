# 6. Everything is an object; every operation is a message

Date: 2026-04-22

## Status

Accepted

## Context

POOP is a Python 3.15 interpreter infected by Smalltalk. It runs Python source, and Python has control flow statements and free functions that Smalltalk does not. POOP has two kinds of infection to change that: validators (`poop/validators/`) reject code incompatible with POOP, and transformers (`poop/transformers/`) rewrite the AST before execution to replace Python constructs with POOP equivalents.

## Decision

Everything is an object, and every operation is message passing.

- There are no control flow structures. Conditionals and iterations are messages sent to objects.
- There are no free functions. All behaviour lives in class methods.

Every program goes through the pipeline `parse → validate → transform → execute(namespace)`. Validators follow the `Validator` + `ast.NodeVisitor` pattern, and transformers the `Transformer` + `ast.NodeTransformer` pattern.

## Consequences

- Each Python construct that is not a message is either refused by a validator or rewritten by a transformer.
- Which constructs count as "not a message" is ADR 7; when a validator may refuse one is ADR 9.
