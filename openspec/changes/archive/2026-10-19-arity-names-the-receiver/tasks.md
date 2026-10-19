# Tasks

## 1. The callee names the class CPython would name

- [x] 1.1 In `_MethodBlock.__call__` (`poop/types/block.py`), catch a binding-time `TypeError` (no traceback frame below `__call__`, text starting with the function's `__qualname__` and `()`) and re-raise `mirrors.TypeError` `from None` with the prefix chosen by the design's rule: the class for a class receiver; for an instance, the current prefix when the owner is the root `Object` or a program's class, else the nearest wrapper in the receiver's MRO. Rewrite `_MethodBlock`'s docstring to state the rule. Add the `message-arity` delta's scenarios for mixin messages (`list.map()`, `list_iterator.has_next()`, `dict_keys.mapping()`) and kept names (`object.repr()`, `list.append()` on `class Stack(list)`, `Try.except_()`) to a new `tests/test_types/test_message_arity.py`, plus one unexpected-keyword case and one case where a method body's own `TypeError` passes through untouched. Verify with `uv run pytest tests/test_types/test_message_arity.py tests/test_types/test_block.py tests/test_types/test_object.py -q`.
- [x] 1.2 Add the `bytearray.lower()` and `frozendict.keys()` scenarios to `tests/test_types/test_message_arity.py`, and confirm the 1.1 rule covers them with no code of their own; if it does not, extend the rule rather than special-casing the two classes. Verify with `uv run pytest tests/test_types/test_message_arity.py -q`.
- [x] 1.3 Add the class-side scenarios (`int.hash()`, a program's `Foo.repr()`) to `tests/test_types/test_message_arity.py`, and update the `class_side.__set_name__` comment in `poop/types/meta.py`, which says naming the class is unavailable, to point at `_MethodBlock`. Verify with `uv run pytest tests/test_types/test_message_arity.py tests/test_types/test_meta.py -q`.

## 2. print is keyword-only

- [x] 2.1 Make `end`, `sep` and `flush` keyword-only in `Object.print`, `List.print`, `Tuple.print`, the exception-instance `_print` (`poop/types/exceptions.py`) and `PoopMeta.print`; change `tests/test_types/test_object.py:582` to the new sentence and add the `object-type` delta's other positional scenarios (with `end`, on a list, on a class) there. Update *Object.print* in `INFECTIONS.md` with the keyword-only signature and why the extra positionals are not printed as CPython's `print(*objects)` would. Verify with `uv run pytest tests/test_types/test_object.py tests/test_types/test_list.py tests/test_types/test_tuple.py tests/test_types/test_meta.py tests/test_types/test_exceptions.py -q`, and check that every example still runs.

## 3. The sweep enforces the name

- [x] 3.1 In `tests/test_no_python_wording.py`, read the callee out of every sentence `_ARITY` matches and fail unless it is the class receiver's name, the instance receiver's own class name, `object` for a message `Object` defines, or the wrapper a program's subclass extends. State the oracle in the comment above `_ARITY`, and send six arguments as well as the current one and two. Record the rule and the sweep in the `_MethodBlock` arity paragraph of `INFECTIONS.md` (*A method is a block…* in *Principles*). Verify with `uv run pytest tests/test_no_python_wording.py -q`, and with the 1.1 rename temporarily reverted, check that the sweep fails and names `object.map`, `bytes.lower` and `hash`.

## 4. Integration

- [x] 4.1 Run `uv run ruff check && uv run ruff format --check && uv run ty check poop/ tests/ && uv run pytest`, reading the summary line, run every example (`examples/basics/greet.py` with `echo Ana |`, the rest with `</dev/null`), and run `openspec validate arity-names-the-receiver --strict`. Verify that every step exits 0 and coverage stays at or above 95%.

## Workflow follow-up

- Archive the change with `/opsx:archive` once every task is done.
