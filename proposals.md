# Proposals

## Expose `math` functions as POOP messages

Python's `math` module is currently unreachable from POOP code because
imports are forbidden. There is no idiomatic way to compute `sqrt`,
`sin`, `log`, etc. in POOP source today.

Smalltalk handles this with **messages on numbers** — `2 sqrt`, `1.0 sin`,
`100 ln`, `30 degreesToRadians sin`. There is no `Math` global; the
behavior lives on `Number` (and concretely on `Float`). POOP should
adopt the same model where it fits, with a pragmatic fallback for
multi-argument helpers and constants.

**Proposal — hybrid model:**

1. **Unary functions become methods on `Int` / `Float`.** The receiver
   is obvious and the message reads naturally:
   - `(2.0).sqrt()`, `(2.0).sin()`, `(2.0).cos()`, `(2.0).tan()`
   - `(2.0).asin()`, `(2.0).acos()`, `(2.0).atan()`
   - `(2.0).sinh()`, `(2.0).cosh()`, `(2.0).tanh()`
   - `(2.0).asinh()`, `(2.0).acosh()`, `(2.0).atanh()`
   - `(2.0).exp()`, `(2.0).log()`, `(2.0).log2()`, `(2.0).log10()`,
     `(2.0).log1p()`
   - `(2.0).floor()`, `(2.0).ceil()`, `(2.0).trunc()`
   - `(0.5).degrees()`, `(0.5).radians()` (Python's `math.degrees` /
     `math.radians`)
   - `(0.5).erf()`, `(0.5).erfc()`, `(0.5).gamma()`, `(0.5).lgamma()`
   - `(n).factorial()` (Int only)
   - `(a).is_finite()`, `(a).is_infinite()`, `(a).is_nan()` (already
     fits the `is_xxx() -> Boolean` pattern)
2. **Binary / multi-argument helpers become a `Math` namespace-only
   object** (same family as `Try` / `With` / `Path`):
   - `Math.atan2(y, x)`, `Math.hypot(x, y, ...)`, `Math.copysign(x, y)`,
     `Math.gcd(a, b)`, `Math.lcm(a, b)`, `Math.dist(p, q)`,
     `Math.fmod(a, b)`, `Math.remainder(a, b)`, `Math.comb(n, k)`,
     `Math.perm(n, k)`, `Math.fsum(iterable)`, `Math.prod(iterable)`,
     `Math.isclose(a, b, ...)`
3. **Constants live on `Math`:** `Math.pi`, `Math.e`, `Math.tau`,
   `Math.inf`, `Math.nan`. Methods returning `Float`.

`MathTransformer` is **namespace-only** (no AST rewrite); it injects
`Math` into `DEFAULT_NAMESPACE` like `Try` / `With` / `Path`.

**Out of scope (for v1):**

- The bit/integer-specific helpers (`bit_length`, `bit_count`) already
  live on `Int` and stay there.
- `math.frexp` / `math.modf` / `math.ldexp` — niche; defer until
  someone asks.
- Complex math (`cmath`) — orthogonal, would need its own proposal.

**Open question:** should `Float`'s `is_finite()` / `is_infinite()` /
`is_nan()` be class-level on `Math` too (mirroring `math.isfinite(x)`)?
Argument for both: receiver-method form reads naturally; class-level
mirror keeps API discoverable for Python users searching for
`isfinite`. Argument against: duplication for no semantic gain.

## Audit the rest of the Python stdlib for POOP equivalents

Following the `math` proposal above, the same question applies to
every other commonly-used Python module: imports are forbidden in
POOP, so anything in the stdlib is currently unreachable from POOP
code. Each module needs a decision about whether — and how — to
surface it inside POOP, without breaking the message-passing model.

Three Smalltalk patterns are already in use and should guide the
decision case-by-case:

- **Message on the value** — when the operation belongs to a single
  receiver (`'abc'.is_digit()`, `(2.0).sqrt()`, `coll.sort()`).
- **Class-with-class-methods (`Math`-style namespace global)** — when
  the operation parses, creates, or combines values (`Random new`,
  `Date today`, `NeoJSONReader fromString:`, `Math.atan2`). In POOP
  this maps to a namespace-only binding like `Try` / `With` / `Path`.
- **Specialized global object** — when there is no single value to
  receive the message (`Smalltalk exit`, `Transcript`, `SystemVersion
  current`). POOP would split this into responsibility-scoped objects
  like `System`, `Platform`, `Stdout`, `Stderr` rather than a single
  monolithic `Sys`.

The audit should classify each commonly-used module against these
three patterns, producing a per-module proposal (or a "stays out"
note). First-pass candidates:

| Module | Likely pattern | Sketch |
|---|---|---|
| `sys` | Split globals | `System.exit()`, `System.gc()`, `Platform.name`, `Args`, `Stdout`/`Stderr.print(...)` |
| `os` / `os.path` | Mix | Most already covered by `Path`; env vars and process ops via a `System` global |
| `random` | Class fábrica | `Random.new()`, `Int.at_random()`, `coll.at_random()` (Smalltalk's `atRandom`) |
| `datetime` / `time` | Class fábricas | `DateTime.now()`, `Date.today()`, `Duration.days(3)`, arithmetic via messages |
| `re` | Message on `Str` | `'abc'.matches('a.*')`, `'abc'.regex_matches('\\d+')` — regex object as input, not as namespace |
| `json` | Class fábrica | `Json.parse(s)`, `Json.dumps(obj)` |
| `collections` | Already covered | `OrderedDict`, `Counter`, `deque` mostly redundant — POOP collections already carry the methods |
| `itertools` / `functools` | Already covered | Replaced by mixin methods (`do`, `map`, `filter`, `reduce`, …) |
| `io` | Message on `Path` / `Str` | Streams via `Path.read_text()` etc.; `StringIO`/`BytesIO` deferred |
| `string` | Already covered | Constants like `string.ascii_letters` could live on `Str` (e.g. `Str.ascii_letters`) |

This is **scoping work**, not implementation work — the audit should
produce a per-module decision and either a follow-up proposal or a
"stays out" entry. Implementation happens proposal-by-proposal.
