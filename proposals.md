# Proposals

Open design backlog. Closing convention: see [`CONTRIBUTING.md`](CONTRIBUTING.md#closing-a-proposal).

Items 1–14 come from one review of `poop/` as Python code rather than as a
language: what a Python engineer would change about how the interpreter is
written. Three of them (1–3) turned out to be behaviour and lead for that
reason. Item 4 is the one measured in wall-clock time. The rest are ordered
roughly by how much code each one touches. Every "trialled" below means the
change was made on a copy of the tree and the whole suite (5048 tests) was run
against it.

When an item is implemented, delete its entry from this file — no `DONE`
marker and no summary left behind. The decision and its reasoning belong in
[`INFECTIONS.md`](INFECTIONS.md), and the diff lives in the git history.

Numbering continues from the highest open item; the next one is 15. Once every
item has been implemented and deleted, numbering starts over at 1.

### 14. 110 comments cite a proposal by a number that names nothing

`proposal N` appears 19 times in `poop/`, 88 times in `tests/` and 3 times in
`INFECTIONS.md`: "the disagreement proposal 16 closed", "Proposal 3's record
quotes the sentence", "the same argument proposal 2 settled for `With`".

Closed entries are deleted from this file, so none of the 110 can be looked
up here. And numbering starts over at 1 whenever the backlog empties, so a
number no longer names one thing: `proposal 2` is cited in `meta.py`
(refusing writes to builtin classes) and in `block.py` (checking `With`'s
argument early), and the item closed last under that number is about
`dict_values`' hash. `git log --grep "close proposal 2"` will keep returning
more commits each time the numbering restarts.

Almost every citation sits beside the reasoning it refers to; the number adds
a pointer, and the pointer is dead.

**Fix.** Drop the number where the sentence stands without it, and cite the
commit hash where the reference matters. `CONTRIBUTING.md` gains one line:
code and tests cite commits, not proposal numbers.
