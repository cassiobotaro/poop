# Proposals

Open design backlog. Closing convention: see [`CONTRIBUTING.md`](CONTRIBUTING.md#closing-a-proposal).

Items 12–20 come from a pass over `poop/` for shape rather than types: what repeats, what a stdlib module already does, what a
library function changes about the process it runs in. Each was measured or
checked before being written down — the import-cycle idiom in 12 on Python
3.15, the overhead in 14 with `timeit`, the redundancy in 15 by walking every
class's MRO. Order: 20 is the lock.

When an item is implemented, delete its entry from this file — no `DONE`
marker and no summary left behind. The decision and its reasoning belong in
[`INFECTIONS.md`](INFECTIONS.md), and the diff lives in the git history.

Numbering continues from the highest open item; the next one is 21. Once every
item has been implemented and deleted, numbering starts over at 1.
