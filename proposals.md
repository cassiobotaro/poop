# Proposals

## Expose `uuid` as POOP messages

Python's `uuid` module is unreachable from POOP today (imports are
forbidden). UUIDs are the default primary-key / correlation-ID
choice across modern systems, and there is no native way to mint
or parse one from POOP source.

Smalltalk models this with a class factory on `UUID`: `UUID new`
mints a v4, `UUID fromString:` parses one, and the instance answers
`asString`, `version`, `asByteArray`.

**Proposal:**

1. **New POOP type `Uuid`** in `poop/types/uuid.py`, wrapping
   `uuid.UUID` internally. Instances answer:
   - `.hex -> Str`, `.urn -> Str`, `.int -> Int`,
     `.bytes -> Bytes`, `.bytes_le -> Bytes`
   - `.fields -> Tuple` (6-tuple of `Int`)
   - `.time_low`, `.time_mid`, `.time_hi_version`,
     `.clock_seq_hi_variant`, `.clock_seq_low`, `.node`, `.time`,
     `.clock_seq` — all `Int`
   - `.version -> Int`, `.variant -> Str`, `.is_safe -> Str`
     (`"safe"` / `"unsafe"` / `"unknown"` — **sanctioned divergence**:
     Python returns a `SafeUUID` enum; POOP flattens to a `Str` token
     to avoid introducing a one-off enum type)
2. **Namespace `Uuid`** injected into `DEFAULT_NAMESPACE`
   (`Math`-style, no AST rewrite). Class-side messages:
   - `Uuid.uuid1(node=None, clock_seq=None)`,
     `Uuid.uuid3(namespace, name)`, `Uuid.uuid4()`,
     `Uuid.uuid5(namespace, name)`,
     `Uuid.uuid6(node=None, clock_seq=None)`, `Uuid.uuid7()`,
     `Uuid.uuid8(a=None, b=None, c=None)` — every variant Python 3.14
     ships
   - `Uuid.from_string(s)`, `Uuid.from_bytes(b)`,
     `Uuid.from_bytes_le(b)`, `Uuid.from_int(i)`,
     `Uuid.from_fields(...)` — factory methods substituting for
     Python's overloaded `uuid.UUID(hex=..., bytes=..., int=...)`
     constructor, since POOP namespaces are not callable
   - `Uuid.getnode() -> Int` (mirrors `uuid.getnode()`)
3. **Constants on `Uuid`** — every public `uuid.*` constant:
   - The four standard namespaces as POOP `Uuid` values:
     `Uuid.NAMESPACE_DNS`, `Uuid.NAMESPACE_URL`,
     `Uuid.NAMESPACE_OID`, `Uuid.NAMESPACE_X500`
   - The two sentinel UUIDs: `Uuid.NIL` (all-zeros), `Uuid.MAX`
     (all-ones)
   - The four variant `Str` constants: `Uuid.RESERVED_NCS`,
     `Uuid.RFC_4122`, `Uuid.RESERVED_MICROSOFT`,
     `Uuid.RESERVED_FUTURE`

`UuidTransformer` is **namespace-only** (no AST rewrite); it
injects `Uuid` into `DEFAULT_NAMESPACE` like `Math` / `Try` /
`With` / `Path`.

**Type discipline:** every signature exposed by this proposal —
methods on `Uuid` instances, methods and constants on the `Uuid`
namespace — takes and returns POOP types (`Uuid`, `Str`, `Bytes`,
`Int`, `Tuple`). No `uuid.UUID`, raw `bytes`, or `int` leaks across
the boundary.

**Smalltalk reference.**

| Python | Smalltalk (Pharo) | Notes |
|---|---|---|
| `uuid.uuid4()` | `UUID new` | POOP mirrors Python — no `.new()` alias |
| `uuid.UUID(s)` | `UUID fromString: s` | keyword msg in Smalltalk |
| `u.hex` | `u asString36 copyWithout: $-` | Pharo has no direct `.hex` |
| `u.bytes` | `u asByteArray` | direct |
| `u.version` | `u version` | direct |
| `uuid.uuid6` / `7` / `8` | (no native) | new in Python 3.14 |

**Out of scope (for v1):**

- `uuid.SafeUUID` exposed as a dedicated POOP enum type — flatten
  to a `Str` token instead.

## Expose `secrets` as POOP messages

Python's `secrets` module is unreachable from POOP today. Without
it, POOP source cannot mint cryptographically-secure tokens, draw
secure random integers, or compare digests in constant time —
operations every auth-aware program needs.

Smalltalk has no equivalent in the base image; Pharo's Cryptography
package adds `SecureRandom`, but the choice is non-canonical. POOP
follows Python here.

**Proposal:**

1. **Namespace `Secrets`** injected into `DEFAULT_NAMESPACE`
   (`Math`-style, no AST rewrite). No new POOP type.
2. **Token minting** (`nbytes=None` resolves to `DEFAULT_ENTROPY`,
   mirroring Python):
   - `Secrets.token_bytes(nbytes=None) -> Bytes`
   - `Secrets.token_hex(nbytes=None) -> Str`
   - `Secrets.token_urlsafe(nbytes=None) -> Str`
3. **Secure draws** (parameter names follow Python exactly):
   - `Secrets.choice(seq) -> element` (works on any POOP iterable;
     element is a POOP type)
   - `Secrets.randbelow(exclusive_upper_bound) -> Int`
   - `Secrets.randbits(k) -> Int`
4. **Constant-time comparison:**
   - `Secrets.compare_digest(a, b, /) -> Boolean` (positional-only,
     accepts `Str` or `Bytes`; rejects mixed types like Python does)
5. **Constant:**
   - `Secrets.DEFAULT_ENTROPY -> Int` (`32` in CPython)

`SecretsTransformer` is **namespace-only**.

**Type discipline:** every signature exposed by this proposal takes
and returns POOP types (`Bytes`, `Str`, `Int`, `Boolean`, plus the
element type for `choice`). No Python primitives leak across the
boundary.

**Smalltalk reference.** No direct mapping in base Pharo. The
nearest analog is `Random new` (NOT cryptographically secure) —
POOP deliberately separates the two: `Random` (proposal pending)
will be non-secure; `Secrets` is secure-by-default.

**Out of scope (for v1):**

- `secrets.SystemRandom` class wrapper — duplicates `choice` /
  `randbelow` / `randbits` already on `Secrets`.

## Expose `random` as POOP messages

Python's `random` module is unreachable from POOP today (imports are
forbidden). Without it, POOP source cannot draw random numbers, pick
a random element from a collection, shuffle a sequence, or seed a
deterministic generator — primitives every simulation, game, and
test fixture needs.

Smalltalk handles randomness on two levels: a `Random` class
(`Random new` returns a non-secure generator) and messages on
values (`aCollection atRandom`, `anInteger atRandom`). POOP
**deliberately does not adopt the Smalltalk message-on-value
shortcuts** — the interface mirrors Python's `random` module
exactly, so the only entry points are the `Random` namespace and
explicit `Random` instances.

**Proposal — exact mirror of Python's `random.Random` instance +
module-level singleton pattern.**

1. **New POOP type `Random`** in `poop/types/random.py`, wrapping
   `random.Random`. Instances answer the full Python method set:
   - **Bookkeeping:** `.seed(a=None, version=2)`,
     `.getstate() -> Tuple`, `.setstate(state)`
   - **Core draws:** `.random() -> Float` (in `[0.0, 1.0)`),
     `.uniform(a, b) -> Float`, `.randint(a, b) -> Int` (inclusive
     both ends), `.randrange(start, stop, step) -> Int`,
     `.getrandbits(k) -> Int`, `.randbytes(n) -> Bytes`
   - **Collection draws** (parameter names follow Python exactly):
     `.choice(seq) -> element`,
     `.choices(population, weights=None, *, cum_weights=None, k=1) -> List`,
     `.sample(population, k, *, counts=None) -> List`,
     `.shuffle(x)` — in-place, mutates and returns `None`
     (mirrors Python)
   - **Distributions:** `.gauss`, `.normalvariate`,
     `.lognormvariate`, `.expovariate`, `.gammavariate`,
     `.betavariate`, `.paretovariate`, `.weibullvariate`,
     `.vonmisesvariate`, `.triangular`, `.binomialvariate`
     (Python 3.12+) — all returning `Float` or `Int` as in Python.
2. **Namespace `Random`** (class side of the `Random` POOP type)
   injected into `DEFAULT_NAMESPACE` (`Math`-style, no AST rewrite).
   Class-side messages mirror every instance method above by
   delegating to a hidden module-level singleton, exactly like
   Python's `random.random()` vs `Random().random()`:
   - `Random.new(seed)` — substitutes for Python's
     `random.Random(seed)` constructor call (POOP namespaces are
     not callable, so this is the one forced naming divergence
     from Python)
   - `Random.random()`, `Random.uniform(a, b)`, `Random.randint(a, b)`,
     `Random.choice(seq)`, `Random.shuffle(x)`,
     `Random.sample(population, k, *, counts=None)`,
     `Random.choices(population, weights=None, *, cum_weights=None, k=1)`,
     … — every Python module-level function with the same name and
     parameter order.

`RandomTransformer` is **namespace-only**; it injects `Random` into
`DEFAULT_NAMESPACE`. There are **no** new methods on iterables or
`Int` — anything that would have looked like `coll.at_random()` or
`(n).at_random()` is reached through `Random.choice(coll)` or
`Random.randint(1, n)`, which is how a Python program would write it.

**Type discipline:** every signature exposed by this proposal —
methods on `Random` instances and on the `Random` namespace — takes
and returns POOP types (`Random`, `Float`, `Int`, `Bytes`, `List`,
`Tuple`, plus the element type of the receiving collection). No
`random.Random` instance, raw `float`, or `int` leaks across the
boundary.

**`random` vs `secrets`.** This proposal is for the non-secure,
deterministic-when-seeded generator. Anything touching auth, token
minting, or constant-time comparison goes through `secrets`
(separate proposal above). POOP keeps the two namespaces strictly
distinct, exactly as Python does.

**Smalltalk reference.** Listed for context only — POOP's interface
mirrors Python, not Smalltalk, even where Smalltalk reads more
naturally.

| Python | Smalltalk (Pharo) | Notes |
|---|---|---|
| `random.random()` | `Random new next` | Smalltalk's `next` returns `[0.0, 1.0)`; POOP keeps `.random()` |
| `random.randint(a, b)` | `a to: b atRandom` | POOP keeps `.randint(a, b)` |
| `random.choice(coll)` | `coll atRandom` | POOP keeps `Random.choice(coll)` — no `coll.at_random()` mixin |
| `random.shuffle(seq)` | `seq shuffle` | POOP mutates like Python; non-mutating shuffle = `Random.sample(coll, k=len(coll))` (Python idiom) |
| `random.sample(pop, k)` | (no native) | POOP keeps `.sample(pop, k)` |
| `random.seed(a)` | `Random new seed: a` | direct |
| `Random()` (new instance) | `Random new` | POOP exposes as `Random.new(seed)` — only forced divergence (namespace not callable) |
| `random.randrange(n)` | `n atRandom` (≠) | **semantics differ**: Smalltalk returns `1..n`, Python returns `0..n-1`. POOP follows Python exactly. |

**Out of scope (for v1):**

- `random.SystemRandom` — duplicates `secrets`; users wanting
  crypto-secure draws go through `Secrets.*` instead.
- `Random.VERSION` class attribute — implementation detail of the
  state-serialization format; defer until needed.
- The `main` entry point (`python -m random`) — niche CLI tool.
- Internal magic constants (`BPF`, `LOG4`, `NV_MAGICCONST`,
  `RECIP_BPF`, `SG_MAGICCONST`, `TWOPI`) — Python exposes them but
  they are implementation detail of the distributions.

## Expose `base64` as POOP messages

Python's `base64` module is unreachable from POOP today. Encoding
bytes to text and back is a foundational primitive (data URIs, JWT
headers, Basic auth, embedded blobs) and POOP source has no path
to it.

Smalltalk's Network-Url package in Pharo puts these messages on the
value: `'abc' asByteArray base64Encoded`. POOP adopts the
message-on-value direction but **keeps Python's exact function
names and return types** so the interface mirrors `base64.*`
literally.

**Proposal — methods on `Bytes` (encode/decode) and `Str` (decode
only), no new namespace.**

1. **Encode on `Bytes`** (each returns `Bytes`, matching Python —
   the encoded value is ASCII-bearing `Bytes`, not `Str`):
   - `.b16encode()`, `.b32encode()`, `.b32hexencode()` (Python 3.10+),
     `.b64encode()`, `.standard_b64encode()`, `.urlsafe_b64encode()`,
     `.a85encode()`, `.b85encode()`, `.z85encode()` (Python 3.13+)
2. **Decode on `Bytes`** (each returns `Bytes`):
   - `.b16decode()`, `.b32decode()`, `.b32hexdecode()`,
     `.b64decode()`, `.standard_b64decode()`,
     `.urlsafe_b64decode()`, `.a85decode()`, `.b85decode()`,
     `.z85decode()` (Python 3.13+)
3. **Decode on `Str`** (each returns `Bytes`) — every variant whose
   Python counterpart accepts a `str` input:
   - `.b16decode()`, `.b32decode()`, `.b32hexdecode()`,
     `.b64decode()`, `.standard_b64decode()`,
     `.urlsafe_b64decode()`, `.a85decode()`, `.b85decode()`,
     `.z85decode()` (Python 3.13+)

No new POOP type, no `Base64Transformer`, no AST rewrite — the
methods are registered on the existing `Bytes` and `Str` types.

**Type discipline:** every method takes and returns POOP types —
`Bytes` and `Str` only. No `bytes` / `str` leaks. Method names,
parameter shapes, and return types mirror `base64.<name>` exactly.
Note that callers wanting a `Str` representation of an encoded
value must explicitly `.decode('ascii')` the returned `Bytes`,
exactly as in Python.

**Smalltalk reference.**

| Python | Smalltalk (Pharo, Network-Url) | Notes |
|---|---|---|
| `base64.b64encode(b)` | `b base64Encoded` | POOP keeps Python name: `b.b64encode()` |
| `base64.b64decode(s)` | `s base64Decoded` | POOP keeps Python name |
| `base64.urlsafe_b64encode(b)` | `b base64UrlEncoded` | POOP keeps Python name |
| `base64.b16encode(b)` | `b hex` | Pharo conflates b16 and hex; POOP keeps Python's `.b16encode()` |
| `base64.a85encode` / `b85encode` | (no native) | rarely used |

**Out of scope (for v1):**

- Optional kwargs on individual encoders/decoders — v1 ships the
  defaults Python ships. Specifically deferred: `altchars` and
  `validate` on `b64encode`/`b64decode`, `casefold` and `map01` on
  `b32decode`/`b32hexdecode` and `b16decode`, `foldspaces` /
  `wrapcol` / `pad` / `adobe` on `a85encode`, `foldspaces` /
  `adobe` / `ignorechars` on `a85decode`, and `pad` on `b85encode`.
- Legacy file-oriented helpers (`encode`, `decode`, `encodebytes`,
  `decodebytes`) — POOP routes file I/O through `Path`.

## Expose `hashlib` as POOP messages

Python's `hashlib` module is unreachable from POOP today.
Computing SHA-256, deriving a key with PBKDF2, or checksumming a
file are common needs that POOP source currently cannot reach.

Smalltalk's Cryptography package in Pharo puts hashing on the
receiver: `'abc' asByteArray sha256` returns a `ByteArray`. POOP
follows the same shape but mirrors Python's two-step API
(`hashlib.sha256(data) -> Hash`, then `.hexdigest()`) so the
incremental `.update()` path is preserved.

**Proposal:**

1. **New POOP type `Hash`** in `poop/types/hash.py`, wrapping
   Python's hash object. Instances answer (mirroring Python
   exactly):
   - `.update(data) -> None` — mutates internal state, returns
     `None` like Python (no chaining)
   - `.digest(length=None) -> Bytes` — `length` is required for
     shake hashes and ignored by the rest (mirrors Python)
   - `.hexdigest(length=None) -> Str` — same shape as `.digest`
   - `.copy() -> Hash`
   - `.digest_size -> Int`, `.block_size -> Int`, `.name -> Str`
2. **Shortcut methods on `Bytes`** — every guaranteed algorithm
   becomes a unary message returning a `Hash`:
   - `.md5()`, `.sha1()`, `.sha224()`, `.sha256()`, `.sha384()`,
     `.sha512()`
   - `.blake2b()`, `.blake2s()`
   - `.sha3_224()`, `.sha3_256()`, `.sha3_384()`, `.sha3_512()`
   - `.shake_128()`, `.shake_256()` — constructor takes no `length`;
     pass `length` to `.digest(length)` / `.hexdigest(length)` on
     the returned `Hash` (mirroring Python exactly)
3. **Key-derivation messages on `Bytes`** (receiver = password,
   substituting for Python's first positional argument):
   - `.pbkdf2_hmac(hash_name, salt, iterations, dklen=None) -> Bytes`
   - `.scrypt(*, salt, n, r, p, maxmem=0, dklen=64) -> Bytes`
4. **Namespace `Hash`** (class side of the `Hash` POOP type):
   - `Hash.new(name, data) -> Hash` (generic constructor)
   - `Hash.algorithms_available -> FrozenSet` of `Str`
   - `Hash.algorithms_guaranteed -> FrozenSet` of `Str`
   - `Hash.file_digest(path, digest, /) -> Hash` (Python 3.11+;
     `path` is a POOP `Path` — sanctioned receiver-type divergence
     from Python's `fileobj`; the parameter named `digest` matches
     Python's name)

`HashTransformer` is **namespace-only**; it injects `Hash` into
`DEFAULT_NAMESPACE` alongside the new methods on `Bytes`.

**Type discipline:** every signature — methods on `Hash`, the
hash-shortcut and key-derivation methods on `Bytes`, and class-side
`Hash.*` — takes and returns POOP types (`Hash`, `Bytes`, `Str`,
`Int`, `FrozenSet`, `Path`). No `bytes`, `int`, or raw `hashlib` object
leaks across the boundary.

**Smalltalk reference.**

| Python | Smalltalk (Pharo Cryptography) | Notes |
|---|---|---|
| `hashlib.sha256(b).hexdigest()` | `b sha256 hex` | POOP keeps Python's `.hexdigest()` (no underscore) |
| `hashlib.sha256(b)`, then `.update(more)` | `SHA256 new accept: b; accept: more; finalHash` | Pharo uses `accept:` |
| `hashlib.md5(b)` | `b md5` | direct |
| `hashlib.pbkdf2_hmac(...)` | `PBKDF2 deriveKey: ... salt: ...` | similar shape, different naming |
| `hashlib.scrypt(...)` | (extension package) | not in base |
| `hashlib.file_digest(f, n)` | (no native) | Python 3.11+ |

**Out of scope (for v1):**

- `usedforsecurity=False` parameter — adds a flag without changing
  semantics on most platforms.
- Per-algorithm custom-init parameters for `blake2b` / `blake2s`
  (`key`, `salt`, `person`, `node_depth`, …) — niche.

**Open question:** should `Str` also offer the shortcut messages
(`'abc'.sha256()` encoding utf-8 first), or should it force
`.encode().sha256()` so the encoding step is explicit? Smalltalk
implicit-encodes via `asByteArray`; Python explicit-encodes via
`.encode()`. POOP could go either way.

## Expose `tomllib` as POOP messages

Python's `tomllib` (3.11+) is unreachable from POOP today. TOML
is the configuration format of choice across modern Python projects
(`pyproject.toml`, ruff / ty configs) and POOP programs should be
able to read it.

Smalltalk has no native TOML support; Pharo uses STON / JSON
instead. POOP follows Python here.

**Proposal:**

1. **Namespace `Toml`** injected into `DEFAULT_NAMESPACE`
   (`Math`-style, no AST rewrite). No new POOP types — TOML values
   map onto existing POOP types (`Dict` / `List` / `Str` / `Int` /
   `Float` / `Boolean` / `DateTime`).
2. **Parsing — keeping Python's exact names and keyword args:**
   - `Toml.loads(s, /, *, parse_float=Float) -> Dict` — direct
     mirror of `tomllib.loads`. `parse_float` defaults to `Float`
     (POOP's `Float`, mirroring Python's `float` default).
   - `Toml.load(path, /, *, parse_float=Float) -> Dict` — mirror of
     `tomllib.load`. Python takes a binary file object; POOP takes
     a POOP `Path` since POOP has no file-object abstraction. This
     is a forced receiver-type divergence; the message name and
     keyword args stay Python's.
3. **Errors:**
   - `Toml.TOMLDecodeError` — POOP error type wrapping
     `tomllib.TOMLDecodeError` (a `ValueError` subclass in Python).
     Raised by both `loads` and `load` on malformed input.

`TomlTransformer` is **namespace-only**.

**Type discipline:** every value in the returned `Dict` is a POOP
type. TOML's `date` / `time` / `datetime` map to POOP's `DateTime`
once that proposal lands (see the audit table — `datetime` is
currently `audit`); until then, expose them as ISO-8601 `Str` so
no Python `datetime.datetime` leaks. This is the one place the
proposal trades full type-coverage for ship-now pragmatism, and is
documented explicitly so it can be tightened later. When the
`DateTime` proposal lands, the `Toml.loads` / `Toml.load` return
type narrows from `Dict[Str, Str]` (for date-typed values) to
`Dict[Str, DateTime]` automatically.

**Smalltalk reference.** Pharo has no TOML parser in base. The
closest analogs are `STON fromString:` and `NeoJSONReader fromString:`
— class-side parsers returning a generic value. POOP keeps Python's
`loads` / `load` names rather than Smalltalk's `fromString:`.

**Out of scope (for v1):**

- Write support — Python's `tomllib` is read-only and there is no
  upstream writer.
- Routing TOML floats into `Decimal` via `parse_float` — the
  parameter ships in v1 (mirroring Python), but a `Decimal` target
  pairs with the `decimal` proposal.

## Audit the rest of the Python stdlib for POOP equivalents

The same question that drove the `math` namespace (shipped in
v0.6.0) applies to every other commonly-used Python module: imports
are forbidden in POOP, so anything in the stdlib is currently
unreachable from POOP code. Each module needs a decision about
whether — and how — to surface it inside POOP, without breaking the
message-passing model.

Three Smalltalk patterns are already in use and should guide the
decision case-by-case:

- **Message on the value** — when the operation belongs to a single
  receiver (`'abc'.is_digit()`, `path.read_text()`,
  `bytes.b64encode()`, `coll.sort()`).
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
note). Below is the full stdlib (`sys.stdlib_module_names`, 194
top-level modules, private `_*` modules excluded) grouped by the
categories from
[docs.python.org/3/library](https://docs.python.org/3/library/),
each annotated with one of:

- **covered** — already reachable from POOP today.
- **proposed** — has an active proposal in this file.
- **audit** — needs a decision (own proposal or "stays out").
- **out** — won't be surfaced; reason in the sketch column.

### Text Processing Services

| Module | Status | Sketch |
|---|---|---|
| `string` | audit | Constants (`ascii_letters`, …) on the `Str` class side |
| `re` | audit | Message on `Str`: `'abc'.matches('a.*')`, `'abc'.regex_matches('\\d+')` |
| `difflib` | audit | `Str.diff(other)` — likely own proposal |
| `textwrap` | audit | Messages on `Str`: `.wrap(width)`, `.indent(prefix)`, `.dedent()` |
| `unicodedata` | audit | Messages on `Str` (`.normalize()`) or `Unicode` namespace |
| `stringprep` | out | Internal IDNA helper |
| `readline` | out | REPL infrastructure — POOP doesn't expose a REPL |
| `rlcompleter` | out | REPL infrastructure |

### Binary Data Services

| Module | Status | Sketch |
|---|---|---|
| `struct` | audit | `Bytes.unpack(fmt)` / `Struct.pack(fmt, …)` — own proposal |
| `codecs` | audit | Mostly covered by `Str.encode` / `Bytes.decode`; rarer codecs need a call |

### Data Types

| Module | Status | Sketch |
|---|---|---|
| `datetime` | audit | Class factories — `DateTime.now()`, `Date.today()` |
| `zoneinfo` | audit | Pairs with `datetime` |
| `calendar` | audit | `Calendar` namespace |
| `collections` | covered | `OrderedDict` / `Counter` / `deque` redundant — POOP collections carry the methods |
| `heapq` | audit | Methods on `List` (`.heap_push`, `.heap_pop`) or `Heap` type |
| `bisect` | audit | `List.bisect(x)` / `.insert_sorted(x)` |
| `array` | audit | Typed dense array vs POOP `List` — defer unless needed |
| `weakref` | audit | Low priority |
| `types` | out | Introspection — forbidden in POOP |
| `copy` | audit | `obj.copy()` / `obj.deep_copy()` on `Object` |
| `pprint` | audit | Pairs with eventual print story |
| `reprlib` | out | POOP forbids `repr` |
| `enum` | audit | POOP classes already support class-side singletons |
| `graphlib` | audit | `Graph` type or namespace |

### Numeric and Mathematical Modules

| Module | Status | Sketch |
|---|---|---|
| `numbers` | out | ABC hierarchy — POOP has its own type tree |
| `math` | covered | `Math` namespace (shipped in v0.6.0) |
| `cmath` | audit | Needs `Complex` POOP type story — see "Future work" |
| `decimal` | audit | `Decimal` POOP type with full message API |
| `fractions` | audit | `Fraction` POOP type |
| `random` | proposed | See proposal above |
| `statistics` | audit | `coll.mean()` / `coll.median()` or `Statistics` namespace |

### Functional Programming Modules

| Module | Status | Sketch |
|---|---|---|
| `itertools` | covered | Mixin methods on iterables |
| `functools` | covered | `coll.reduce(…)`; partial application via `Block` |
| `operator` | out | Reflective access — clashes with no-introspection rule |

### File and Directory Access

| Module | Status | Sketch |
|---|---|---|
| `pathlib` | covered | `Path` |
| `os.path` / `posixpath` / `ntpath` / `genericpath` / `nturl2path` | covered | Reachable via `Path` |
| `fileinput` | out | Niche CLI helper |
| `stat` | out | Low-level constants — `Path` already exposes the queries |
| `filecmp` | audit | `Path.diff(other)`? |
| `tempfile` | audit | `Path.temp_file()` / `Path.temp_dir()` |
| `glob` | audit | `Path.glob(pattern)` (may already exist) |
| `fnmatch` | audit | `Str.matches_glob(pattern)` |
| `linecache` | out | Internal traceback helper |
| `shutil` | audit | High-level ops as messages on `Path` |

### Data Persistence

| Module | Status | Sketch |
|---|---|---|
| `pickle` | audit | `Path.dump(obj)` / `Path.load()` — security caveats |
| `copyreg` | out | Internal hook for `pickle` |
| `shelve` | out | Depends on `dbm` |
| `marshal` | out | CPython internal |
| `dbm` | out | Niche; prefer `sqlite3` |
| `sqlite3` | audit | `Database.open(path)` class factory — own proposal |

### Data Compression and Archiving

| Module | Status | Sketch |
|---|---|---|
| `zlib` | audit | `Bytes.compress()` / `Bytes.decompress()` |
| `gzip` | audit | `Path.gunzip()` / `Path.gzip()` |
| `bz2` | audit | Same shape as `gzip` |
| `lzma` | audit | Same shape as `gzip` |
| `zipfile` | audit | `Zip.open(path)` namespace |
| `tarfile` | audit | `Tar.open(path)` namespace |
| `compression` | audit | New 3.14 wrapper namespace — track upstream |

### File Formats

| Module | Status | Sketch |
|---|---|---|
| `csv` | audit | `Csv.parse(s)` / `Path.read_csv()` — own proposal |
| `configparser` | audit | `Ini.parse(s)` namespace |
| `tomllib` | proposed | See proposal above |
| `netrc` | out | Niche legacy format |
| `plistlib` | out | macOS-specific niche |

### Cryptographic Services

| Module | Status | Sketch |
|---|---|---|
| `hashlib` | proposed | See proposal above |
| `hmac` | audit | Pairs with `hashlib` |
| `secrets` | proposed | See proposal above |

### Generic Operating System Services

| Module | Status | Sketch |
|---|---|---|
| `os` | audit | Split: `System`, `Platform`, `Env`, `Process` |
| `io` | audit | Streams largely via `Path`; `StringIO`/`BytesIO` deferred |
| `time` | audit | Pairs with `datetime` |
| `logging` | audit | `Logger` namespace if a logging story emerges |
| `argparse` | out | POOP programs don't expose a CLI surface (yet) |
| `getpass` | audit | `Stdin.password()` if a stdin story emerges |
| `curses` | out | Terminal UI — niche |
| `platform` | audit | `Platform.name`, `Platform.version` |
| `errno` | audit | Constants on `Error` class? |
| `ctypes` | out | FFI — clashes with introspection rules |
| `mmap` | out | Low-level; defer until needed |

### Concurrent Execution

| Module | Status | Sketch |
|---|---|---|
| `threading` | audit | Smalltalk uses `Process` — POOP equivalent TBD |
| `multiprocessing` | audit | Pairs with `threading` |
| `concurrent` | audit | Futures — `Block.fork()` returning a `Future`? |
| `subprocess` | audit | `Process.run(cmd)` class factory |
| `sched` | out | Niche scheduler |
| `queue` | audit | `Queue` POOP type |
| `contextvars` | out | Implementation detail |

### Networking and Interprocess Communication

| Module | Status | Sketch |
|---|---|---|
| `asyncio` | audit | Huge surface — own proposal |
| `socket` | audit | `Socket.open(addr)` class factory |
| `ssl` | audit | Pairs with `socket` |
| `select` | out | Low-level — `selectors` is preferred |
| `selectors` | out | Low-level multiplexing |
| `signal` | audit | `System.on_signal(sig, block)` |

### Internet Data Handling

| Module | Status | Sketch |
|---|---|---|
| `email` | audit | Own proposal — `Email.parse(s)` |
| `json` | audit | `Json.parse(s)` / `Json.dumps(obj)` |
| `mailbox` | out | Niche legacy |
| `mimetypes` | audit | `Path.mime_type` message |
| `base64` | proposed | See proposal above |
| `binascii` | audit | Pairs with `base64` |
| `quopri` | out | Niche legacy encoding |

### Structured Markup Processing Tools

| Module | Status | Sketch |
|---|---|---|
| `html` | audit | `Str.escape_html()` / `Str.unescape_html()` |
| `xml` | audit | Own proposal — `Xml.parse(s)` |
| `xmlrpc` | out | Legacy protocol |
| `pyexpat` | out | Internal; covered by `xml` if ever |

### Internet Protocols and Support

| Module | Status | Sketch |
|---|---|---|
| `webbrowser` | audit | `System.open_browser(url)` |
| `wsgiref` | out | Reference impl |
| `urllib` | audit | HTTP client — own proposal |
| `http` | audit | Pairs with `urllib` |
| `ftplib` | out | Legacy protocol |
| `poplib` | out | Legacy protocol |
| `imaplib` | out | Legacy protocol |
| `smtplib` | audit | `Smtp` namespace if a mail story emerges |
| `uuid` | proposed | See proposal above |
| `socketserver` | out | Pairs with `socket` if ever |
| `ipaddress` | audit | `IpAddress` POOP type |

### Multimedia Services

| Module | Status | Sketch |
|---|---|---|
| `wave` | out | Niche audio format |
| `colorsys` | out | Tiny niche helper |

### Internationalization

| Module | Status | Sketch |
|---|---|---|
| `gettext` | out | Niche |
| `locale` | audit | `Locale` namespace |

### Program Frameworks

| Module | Status | Sketch |
|---|---|---|
| `turtle` | out | Educational graphics |
| `turtledemo` | out | Pairs with `turtle` |
| `cmd` | out | REPL framework |
| `shlex` | audit | `Str.shell_split()` |

### Graphical User Interfaces

| Module | Status | Sketch |
|---|---|---|
| `tkinter` | out | GUI toolkit — out of scope |

### Development Tools

| Module | Status | Sketch |
|---|---|---|
| `typing` | out | POOP is dynamically typed in the Smalltalk tradition |
| `annotationlib` | out | Pairs with `typing` |
| `pydoc` | out | POOP has no docstring tooling |
| `pydoc_data` | out | Pairs with `pydoc` |
| `doctest` | out | Depends on `repr` (forbidden) |
| `unittest` | audit | POOP testing story TBD |
| `ensurepip` | out | Packaging |
| `venv` | out | Packaging |
| `zipapp` | out | Packaging |
| `idlelib` | out | IDE |

### Debugging and Profiling

| Module | Status | Sketch |
|---|---|---|
| `bdb` | out | Debugger framework — depends on introspection |
| `faulthandler` | out | C-level crash dumps |
| `pdb` | out | Depends on introspection |
| `profile` / `cProfile` / `pstats` | audit | `Block.profile()`? |
| `timeit` | audit | `Block.benchmark()` |
| `trace` | out | Depends on introspection |
| `tracemalloc` | out | Depends on introspection |

### Python Runtime Services

| Module | Status | Sketch |
|---|---|---|
| `sys` | audit | Split: `System`, `Stdout`/`Stderr`, `Args` |
| `sysconfig` | out | Build-time metadata |
| `builtins` | out | POOP *replaces* this |
| `warnings` | out | POOP doesn't have a warning concept |
| `dataclasses` | out | POOP classes don't use decorators |
| `contextlib` | covered | Reachable via `With` |
| `abc` | out | All POOP classes can be subclassed |
| `atexit` | audit | `System.at_exit(block)` |
| `traceback` | out | Depends on introspection |
| `gc` | audit | `System.gc()` |
| `inspect` | out | Forbidden — POOP rejects introspection |
| `site` | out | Site-packages plumbing |

### Custom Python Interpreters

| Module | Status | Sketch |
|---|---|---|
| `code` | out | Embeddable REPL |
| `codeop` | out | Pairs with `code` |

### Importing Modules

| Module | Status | Sketch |
|---|---|---|
| `importlib` | out | POOP forbids imports |
| `zipimport` | out | Pairs with `importlib` |
| `pkgutil` | out | Pairs with `importlib` |
| `modulefinder` | out | Pairs with `importlib` |
| `runpy` | out | Pairs with `importlib` |

### Python Language Services

| Module | Status | Sketch |
|---|---|---|
| `ast` | out | Used internally by POOP itself; not surfaced |
| `symtable` | out | Compiler internal |
| `token` / `tokenize` | out | Lexer internal |
| `keyword` | out | Lexer internal |
| `tabnanny` | out | Linter |
| `pyclbr` | out | Class browser |
| `py_compile` / `compileall` | out | Build helpers |
| `dis` | out | Bytecode disassembler |
| `pickletools` | out | Pairs with `pickle` |
| `opcode` | out | Internal |

### Unix-Specific Services

| Module | Status | Sketch |
|---|---|---|
| `posix` | out | Low-level — covered via `os` if at all |
| `pwd` | audit | `System.user`? |
| `grp` | audit | Pairs with `pwd` |
| `termios` / `tty` / `pty` | out | Low-level TTY |
| `fcntl` | out | Low-level file control |
| `resource` | audit | `System.resource_limit(…)` |
| `syslog` | out | Niche logging |

### Windows-Specific Services

| Module | Status | Sketch |
|---|---|---|
| `msvcrt` | out | Low-level |
| `winreg` | out | Niche registry |
| `winsound` | out | Niche audio |
| `nt` | out | Internal counterpart to `posix` |

### Superseded / Internal / Easter Eggs

| Module | Status | Sketch |
|---|---|---|
| `optparse` | out | Superseded by `argparse`; both out of scope anyway |
| `getopt` | out | Superseded by `argparse` |
| `sre_compile` / `sre_constants` / `sre_parse` | out | `re` internals |
| `encodings` | out | Codec implementations — surfaced via `Str`/`Bytes` |
| `antigravity` | out | Easter egg |
| `this` | out | Easter egg |

This is **scoping work**, not implementation work — the audit should
produce a per-module decision and either a follow-up proposal or a
"stays out" entry. Implementation happens proposal-by-proposal.

## Future work

Items deferred from shipped proposals that need their own follow-up
once a prerequisite exists.

### Complex math (`cmath`) — from the `math` proposal (v0.6.0)

The `Math` namespace deliberately omits `cmath` because it requires
a `Complex` POOP type with a fully-fleshed message API. POOP has a
`Complex` wrapper today (`poop/types/complex.py`) used by literal
transforms and arithmetic, but it does not yet expose the
transcendental surface (`cmath.sqrt`, `cmath.exp`, `cmath.sin`,
`cmath.phase`, `cmath.polar`, `cmath.rect`, `cmath.isclose`,
`cmath.isfinite`/`isinf`/`isnan`, and the constants
`cmath.pi`/`e`/`tau`/`inf`/`nan`/`infj`/`nanj`).

When written, the `cmath` proposal should mirror the shape of the
`math` namespace exactly — a `CMath` namespace-only injection (or
fold the operations onto the existing `Complex` POOP type, TBD),
with the same constant-case rule (lowercase, mirroring source).
Cross-cutting decisions to make first:

- Are `Complex` arithmetic predicates (`.isfinite()` / `.isinf()` /
  `.isnan()`) Float-typed on the real and imaginary parts, or
  defined on the whole `Complex`? Python defines the latter on
  `cmath.*`.
- Should `cmath` and `math` share predicates that take Complex
  (returning Boolean) or duplicate them per type, like Python does?

