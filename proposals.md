# Proposals

Open design backlog. Closing convention: see [`CONTRIBUTING.md`](CONTRIBUTING.md#closing-a-proposal).

Items 1–16 come from a second Pythonic-code review of the package and the test
suite, opened once the first twelve closed. The first three change behaviour a
program can observe; the rest remove duplication, hand-rolled dispatch or
spellings of things the stdlib or the codebase already has. Each was verified
against the code at the commit that opened it: the leaks were reproduced with
`poop`, the counts are from `grep`.

When an item is implemented, delete its entry from this file — no `DONE`
marker and no summary left behind. The decision and its reasoning belong in
[`INFECTIONS.md`](INFECTIONS.md), and the diff lives in the git history.

Numbering continues from the highest open item; the next one is 17. Once every
item has been implemented and deleted, numbering starts over at 1.

### 16. The suite asserts AST shape by hand and copies the call-name contract thirty-eight times

- `tests/test_transformers/` has forty-one `isinstance(call.func, ast.Name)` …
  `call.func.id == "_poop_int"` chains, each four to six asserts that check
  part of the tree, and only four files use `ast.unparse`. `ast.unparse` of the
  transformed module says it exactly in one line: `x = _poop_int(42)`,
  `_poop_int_from('42')`. A `rewritten(transformer, source) -> str` next to
  the `transform` helper in `tests/_support.py` makes each test one assert,
  and the three-case tests `parametrize` cleanly; the "is not rewritten" tests
  become `rewritten(...) == source`. The `isinstance` narrowing was only there
  for `ty`, which `unparse` removes the need for. The four `BINDINGS[...] is`
  identity tests stay.
- Thirty-eight validators are `CallNameValidator` subclasses with two class
  attributes, and their seventy test modules repeat the same contract: sixty
  `test_valid_code_passes` over `x = 1 + 2`, sixty-two `*_carries_line_number`,
  the `method named X is not blocked` and `bare name is reserved` cases.
  `test_no_hash.py`, `test_no_len.py` and `test_no_abs.py` are byte-identical
  modulo the name. One `tests/test_validators/test_call_name.py` parametrised
  over `[(v, name) for v in DEFAULT_VALIDATORS if isinstance(v,
  CallNameValidator) for name in v.forbidden]` states the contract once and
  cannot forget a new validator; a suite-wide `test_plain_code_passes` over
  `DEFAULT_VALIDATORS` replaces the sixty copies. Each per-validator file keeps
  only what is specific — the substitute wording. CONTRIBUTING's "tests live
  next to their target" gets a line saying the mechanical contract lives in
  the shared module.
- Hygiene in the same sweep: unused `capsys` / `monkeypatch` parameters in
  `tests/test_repl.py` (ruff `ARG` is off); `tmp_path: object` then
  `Path(str(tmp_path))` twice there; both `import pathlib` and `from pathlib
  import Path` in one file; `_repl()` returning `(repl, repl._ns)` thirty-three
  times, mostly unpacked as `repl, _` — a `repl` fixture; one test in
  `tests/test_cli.py` writing `syntax.py` by hand beside the `source_file`
  fixture that does it, and two identical `subprocess.run([sys.executable,
  "main.py", ...])` blocks.

**Fix.** The `rewritten` helper and a file-by-file conversion; the parametrised
call-name module; the hygiene bullets as one commit. No behaviour is touched.

---

Considered and not proposed, so the next review does not re-open them:
subclassing `code.InteractiveConsole` wholesale (the REPL writes banner and
prompts to stderr and names each input `<repl-N>`, which it does not offer);
moving the per-class `max`/`min` and set messages into their mixins (the
mixins are cloaked `object`, and the rule that a wrong-arity error names the
receiver is stated in `_set_algebra.py` and `_sequence.py`); deriving the
three `BINDINGS` entries of the sixteen constructor transformers from
`rewriter.builtin` (the keys are not uniform — `_poop_range` is a converter,
`Boolean` binds as `_poop_boolean`, `complex` adds a literal binding — and
twenty test files name them, so it is a rename with scope to confirm first);
`isinstance(raw, SupportsIndex)` for `hasattr(raw, "__index__")` (slower, and
the current test is CPython's exact rule); `zip(strict=True)` under `Zip` (a
`ValueError` from a user block would be indistinguishable from the mismatch).
