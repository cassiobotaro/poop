# POOP — Copilot Instructions

POOP (**P**ython **O**bject **O**riented **P**rogramming) is a Python 3.14 interpreter infected by Smalltalk. It takes valid Python syntax and enforces a strict message-passing style by rejecting procedural constructs and rewriting literals/calls at the AST level before execution.

## Commands

```bash
uv sync --dev               # install dependencies
uv run python main.py <file.py>  # run without installing
poop <file.py>              # run after installing

uv run ruff check --fix     # lint + autofix
uv run ruff format          # format
uv run ty check poop/ tests/  # type check (examples/ excluded)
uv run pytest               # tests with coverage
uv run pytest tests/test_validators/test_no_if.py::test_name  # single test
```

Git hooks (`prek`) run ruff and ty on every commit.

## Pipeline

```
source → parse → validate → transform → execute(namespace)
```

- **`poop/parser.py`** — wraps `ast.parse`
- **`poop/validators/`** — `ast.NodeVisitor` subclasses that raise `ValidationError` on forbidden constructs
- **`poop/transformers/`** — `ast.NodeTransformer` subclasses that rewrite AST nodes before execution
- **`poop/types/`** — Smalltalk-style runtime types
- **`poop/executor.py`** — compiles and `exec()`s the transformed AST with an injectable namespace
- **`poop/interpreter.py`** — orchestrates: accepts optional custom validators/transformers/namespace

`DEFAULT_VALIDATORS` and `DEFAULT_TRANSFORMERS` are registered lists in `poop/validators/__init__.py` and `poop/transformers/__init__.py`. New infections must be added to these lists to take effect.

## Adding a Validator

1. Create `poop/validators/no_<thing>.py` with a `No<Thing>Validator` class and a private `_No<Thing>Visitor(ast.NodeVisitor)`.
2. Raise `ValidationError(message, lineno=node.lineno, col_offset=node.col_offset)` from the visitor.
3. Register the validator instance in `DEFAULT_VALIDATORS` in `poop/validators/__init__.py`.
4. Add a test file `tests/test_validators/test_no_<thing>.py`.
5. Document the infection in `INFECTIONS.md`.

**Rule**: only activate a validator when the substitute already exists. No blocking without an alternative.

## Adding a Transformer

1. Create `poop/transformers/<thing>.py` with a `<Thing>Transformer` class and a private `_<Thing>Rewriter(ast.NodeTransformer)`.
2. Define `BINDINGS: ClassVar[dict[str, object]]` on the transformer — these are injected into the runtime namespace so the rewritten AST can resolve the replacement names.
3. Call `ast.fix_missing_locations(tree)` before returning from `transform()`.
4. Register the transformer in `DEFAULT_TRANSFORMERS` and merge its `BINDINGS` into `DEFAULT_NAMESPACE` in `poop/transformers/__init__.py`.

## Adding a Type

1. Create `poop/types/<type>.py` with the class inheriting from `Object` (or another POOP type).
2. Declare `__slots__` — instance variables are fixed; dynamic attribute addition is not allowed.
3. All explicitly-named POOP methods must return POOP types, **never** raw Python primitives.
4. Python protocol dunders (`__bool__`, `__hash__`, `__len__`, `__str__`, `__int__`, `__float__`, `__contains__`, `__repr__`) must return native Python types — Python itself requires this.
5. `__str__` and `__repr__` must both be implemented (`__repr__` delegates to `__str__`).

## Key Conventions

**Naming — Python, not Smalltalk.** Method names follow Python idioms: `map` not `collect`, `filter` not `select`, `filter_false` not `reject`, `find` not `detect`, `reduce` not `inject_into`. Exception: `do` (Smalltalk iteration) is used because `for` is a keyword and `for_each` has no Python precedent.

**Every literal is transformed.** `1`, `3.14`, `"hello"`, `True`, `False`, `None`, `[1,2]`, `(1,2)`, `{1,2}`, `{k:v}`, `b"..."`, `1+2j` are all rewritten to their POOP equivalents before execution. No naked Python primitive reaches runtime.

**Class inheritance is implicit.** `class Foo:` is rewritten to `class Foo(Object):` by `ClassTransformer`. `class Foo(object):` is also rewritten to `class Foo(Object):`. Classes with an explicit non-`object` base are left unchanged. `Object` is injected into `DEFAULT_NAMESPACE`.

**Constructor builtins are intercepted, not banned.** `int()`, `str()`, `list()`, etc. are object instantiation — transformers rewrite them to POOP factory functions (`_poop_int_from`, `_poop_str_from`, …).

**Singletons.** `true`, `false`, and `none` are unique objects. Identity checks rely on this — there is exactly one instance of each.

**`ty` type-checking suppression.** `invalid-method-override` is globally ignored in `pyproject.toml` because POOP deliberately overrides `__eq__`/`__ne__`/`__lt__` etc. to return `Boolean` (a Smalltalk-style type) instead of `bool`, violating LSP by design.

**`examples/` is excluded from linters and `ty`.** Files there use names injected at runtime (`true`, `false`, `none`, POOP type constructors) that aren't resolvable statically.

**Commits are atomic and in English.** One validator, one type, one bug fix per commit — never group unrelated changes.
