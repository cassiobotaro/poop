# Proposals

Open design backlog. Closing convention: see [`CONTRIBUTING.md`](CONTRIBUTING.md#closing-a-proposal).

Item 8 was found while implementing the Python 3.15 batch (items 1–7, all
closed): a wrapper's operator refusal exposed a pre-existing leak on the class
side.

When an item is implemented, delete its entry from this file — no `DONE`
marker and no summary left behind. The decision and its reasoning belong in
[`INFECTIONS.md`](INFECTIONS.md), and the diff lives in the git history.

Numbering continues from the highest open item; the next one is 9. Once every
item has been implemented and deleted, numbering starts over at 1.

### 8. A class-side operator names `_AliasMeta`

Found while wrapping `sentinel`: `int | sentinel("M")` answers `TypeError:
_AliasMeta does not understand #| with a sentinel`. A bare builtin name is the
alias class (`poop/types/_alias.py`), and `type.__or__` — CPython's union
builder, so `int | str` quietly answers a `types.UnionType` POOP has no use
for — declines a non-type operand, after which `poop_message` rewords
CPython's `unsupported operand type(s) for |: '_AliasMeta' and 'sentinel'`
with the metaclass's name in the receiver slot. `receiver_label` already
exists so `does not understand` says `int` for a class receiver; the operator
path does not go through it.

**Fix.** Decide what a class-side `|` means in POOP — probably nothing, since
unions belong to annotations the language does not write — and refuse it
under the class's own name (`int does not understand #| with a sentinel`),
which also closes the silent `int | str` success. The wording sweep's operator
half pairs instances only; a class receiver in `_OPERANDS` would have found
this.
