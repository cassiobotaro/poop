# Tasks

## 1. A caught error and raise_

- [x] 1.1 Make `_cpython_name` (`poop/types/block.py`) name an `Error` receiver by its exception's class, importing `Error` lazily with a `# circular:` comment, and switch the sweep oracle in `tests/test_no_python_wording.py` from `type(receiver).__name__` to `receiver.class_().__name__` for an instance. Add the `message-arity` delta's two caught-error scenarios to `tests/test_types/test_message_arity.py`. Verify with `uv run pytest tests/test_types/test_message_arity.py tests/test_no_python_wording.py -q`. Then, with the `Error` branch temporarily removed, check that the sweep fails and names the error sample.
- [x] 1.2 Remove the hand-written `*extra` refusal from `_raise` (`poop/types/exceptions.py`) and `Error.raise_` (`poop/types/error.py`), and drop any import that only served it. Change `tests/test_types/test_exceptions.py:482` and `tests/test_types/test_error.py:387` to `ValueError.raise_() takes 1 positional argument but 2 were given`, and remove `'ValueError("x").raise_(1)'` from the sweep's `_FAILING` list, since that sentence is now CPython's shape on purpose. Update the *PoopExcMeta* and *Error* paragraphs in `INFECTIONS.md` that quote the old sentences. Verify with `uv run pytest tests/test_types/test_exceptions.py tests/test_types/test_error.py tests/test_no_python_wording.py -q`.

## 2. The branch family teaches

- [x] 2.1 Give every block parameter of the branch family a `… | Missing = MISSING` default: `if_true`, `if_false`, `if_true_if_false`, `if_false_if_true`, `and_` and `or_` on `Boolean` and both singleton classes (`poop/types/boolean.py`); `if_none`, `if_not_none` and both pairs on `Object` and `NoneClass`; and `while_true`/`while_false`'s `body` on `Block`. Add the `message-arity` delta's missing-block scenarios to `tests/test_types/test_message_arity.py`, with one case per receiver class (a boolean, `None`, an object, a block), and one `tests/test_types/test_block.py` case that a block made by `get_attr` from a branch message keeps `block-arity`'s sentence. Verify with `uv run pytest tests/test_types/test_message_arity.py tests/test_types/test_boolean.py tests/test_types/test_none.py tests/test_types/test_object.py tests/test_types/test_block.py -q`.
- [x] 2.2 Pass `spelt="lambda: …, lambda: …"` to `a_block` in both `bool` pairs, add the "boolean pair handed a non-block" scenario to `tests/test_types/test_message_arity.py`, and update any test that pins the one-block hint. Verify with `uv run pytest tests/test_types/test_message_arity.py tests/test_types/test_boolean.py -q`.

## 3. The rule on record

- [x] 3.1 Extend the *The arity sentence is CPython's, and so is the class inside it* bullet in `INFECTIONS.md` with the rule (POOP rewords an arity refusal only to add a hint), the families that keep their own wording (converters, `Try`/`With`, the missing-block family, `raise_from`) and why `raise_` lost its own. Verify that every snippet quoted runs with `uv run poop` and answers the quoted sentence.

## 4. Integration

- [x] 4.1 Run `uv run ruff check && uv run ruff format --check && uv run ty check poop/ tests/ && uv run pytest`, reading the summary line, run every example (`examples/basics/greet.py` with `echo Ana |`, the rest with `</dev/null`), and run `openspec validate arity-refusals-teach --strict`. Verify that every step exits 0 and coverage stays at or above 95%.

## Workflow follow-up

- Archive the change with `/opsx:archive` once every task is done.
