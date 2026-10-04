# Proposals

Open design backlog. Closing convention: see [`CONTRIBUTING.md`](CONTRIBUTING.md#closing-a-proposal).

Item 1 comes from checking `INFECTIONS.md` against two leaks found by hand.

When an item is implemented, delete its entry from this file — no `DONE`
marker and no summary left behind. The decision and its reasoning belong in
[`INFECTIONS.md`](INFECTIONS.md), and the diff lives in the git history.

Numbering continues from the highest open item; the next one is 2. Once every
item has been implemented and deleted, numbering starts over at 1.

### 1. The wording sweep is blind to three CPython sentences, and 64 sites leak them

`INFECTIONS.md` says `tests/test_no_python_wording.py` sends every public
message on every wrapper with wrong-typed arguments and runs the forbidden
patterns over what comes back. It does — but the patterns cover a call, a
dunder, an operator and a handful of argument reports, and three of CPython's
most common sentences carry none of those. `"a,b".split(5)` (`must be str or
None, not int`) and `int.from_bytes(5)` (`cannot convert 'int' object to
bytes`) were found by hand for that reason, and fixed one site at a time.

Trialled: adding `cannot be interpreted as|cannot convert '|must be str\b|object
is not` to the `"a CPython argument report"` pattern makes
`test_no_message_leaks_pythons_wording_when_sent_wrong` report 64
receiver/message sites, in three families.

- **`'str' object cannot be interpreted as an integer` — 29 sites.** An
  integer argument handed something else: `round` on `Int`, `Float` and
  `Boolean`; `to_bytes` on `Int` and `Boolean`; `center`, `ljust`, `rjust`,
  `zfill` and `expandtabs` on `Str`, `Bytes` and `ByteArray`; `hex` on both
  byte wrappers; `insert` and `pop` on `List` and `ByteArray`; `append` and
  `remove` on `ByteArray`; `Slice.indices`. No message, no argument, and
  "interpreted as" names a conversion the program never asked for.
- **`'int' object is not iterable` — 33 sites.** A collection argument handed
  a scalar: `zip` on nine collections; the set algebra on `Set` and
  `FrozenSet` (`union`, `intersection`, `difference`, `symmetric_difference`,
  `isdisjoint`, `issubset`, `issuperset`, and `Set`'s three `*_update`
  messages plus `update`); `join` on `Str`, `Bytes` and `ByteArray`;
  `List.extend`; `Dict.update` and `Dict.fromkeys`. "Iterable" is the protocol
  `no_iter` bans.
- **`startswith first arg must be str or a tuple of str, not int` — 2 sites.**
  `Str.startswith` and `Str.endswith`; the message as a bare word and "arg",
  the shape `_opt_text` already replaced for the strip family.

**Fix.** Widen the pattern first, so the sweep fails, then make it pass one
family at a time — one guard per argument *kind* in
`poop/types/_argument.py`, as `a_bound` and `text_like` are, not one per
receiver. `a_bound` and `max_split` already word an integer argument
(`#split's maxsplit must be an int, got a str`); the first family is mostly
call sites adopting that shape with the role named. The second needs a new
guard for "a collection". Worth deciding before starting: what the refusal
calls the thing it wanted — POOP has no word "iterable".
