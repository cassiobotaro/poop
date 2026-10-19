# Tasks

## 1. Placeholders by role

- [x] 1.1 Name the receiver's own value `value`: change `_PAIR` and `_PAIR_SWAPPED` in `poop/types/object.py` to `lambda: …, lambda value: …` and `lambda value: …, lambda: …`, and pass `param="value"` to `a_block` in `if_not_none` on `Object` and `NoneClass` (`poop/types/none.py`). Update the pinned hints in `tests/test_types/test_object.py`, `tests/test_types/test_none.py` and `tests/test_types/test_message_arity.py`, add the `object-type` delta's three `if_not_none`/swapped-pair scenarios to `tests/test_types/test_object.py`, and update any hint `INFECTIONS.md` quotes for the null tests. Verify with `uv run pytest tests/test_types/test_object.py tests/test_types/test_none.py tests/test_types/test_message_arity.py -q` and with `grep -rn "lambda x: …" poop/types/object.py poop/types/none.py` coming back empty.
- [x] 1.2 Name a collection element `item`: change `find`'s positional-default refusal in `poop/types/_iterable_mixin.py` and the `detectIfNone`, `timesRepeat` and `toDo` hints in `poop/types/_selectors.py`. Update `tests/test_types/test_list.py` and `tests/test_types/test_does_not_understand.py`, adding the `does-not-understand` delta's `toDo` and `detectIfNone` scenarios there, and update the hints quoted in `INFECTIONS.md` (the Smalltalk-table paragraph and the `find` default paragraph). Verify with `uv run pytest tests/test_types/test_list.py tests/test_types/test_does_not_understand.py -q` and with `grep -rnE "lambda (x|i): …" poop` coming back empty.

## 2. Integration

- [x] 2.1 Run `uv run ruff check && uv run ruff format --check && uv run ty check poop/ tests/ && uv run pytest`, reading the summary line and gating on pytest's own exit code, run every example (`examples/basics/greet.py` with `echo Ana |`, the rest with `</dev/null`), and run `openspec validate hint-placeholders-by-role --strict`. Verify that every step exits 0 and coverage stays at or above 95%.

## Workflow follow-up

- Archive the change with `/opsx:archive` once every task is done.
