# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

POOP (Python Object Oriented Programming) is a Python 3.14 interpreter infected by Smalltalk, managed with `uv`.

## Commands

```bash
# Install dependencies
uv sync --dev

# Run
poop <file.py>
uv run python main.py <file.py>  # alternativa sem instalar

# Lint and format
uv run ruff check --fix
uv run ruff format

# Type check (examples/ excluded — uses runtime-injected names)
uv run ty check poop/ tests/

# Run tests with coverage
uv run pytest

# Run a single test
uv run pytest tests/test_file.py::test_name
```

## Tooling

- **ruff** — linting and formatting (configured in `pyproject.toml` under `[tool.ruff]`)
- **ty** — type checking
- **pytest-cov** — test coverage reporting for the `poop` module (`tests/`)
- **prek** — git hook runner using `.pre-commit-config.yaml`; hooks run `ruff check --fix`, `ruff format`, and `ty check` on every commit

## Conventions and workflow

The contributor workflow and conventions (atomic commits, imports at top, English-only `proposals.md`, Smalltalk version in every example, etc.) are documented in [`CONTRIBUTING.md`](CONTRIBUTING.md). Follow them as if you were a human contributor.

AI-specific guidance:

- Before implementing a multi-part plan, confirm scope with the user — they may want only a subset implemented (e.g., `dir` as method but `help` as function).
- When fixing tests, verify expected values against actual language semantics (e.g., ascii repr quoting style, inclusive vs exclusive interval bounds, `__radd__` requirements for `builtins.sum`) before assuming the implementation is wrong.
- When implementing new types or features, ensure they are transparent to end users (e.g., use lambda transformers, `__call__`, or syntactic sugar) rather than exposing internal class names like `Block()`.

## Architecture

Entry point is `main.py` (CLI via `argparse`). Pipeline: `parse → validate → transform → execute(namespace)`.

- `poop/parser.py` — wraps `ast.parse`
- `poop/validators/` — AST validators (reject forbidden constructs); registered in `DEFAULT_VALIDATORS`: `no_if`, `no_loops`, `no_comprehension`, `no_free_functions`, `no_print`, `no_assert`, `no_raise`, `no_try`, `no_type_alias`, `no_with`, `no_async`, `no_not`, `no_and_or`, `no_unary_minus`, `no_unary_plus`, `no_invert`, `no_is`, `no_in`, `no_global`, `no_yield`, `no_walrus`, `no_match`, `no_len`, `no_abs`, `no_hash`, `no_isinstance`, `no_issubclass`, `no_callable`, `no_id`, `no_ascii`, `no_all`, `no_any`, `no_min`, `no_max`, `no_map`, `no_filter`, `no_round`, `no_bin`, `no_breakpoint`, `no_chr`, `no_divmod`, `no_exec`, `no_exit`, `no_format`, `no_getattr`, `no_hasattr`, `no_input`, `no_dir`, `no_introspection`, `no_iter`, `no_open`, `no_pow`, `no_repr`, `no_setattr`, `no_sorted`, `no_reversed`, `no_subscript`, `no_sum`, `no_del`, `no_poop_prefix`, `no_namespace_shadow`
- `poop/transformers/` — AST transformers (rewrite nodes before execution); registered in `DEFAULT_TRANSFORMERS`: `boolean`, `none`, `complex`, `bytes`, `byte_array`, `memory_view`, `int`, `float`, `string`, `enumerate`, `zip`, `range`, `list`, `tuple`, `dict`, `set`, `frozen_set`, `raise_`, `class_`, `block`, `slice`. `try_`, `with_`, `path`, `math`, `random`, `errno`, `getpass`, `secrets`, `binascii`, `mimetypes`, `webbrowser`, `glob`, `fnmatch`, `copy`, `pprint`, `bisect`, `heapq`, `shlex`, `uuid`, `json`, `tomllib`, `hmac`, `graphlib`, `re`, `hashlib`, `datetime`, `decimal`, `sqlite3`, `string` (namespace), `difflib`, `textwrap`, `unicodedata`, `zoneinfo`, `calendar`, `array`, `weakref`, `enum`, `fractions`, and `statistics` are namespace-only — they inject `Try`/`With`/`Path`/`math`/`random`/`errno`/`getpass`/`secrets`/`binascii`/`mimetypes`/`MimeTypes`/`webbrowser`/`Browser`/`glob`/`fnmatch`/`copy`/`pprint`/`PrettyPrinter`/`bisect`/`heapq`/`shlex`/`Shlex`/`uuid`/`UUID`/`json`/`tomllib`/`hmac`/`HMAC`/`graphlib`/`TopologicalSorter`/`re`/`Pattern`/`Match`/`hashlib`/`Hash`/`datetime`/`Date`/`Time`/`DateTime`/`TimeDelta`/`TimeZone`/`decimal`/`Decimal`/`Context`/`sqlite3`/`Connection`/`Cursor`/`Row`/`string`/`Template`/`difflib`/`SequenceMatcher`/`textwrap`/`TextWrapper`/`unicodedata`/`zoneinfo`/`ZoneInfo`/`calendar`/`Calendar`/`array`/`Array`/`weakref`/`WeakRef`/`WeakSet`/`WeakKeyDictionary`/`WeakValueDictionary`/`enum`/`Enum`/`IntEnum`/`StrEnum`/`Flag`/`IntFlag`/`ReprEnum`/`auto`/`fractions`/`Fraction`/`statistics`/`NormalDist` (Python module mirrors lowercase, POOP-specific entry points PascalCase; a module that also exposes a class binds both names) into `DEFAULT_NAMESPACE` without rewriting AST. Every other type wrapper (`Int`, `List`, `Object`, ...) is bound under a mangled `_poop_*` name and unreachable from user code; lowercase Python builtins (`int`, `list`, `object`, ...) get rewritten to those mangled names.
- `poop/types/` — Smalltalk-style types: `object.py` (root), `boolean.py`, `none.py`, `complex.py`, `bytes.py`, `byte_array.py`, `memory_view.py`, `int.py`, `float.py`, `range.py`, `string.py`, `list.py`, `tuple.py`, `dict.py`, `dict_keys.py`, `dict_values.py`, `dict_items.py`, `mapping_proxy.py`, `set.py`, `frozen_set.py`, `enumerate.py`, `zip.py`, `map.py`, `filter.py`, `path.py`, `math.py`, `random.py`, `errno.py`, `getpass.py`, `secrets.py`, `binascii.py`, `mimetypes.py`, `webbrowser.py`, `glob.py`, `fnmatch.py`, `copy.py`, `pprint.py`, `bisect.py`, `heapq.py`, `shlex.py`, `uuid.py`, `json.py`, `tomllib.py`, `hmac.py`, `graphlib.py`, `re.py`, `hash.py`, `datetime.py`, `decimal.py`, `sqlite3.py`, `difflib.py`, `textwrap.py`, `unicodedata.py`, `zoneinfo.py`, `calendar.py`, `array.py`, `weakref.py`, `enum.py`, `fractions.py`, `statistics.py`, `slice.py`, `block.py`, `error.py`, `try_.py`, `with_.py`, `_iterable_mixin.py`, `_iterator_base.py`, `list_iterator.py`, `tuple_iterator.py`, `set_iterator.py`, `frozen_set_iterator.py`, `dict_key_iterator.py`, `dict_value_iterator.py`, `dict_item_iterator.py`, `dict_reverse_key_iterator.py`, `dict_reverse_value_iterator.py`, `dict_reverse_item_iterator.py`, `str_iterator.py`, `range_iterator.py`, `bytes_iterator.py`, `byte_array_iterator.py`, `memory_view_iterator.py`, `path_iterator.py`
- `poop/executor.py` — compiles and executes AST with an injectable namespace
- `poop/interpreter.py` — orchestrates the full pipeline

`examples/` contains valid POOP programs. Files there use names injected at runtime (`True`→POOP boolean, etc.) so they are excluded from `ty` and ruff `F821`.
