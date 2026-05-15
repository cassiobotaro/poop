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

1. **New POOP class `UUID`** in `poop/types/uuid.py`, wrapping
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
   - `UUID(hex=..., bytes=..., int=..., fields=..., bytes_le=...)`
     constructor — mirrors `uuid.UUID(...)` exactly (Python uses
     keyword args for the parse-from-foo variants).
2. **Namespace `uuid`** (lowercase, mirroring Python's module name)
   injected into `DEFAULT_NAMESPACE` (`math`-style, no AST rewrite).
   Module-level functions:
   - `uuid.uuid1(node=None, clock_seq=None)`,
     `uuid.uuid3(namespace, name)`, `uuid.uuid4()`,
     `uuid.uuid5(namespace, name)`,
     `uuid.uuid6(node=None, clock_seq=None)`, `uuid.uuid7()`,
     `uuid.uuid8(a=None, b=None, c=None)` — every variant Python 3.14
     ships, returning `UUID` instances
   - `uuid.getnode() -> Int` (mirrors `uuid.getnode()`)
   - `uuid.UUID` — the class itself, accessible as a module attribute
     just like Python's `uuid.UUID`
3. **Constants** on the `uuid` namespace — every public `uuid.*`
   constant:
   - The four standard namespaces as POOP `UUID` values:
     `uuid.NAMESPACE_DNS`, `uuid.NAMESPACE_URL`,
     `uuid.NAMESPACE_OID`, `uuid.NAMESPACE_X500`
   - The two sentinel UUIDs: `uuid.NIL` (all-zeros), `uuid.MAX`
     (all-ones)
   - The four variant `Str` constants: `uuid.RESERVED_NCS`,
     `uuid.RFC_4122`, `uuid.RESERVED_MICROSOFT`,
     `uuid.RESERVED_FUTURE`

`UuidTransformer` is **namespace-only** (no AST rewrite); it injects
two bindings — `uuid` (lowercase singleton) and `UUID` (the class) —
into `DEFAULT_NAMESPACE` in the same family as `random` / `Random`.

**Type discipline:** every signature exposed by this proposal —
methods on `UUID` instances, methods and constants on the `uuid`
namespace — takes and returns POOP types (`UUID`, `Str`, `Bytes`,
`Int`, `Tuple`). No `uuid.UUID`, raw `bytes`, or `int` leaks across
the boundary.

**Smalltalk reference.**

| Python | Smalltalk (Pharo) | Notes |
|---|---|---|
| `uuid.uuid4()` | `UUID new` | POOP mirrors Python lowercase: `uuid.uuid4()` |
| `uuid.UUID(s)` | `UUID fromString: s` | POOP: `UUID(s)` (the class is in scope) |
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

1. **Namespace `secrets`** (lowercase, mirroring Python's module
   name) injected into `DEFAULT_NAMESPACE` (`math`-style, no AST
   rewrite). No new POOP type (`secrets` has no public class).
2. **Token minting** (`nbytes=None` resolves to `DEFAULT_ENTROPY`,
   mirroring Python):
   - `secrets.token_bytes(nbytes=None) -> Bytes`
   - `secrets.token_hex(nbytes=None) -> Str`
   - `secrets.token_urlsafe(nbytes=None) -> Str`
3. **Secure draws** (parameter names follow Python exactly):
   - `secrets.choice(seq) -> element` (works on any POOP iterable;
     element is a POOP type)
   - `secrets.randbelow(exclusive_upper_bound) -> Int`
   - `secrets.randbits(k) -> Int`
4. **Constant-time comparison:**
   - `secrets.compare_digest(a, b, /) -> Boolean` (positional-only,
     accepts `Str` or `Bytes`; rejects mixed types like Python does)
5. **Constant:**
   - `secrets.DEFAULT_ENTROPY -> Int` (`32` in CPython)

`SecretsTransformer` is **namespace-only**.

**Type discipline:** every signature exposed by this proposal takes
and returns POOP types (`Bytes`, `Str`, `Int`, `Boolean`, plus the
element type for `choice`). No Python primitives leak across the
boundary.

**Smalltalk reference.** No direct mapping in base Pharo. The
nearest analog is `Random new` (NOT cryptographically secure) —
POOP deliberately separates the two: `random` is non-secure;
`secrets` is secure-by-default.

**Out of scope (for v1):**

- `secrets.SystemRandom` class wrapper — duplicates `choice` /
  `randbelow` / `randbits` already on `secrets`.

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

**Proposal — `hashlib` (lowercase module) + `Hash` (class), in the
same dual-binding family as `random` / `Random`.**

1. **New POOP class `Hash`** in `poop/types/hash.py`, wrapping
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
4. **Namespace `hashlib`** (lowercase, mirroring Python's module
   name):
   - `hashlib.new(name, data) -> Hash` (generic constructor — same
     as Python's `hashlib.new`)
   - `hashlib.algorithms_available -> FrozenSet` of `Str`
   - `hashlib.algorithms_guaranteed -> FrozenSet` of `Str`
   - `hashlib.file_digest(path, digest, /) -> Hash` (Python 3.11+;
     `path` is a POOP `Path` — sanctioned receiver-type divergence
     from Python's `fileobj`; the parameter named `digest` matches
     Python's name)
   - `hashlib.Hash` — the class itself, accessible as a module
     attribute just like Python's `hashlib._Hash`

`HashlibTransformer` is **namespace-only**; it injects two
bindings (`hashlib` lowercase singleton + `Hash` class) into
`DEFAULT_NAMESPACE` alongside the new methods on `Bytes`.

**Type discipline:** every signature — methods on `Hash`, the
hash-shortcut and key-derivation methods on `Bytes`, and module-
level `hashlib.*` — takes and returns POOP types (`Hash`, `Bytes`,
`Str`, `Int`, `FrozenSet`, `Path`). No `bytes`, `int`, or raw
`hashlib` object leaks across the boundary.

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

1. **Namespace `tomllib`** (lowercase, mirroring Python's module
   name) injected into `DEFAULT_NAMESPACE` (`math`-style, no AST
   rewrite). No new POOP types — TOML values map onto existing POOP
   types (`Dict` / `List` / `Str` / `Int` / `Float` / `Boolean` /
   `DateTime`).
2. **Parsing — keeping Python's exact names and keyword args:**
   - `tomllib.loads(s, /, *, parse_float=Float) -> Dict` — direct
     mirror of `tomllib.loads`. `parse_float` defaults to `Float`
     (POOP's `Float`, mirroring Python's `float` default).
   - `tomllib.load(path, /, *, parse_float=Float) -> Dict` — mirror
     of `tomllib.load`. Python takes a binary file object; POOP
     takes a POOP `Path` since POOP has no file-object abstraction.
     This is a forced receiver-type divergence; the message name
     and keyword args stay Python's.
3. **Errors:**
   - `tomllib.TOMLDecodeError` — POOP error type wrapping
     `tomllib.TOMLDecodeError` (a `ValueError` subclass in Python).
     Raised by both `loads` and `load` on malformed input.

`TomllibTransformer` is **namespace-only**.

**Type discipline:** every value in the returned `Dict` is a POOP
type. TOML's `date` / `time` / `datetime` map to POOP's `DateTime`
once that proposal lands (see the audit table — `datetime` is
currently `audit`); until then, expose them as ISO-8601 `Str` so
no Python `datetime.datetime` leaks. This is the one place the
proposal trades full type-coverage for ship-now pragmatism, and is
documented explicitly so it can be tightened later. When the
`DateTime` proposal lands, the `tomllib.loads` / `tomllib.load`
return type narrows from `Dict[Str, Str]` (for date-typed values)
to `Dict[Str, DateTime]` automatically.

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

## Expose `string` as POOP messages

Python's `string` module ships ASCII character-class constants
(`ascii_letters`, `digits`, `whitespace`, …) plus `Template` for
`$variable` substitution. None is reachable from POOP today.

**Proposal — `string` (lowercase module) + `Template` class:**

1. **Constants** (each is `Str`): `ascii_letters`, `ascii_lowercase`,
   `ascii_uppercase`, `digits`, `hexdigits`, `octdigits`,
   `punctuation`, `printable`, `whitespace`.
2. **`Template` class** — safe `$var` substitution:
   - `Template(template_str)` constructor
   - `.substitute(mapping) -> Str` (raises on missing key)
   - `.safe_substitute(mapping) -> Str` (leaves missing as-is)
   - `.template -> Str`

**Type discipline:** constants are `Str`; `Template.substitute`
accepts a POOP `Dict`, returns `Str`.

**Out of scope (for v1):**

- `string.Formatter` — `Str.format(spec)` covers the common case.
- `string.capwords` — `Str.title()` is close enough; defer.

## Expose `re` as POOP messages

Python's `re` is unreachable from POOP today; POOP `Str` has no
regex methods. Regex is essential for parsing, validation, and
substitution.

**Proposal — `re` (lowercase module) + `Pattern` and `Match`
POOP classes:**

1. **Module-level shortcuts** mirroring Python: `match`, `search`,
   `fullmatch`, `findall`, `finditer`, `sub`, `subn`, `split`,
   `escape`, `compile`. All take/return POOP types.
2. **`Pattern` class** — `re.compile(...)` returns it; same methods
   as module-level shortcuts (reusing the compiled regex) plus
   `.pattern`, `.flags`, `.groups`, `.groupindex`.
3. **`Match` class** — result of a successful match; methods
   `.group`, `.groups`, `.groupdict`, `.start`, `.end`, `.span`,
   `.expand`; properties `.string`, `.re`. `None`-on-no-match
   becomes POOP `none`.
4. **Flag constants** on `re`: `IGNORECASE`, `MULTILINE`, `DOTALL`,
   `VERBOSE`, `ASCII`, `UNICODE`, `LOCALE`, `DEBUG`.

**Type discipline:** all POOP types — `Str` for patterns/strings,
`Int` for positions, `Tuple`/`Dict` for groups.

**Out of scope (for v1):** `re.Scanner` (legacy), `Match.regs`
(deprecated).

## Expose `difflib` as POOP messages

Python's `difflib` produces text diffs (unified/context/ndiff) and
fuzzy-matches strings. Unreachable from POOP today.

**Proposal — `difflib` (lowercase module) + `SequenceMatcher` class:**

1. **Diff producers** (each returns `List[Str]` of lines, mirroring
   Python):
   `difflib.unified_diff(a, b, ...)`, `difflib.context_diff(a, b, ...)`,
   `difflib.ndiff(a, b)`, `difflib.restore(seq, which)`.
2. **Fuzzy matching:**
   `difflib.get_close_matches(word, possibilities, n=3, cutoff=0.6) -> List[Str]`.
3. **`SequenceMatcher` class** — element-wise diff with detailed
   queries: `.ratio()`, `.get_matching_blocks()`, `.get_opcodes()`,
   `.find_longest_match(...)`.

**Type discipline:** `List[Str]` for line lists, `Float` for ratios,
`Tuple[Int, Int, Int]` for matching blocks.

**Out of scope (for v1):** `HtmlDiff`, `IS_LINE_JUNK` /
`IS_CHARACTER_JUNK` predicates.

## Expose `textwrap` as POOP messages

Python's `textwrap` reflows multi-line strings: `wrap`, `fill`,
`shorten`, `indent`, `dedent`. Unreachable from POOP today.

**Proposal — `textwrap` (lowercase module) + `TextWrapper` class:**

1. **Module-level shortcuts:**
   - `textwrap.wrap(text, width=70, ...) -> List[Str]`
   - `textwrap.fill(text, width=70, ...) -> Str`
   - `textwrap.shorten(text, width, ...) -> Str`
   - `textwrap.indent(text, prefix, predicate=None) -> Str`
   - `textwrap.dedent(text) -> Str`
2. **`TextWrapper` class** — reusable wrapper with tuning knobs
   (`width`, `initial_indent`, `subsequent_indent`, `expand_tabs`,
   `replace_whitespace`, `drop_whitespace`, `fix_sentence_endings`,
   `break_long_words`, `break_on_hyphens`, `tabsize`, `max_lines`,
   `placeholder`). Methods: `.wrap(text)`, `.fill(text)`.

**Type discipline:** `Str` input/output, `Int` widths, `List[Str]`
for `wrap()`.

## Expose `unicodedata` as POOP messages

Python's `unicodedata` gives access to the Unicode Character
Database: normalization, character categorization, name lookup.
Unreachable from POOP today.

**Proposal — `unicodedata` (lowercase module) namespace, no new
POOP type:**

1. **Normalization:** `unicodedata.normalize(form, unistr) -> Str`,
   `unicodedata.is_normalized(form, unistr) -> Boolean`.
2. **Character properties:** `category`, `bidirectional`,
   `combining`, `east_asian_width`, `mirrored`, `decomposition` —
   all take a one-char `Str` and return `Str`/`Int`.
3. **Name lookup:** `unicodedata.name(chr, default=None) -> Str`,
   `unicodedata.lookup(name) -> Str`.
4. **Numeric values:** `decimal`, `digit` (return `Int`),
   `numeric` (returns `Float`).
5. **Version:** `unicodedata.unidata_version -> Str`.

**Type discipline:** `Str` for characters/names, `Int` for combining
classes, `Float` for `numeric`, `Boolean` for `is_normalized`.

**Out of scope (for v1):** the internal `ucd_3_2_0` private object.

## Expose `struct` as POOP messages

Python's `struct` packs/unpacks binary data via format strings (`I`,
`H`, `<i`, `>Q`, …). Unreachable from POOP today; necessary for
binary file formats and network protocols.

**Proposal — `struct` (lowercase module) + `Struct` class:**

1. **Module-level shortcuts** (each takes a format `Str`):
   `struct.pack(format, *values) -> Bytes`,
   `struct.unpack(format, buffer) -> Tuple`,
   `struct.pack_into(format, buffer, offset, *values) -> NoneClass`,
   `struct.unpack_from(format, buffer, offset=0) -> Tuple`,
   `struct.iter_unpack(format, buffer) -> Map`,
   `struct.calcsize(format) -> Int`.
2. **`Struct` class** — pre-compiled format for reuse:
   - `Struct(format)` constructor
   - `.pack`, `.unpack`, `.pack_into`, `.unpack_from`,
     `.iter_unpack` mirroring module-level
   - `.format -> Str`, `.size -> Int`
3. **`struct.error`** — POOP error type for format mismatches.

**Type discipline:** `Bytes` in/out for buffers, `Tuple` for
unpacked values (each element wrapped to POOP type per format char),
`Int` for sizes/offsets.

## Expose `codecs` as POOP messages

Python's `codecs` is the codec registry behind `str.encode` /
`bytes.decode`. Most use is already covered by `Str.encode` /
`Bytes.decode` on POOP types; the module is needed for less common
codecs (`rot_13`, `hex_codec`, `base64_codec`) and incremental
encoders.

**Proposal — `codecs` (lowercase module) namespace, narrow surface:**

1. **Codec lookup:** `codecs.encode(obj, encoding='utf-8', errors='strict') -> Bytes`,
   `codecs.decode(obj, encoding='utf-8', errors='strict') -> Str`.
2. **BOMs (constants):** `codecs.BOM_UTF8`, `BOM_UTF16`,
   `BOM_UTF16_LE`, `BOM_UTF16_BE`, `BOM_UTF32`, `BOM_UTF32_LE`,
   `BOM_UTF32_BE` (each `Bytes`).
3. **Lookup metadata:** `codecs.lookup(encoding) -> CodecInfo`
   returning a POOP record with `.name`, `.encode`, `.decode`,
   `.incrementalencoder`, `.incrementaldecoder`.

**Type discipline:** `Bytes`/`Str` end-to-end. No leaks.

**Out of scope (for v1):**

- Incremental encoder/decoder API and `StreamReader`/`StreamWriter`
  — pair with future streaming I/O proposal.
- `register` / `register_error` — extension hooks; defer.

## Expose `datetime` as POOP messages

Python's `datetime` ships five canonical types (`date`, `time`,
`datetime`, `timedelta`, `tzinfo`) plus `timezone`. Unreachable from
POOP today and a hard dependency of `tomllib`, logging, file
metadata, and almost every domain model.

**Proposal — `datetime` (lowercase module) + five POOP classes:**

1. **`Date`** — `Date(year, month, day)`, `Date.today()`,
   `Date.fromisoformat(s)`, `Date.fromtimestamp(t)`. Properties
   `.year`/`.month`/`.day`, methods `.weekday()`, `.isoweekday()`,
   `.isoformat()`, `.strftime(fmt)`, arithmetic with `TimeDelta`.
2. **`Time`** — `Time(hour, minute, second, microsecond, tzinfo)`,
   `Time.fromisoformat(s)`. Same property/method shape as `Date`.
3. **`DateTime`** — `DateTime(year, month, day, hour, …, tzinfo)`,
   `DateTime.now(tz=None)`, `DateTime.utcnow()` (deprecated alias
   ok), `DateTime.fromtimestamp(t, tz=None)`,
   `DateTime.fromisoformat(s)`, `.timestamp()`, `.astimezone(tz)`.
4. **`TimeDelta`** — `TimeDelta(days, seconds, microseconds, ...)`,
   arithmetic between `DateTime`s yields `TimeDelta`.
5. **`TimeZone`** — `TimeZone(offset, name=None)`,
   `TimeZone.utc` constant.
6. **`datetime` namespace** binds the five classes (just like
   Python's `datetime.date`, `datetime.time`, etc. are accessible
   as module attributes).

**Type discipline:** all POOP types — `Int`/`Float` for components,
`Str` for ISO strings, `Bytes` for `__bytes__` if exposed.

**Out of scope (for v1):**

- The abstract `tzinfo` extension protocol — POOP users get
  `TimeZone`; custom subclasses defer.
- `datetime.MINYEAR`/`MAXYEAR` integer constants — expose if asked.

## Expose `zoneinfo` as POOP messages

Python's `zoneinfo` (3.9+) provides IANA timezone database access:
`ZoneInfo("America/Sao_Paulo")` returns a `tzinfo` subclass. Pairs
directly with `datetime`'s `TimeZone`.

**Proposal — `zoneinfo` (lowercase module) + `ZoneInfo` class:**

1. **`ZoneInfo` class** — `ZoneInfo(key)` looks up by IANA name;
   `ZoneInfo.from_file(file_obj, key)`,
   `ZoneInfo.no_cache(key)`,
   `ZoneInfo.clear_cache(only_keys=None)`. Property `.key -> Str`.
2. **Module-level helpers:**
   `zoneinfo.available_timezones() -> Set[Str]`,
   `zoneinfo.reset_tzpath(to=None)`.
3. **`ZoneInfoNotFoundError`** — POOP error for missing zones.
4. **Tzpath** — `zoneinfo.TZPATH` exposed as `Tuple[Str]`.

**Type discipline:** `Str` for keys, `Set[Str]` for the timezone
roster, `Tuple[Str]` for the search path.

**Out of scope (for v1):** `InvalidTZPathWarning` (warning system
out of scope).

## Expose `calendar` as POOP messages

Python's `calendar` formats month/year calendars and answers
calendar queries (leap years, weekdays). Niche but small.

**Proposal — `calendar` (lowercase module) + `Calendar` class:**

1. **Module-level helpers:**
   `calendar.isleap(year) -> Boolean`,
   `calendar.leapdays(y1, y2) -> Int`,
   `calendar.weekday(year, month, day) -> Int`,
   `calendar.monthrange(year, month) -> Tuple[Int, Int]`,
   `calendar.month(year, month, w=0, l=0) -> Str` (text rendering),
   `calendar.calendar(year, w=2, l=1, c=6, m=3) -> Str`,
   `calendar.timegm(time_tuple) -> Int`.
2. **`Calendar` class** for iterating dates:
   - `Calendar(firstweekday=0)` constructor
   - `.iterweekdays() -> Map[Int]`,
     `.itermonthdates(year, month) -> Map[Date]`,
     `.itermonthdays(year, month) -> Map[Int]`, …
3. **Weekday constants:** `calendar.MONDAY` … `calendar.SUNDAY`
   (each `Int`).

**Type discipline:** `Int` for years/months/days, `Boolean` for
leap predicate, `Str` for formatted output.

**Out of scope (for v1):**

- `HTMLCalendar`, `LocaleTextCalendar`, `LocaleHTMLCalendar` —
  niche output formats.

## Expose `heapq` as POOP messages

Python's `heapq` implements a binary min-heap on a regular list.
The functions mutate the underlying list in-place.

**Proposal — `heapq` (lowercase module) namespace, no new POOP
type (operations work on POOP `List`):**

1. **In-place operations** (each returns `none`, mutates the list):
   `heapq.heappush(heap, item)`, `heapq.heappop(heap) -> element`,
   `heapq.heappushpop(heap, item) -> element`,
   `heapq.heapreplace(heap, item) -> element`,
   `heapq.heapify(x) -> NoneClass`.
2. **Queries:**
   `heapq.nlargest(n, iterable, key=None) -> List`,
   `heapq.nsmallest(n, iterable, key=None) -> List`,
   `heapq.merge(*iterables, key=None, reverse=False) -> Map`.

**Type discipline:** POOP `List` in, POOP elements out. `heappop`
on an empty heap raises `IndexError` (Python's behaviour).

**Out of scope (for v1):** `_heapify_max` and the other private
max-heap variants.

## Expose `bisect` as POOP messages

Python's `bisect` does binary search and ordered insertion on
sorted sequences.

**Proposal — `bisect` (lowercase module) namespace:**

1. **Binary search:**
   `bisect.bisect_left(a, x, lo=0, hi=None, *, key=None) -> Int`,
   `bisect.bisect_right(a, x, lo=0, hi=None, *, key=None) -> Int`,
   `bisect.bisect(a, x, ...)` (alias for `bisect_right`).
2. **Ordered insertion** (mutate the list, return `none`):
   `bisect.insort_left(a, x, lo=0, hi=None, *, key=None) -> NoneClass`,
   `bisect.insort_right(a, x, ...)`, `bisect.insort(a, x, ...)`.

**Type discipline:** `List` in, `Int` for index queries, `none`
for in-place mutators.

## Expose `array` as POOP messages

Python's `array.array` is a homogeneous, memory-compact sequence.
Niche in pure Python (NumPy/struct do most jobs) but useful for
fixed-typecode storage.

**Proposal — `array` (lowercase module) + `Array` class:**

1. **`Array` class:**
   - `Array(typecode, initializer=None)` — typecode is `Str`
     (`'i'`, `'B'`, `'f'`, …)
   - Standard sequence API: `.append`, `.extend`, `.insert`,
     `.pop`, `.remove`, `.count`, `.index`, `.reverse`, `.len()`,
     iteration via `.do(block)`, `at(i)`, `.slice(...)`.
   - Conversion: `.tobytes() -> Bytes`, `.tolist() -> List`,
     `.frombytes(b)`, `.fromlist(l)`, `.fromstring` (deprecated).
   - Metadata: `.typecode -> Str`, `.itemsize -> Int`.
2. **`array.typecodes`** module attribute — `Str` of valid codes.

**Type discipline:** typecode-appropriate POOP elements; `Bytes`
for raw, `List` for conversion.

**Out of scope (for v1):** `array.fromfile`/`tofile` — pair with
streaming I/O.

## Expose `weakref` as POOP messages

Python's `weakref` creates references that don't prevent garbage
collection. Niche — mostly for caches and circular-reference
breakers. Low priority but worth proposing.

**Proposal — `weakref` (lowercase module) + class set:**

1. **`weakref` namespace shortcuts:**
   `weakref.ref(obj, callback=None) -> WeakRef`,
   `weakref.proxy(obj, callback=None)`,
   `weakref.getweakrefcount(obj) -> Int`,
   `weakref.getweakrefs(obj) -> List`.
2. **`WeakRef` class** — call returns the live object or `none`.
3. **`WeakSet` / `WeakKeyDictionary` / `WeakValueDictionary`** —
   POOP collections with weak-reference semantics.

**Type discipline:** POOP types; `none` for dead refs.

**Out of scope (for v1):** `finalize`, `WeakMethod` — niche.

## Expose `copy` as POOP messages

Python's `copy` does shallow and deep object copying. `copy.copy`
and `copy.deepcopy` are the entire public surface.

**Proposal — `copy` (lowercase module) namespace:**

1. `copy.copy(obj) -> Object` — shallow copy.
2. `copy.deepcopy(obj, memo=None) -> Object` — recursive deep copy.
3. `copy.Error` — POOP error wrapping `copy.Error`.

**Type discipline:** returns the same POOP type as the input.

**Out of scope (for v1):** `copy.replace` (3.13+) — small but
trivially added later if asked.

## Expose `pprint` as POOP messages

Python's `pprint` pretty-prints data structures (multi-line,
indented). Useful for debugging.

**Proposal — `pprint` (lowercase module) + `PrettyPrinter` class:**

1. **Module-level shortcuts:**
   `pprint.pprint(obj, ...) -> NoneClass` (prints to stdout),
   `pprint.pformat(obj, ...) -> Str`,
   `pprint.pp(obj, ...)` (3.8+ alias),
   `pprint.isreadable(obj) -> Boolean`,
   `pprint.isrecursive(obj) -> Boolean`,
   `pprint.saferepr(obj) -> Str`.
2. **`PrettyPrinter` class** — reusable with `indent`, `width`,
   `depth`, `compact`, `sort_dicts`, `underscore_numbers` knobs.

**Type discipline:** `Str` output, `Boolean` for predicates.

## Expose `enum` as POOP messages

Python's `enum` provides `Enum`, `IntEnum`, `StrEnum`, `Flag`,
`IntFlag` — typed enumeration classes. POOP user classes can
already support class-side singletons; this proposal codifies the
explicit `Enum` base for ergonomics.

**Proposal — `enum` (lowercase module) + class set:**

1. **`Enum` base** — `class Color(Enum): RED = 1; GREEN = 2`.
   Members are class-side `Enum` instances accessible by name and
   value (`Color.RED`, `Color(1)`, `Color["RED"]`).
2. **Specialised bases:** `IntEnum`, `StrEnum` (3.11+),
   `IntFlag`, `Flag`, `ReprEnum` (3.11+).
3. **`auto()`** for sequential value generation.
4. **Method/property:** `.name -> Str`, `.value -> Object`,
   `Enum.iter()` for member iteration.
5. **Decorators:** `@enum.unique`, `@enum.verify`,
   `@enum.member`, `@enum.nonmember` (3.12+).

**Type discipline:** members are POOP `Enum` instances;
`.value` returns whatever POOP type the user assigned.

**Out of scope (for v1):** `EnumType` metaclass introspection
(POOP forbids introspection).

## Expose `graphlib` as POOP messages

Python's `graphlib` is small: just `TopologicalSorter` for graph
topo-sorts (3.9+). Useful for dependency resolution.

**Proposal — `graphlib` (lowercase module) + `TopologicalSorter`
class:**

1. **`TopologicalSorter` class:**
   - `TopologicalSorter(graph=None)` — graph as `Dict[node, Iterable[predecessors]]`
   - `.add(node, *predecessors)` for incremental building
   - `.prepare()` — finalize structure
   - `.is_active() -> Boolean`,
     `.get_ready() -> Tuple[node]`,
     `.done(*nodes)`,
     `.static_order() -> Tuple[node]` (one-shot full order)
2. **`CycleError`** — POOP error if the graph has cycles.

**Type discipline:** generic over POOP node types; `Tuple` for
returned orderings.

## Expose `decimal` as POOP messages

Python's `decimal` provides arbitrary-precision decimal arithmetic
— critical for money, accounting, and any computation where
binary-float rounding error is unacceptable.

**Proposal — `decimal` (lowercase module) + `Decimal` class:**

1. **`Decimal` class** wrapping Python's `decimal.Decimal`:
   - `Decimal(value)` — accepts `Int`, `Str` (`"3.14"`), `Tuple`
     (sign, digits, exponent), `Float`. Mirrors Python.
   - All arithmetic operators (`+ - * / // % **`) returning
     `Decimal`.
   - `.quantize(exp, rounding=None)`, `.normalize()`, `.adjusted()`,
     `.as_tuple()`, `.as_integer_ratio()`, `.is_finite()`,
     `.is_infinite()`, `.is_nan()`, `.is_signed()`, `.is_zero()`,
     `.sqrt()`, `.ln()`, `.log10()`, `.exp()`.
2. **`decimal` module namespace:**
   - `decimal.Decimal` — class attribute alias.
   - `decimal.getcontext() -> Context`,
     `decimal.setcontext(ctx) -> NoneClass`,
     `decimal.localcontext(ctx=None)` (with-block context manager).
   - Rounding constants: `ROUND_UP`, `ROUND_DOWN`, `ROUND_HALF_UP`,
     `ROUND_HALF_DOWN`, `ROUND_HALF_EVEN`, `ROUND_CEILING`,
     `ROUND_FLOOR`, `ROUND_05UP`.
   - Signal classes: `InvalidOperation`, `DivisionByZero`,
     `Overflow`, `Underflow`, `Inexact`, `Rounded`, `Subnormal`,
     `Clamped`, `FloatOperation`, `DecimalException`.
3. **`Context` class** — precision, rounding, traps, flags.

**Type discipline:** `Decimal` is its own POOP type with full
arithmetic; conversions cross to `Int`/`Float`/`Str` explicitly.

**Out of scope (for v1):** the C-vs-Python implementation toggle;
historical traps inherited from `cdecimal`.

## Expose `fractions` as POOP messages

Python's `fractions.Fraction` is exact rational arithmetic.

**Proposal — `fractions` (lowercase module) + `Fraction` class:**

1. **`Fraction` class:**
   - `Fraction(numerator=0, denominator=1)`,
     `Fraction.from_float(f)`, `Fraction.from_decimal(d)`,
     `Fraction(string)` — `"3/4"` or `"0.25"`.
   - `.numerator -> Int`, `.denominator -> Int`,
     `.limit_denominator(max=10**6) -> Fraction`,
     `.as_integer_ratio() -> Tuple[Int, Int]`.
   - All arithmetic operators returning `Fraction` (or `Float` for
     mixed-type promotion, mirroring Python).
2. **`fractions` namespace:** binds `Fraction` class.

**Type discipline:** `Fraction` is its own POOP type. Mixed
arithmetic with `Int` returns `Fraction`; with `Float` returns
`Float`.

**Out of scope (for v1):** `Fraction.from_number_str` (private),
the `_RATIONAL_FORMAT` regex.

## Expose `statistics` as POOP messages

Python's `statistics` covers mean/median/mode, variance, stdev,
quantiles, correlation. Useful for any data summarisation.

**Proposal — `statistics` (lowercase module) + `NormalDist` class:**

1. **Central tendency:**
   `statistics.mean(data) -> Float`,
   `statistics.fmean(data, weights=None) -> Float`,
   `statistics.geometric_mean(data) -> Float`,
   `statistics.harmonic_mean(data, weights=None) -> Float`,
   `statistics.median(data) -> Float | Int`,
   `statistics.median_low(data)`, `median_high(data)`,
   `median_grouped(data, interval=1)`,
   `statistics.mode(data) -> element`,
   `statistics.multimode(data) -> List`.
2. **Spread:**
   `statistics.pstdev`, `statistics.pvariance`, `statistics.stdev`,
   `statistics.variance` (all `(data, xbar=None) -> Float`).
3. **Quantiles:**
   `statistics.quantiles(data, *, n=4, method='exclusive') -> List[Float]`.
4. **Correlation:**
   `statistics.correlation(x, y, *, method='linear') -> Float`,
   `statistics.covariance(x, y) -> Float`,
   `statistics.linear_regression(x, y, *, proportional=False) -> Tuple`.
5. **`NormalDist` class** for Gaussian distributions:
   `NormalDist(mu=0.0, sigma=1.0)`, `.from_samples(data)`,
   `.mean`, `.stdev`, `.variance`, `.median`, `.mode`,
   `.cdf(x)`, `.pdf(x)`, `.inv_cdf(p)`, `.zscore(x)`, `.samples(n)`,
   `.overlap(other)`, `.quantiles(n=4)`, arithmetic between
   `NormalDist`s.
6. **`StatisticsError`** — POOP error for empty/invalid data.

**Type discipline:** numerical inputs are POOP `Int`/`Float`;
returns POOP `Float`/`Int`. `mode`/`multimode` return whatever the
elements are.

**Out of scope (for v1):** the `_sum` private helper; `Decimal`-
aware variants surface naturally once `decimal` lands.

## Expose `filecmp` as POOP messages

Python's `filecmp` compares files and directory trees: shallow
metadata or full content comparison.

**Proposal — `filecmp` (lowercase module) + `dircmp` class:**

1. **File comparison:**
   `filecmp.cmp(f1, f2, shallow=True) -> Boolean`,
   `filecmp.cmpfiles(dir1, dir2, common, shallow=True) -> Tuple[List, List, List]`.
2. **`dircmp` class** for recursive directory comparison:
   `dircmp(a, b, ignore=None, hide=None)` with attributes
   `.left_only`, `.right_only`, `.common`, `.diff_files`,
   `.same_files`, `.funny_files`, `.subdirs`, plus
   `.report()`/`.report_partial_closure()`/`.report_full_closure()`.
3. **`filecmp.clear_cache() -> NoneClass`** — drop comparison cache.

**Type discipline:** `Path` for inputs, `Boolean` for equality,
`List[Str]` for file-name groupings.

## Expose `tempfile` as POOP messages

Python's `tempfile` creates secure temporary files/directories.
Unreachable from POOP today and a common need for tests and
intermediate processing.

**Proposal — `tempfile` (lowercase module) + class set:**

1. **Module-level shortcuts:**
   `tempfile.mkstemp(suffix=None, prefix=None, dir=None, text=False) -> Tuple[Int, Path]`,
   `tempfile.mkdtemp(suffix=None, prefix=None, dir=None) -> Path`,
   `tempfile.gettempdir() -> Path`,
   `tempfile.gettempprefix() -> Str`,
   `tempfile.gettempdirb() -> Bytes`.
2. **`TemporaryFile` / `NamedTemporaryFile` / `SpooledTemporaryFile`
   / `TemporaryDirectory`** classes — context-manager friendly via
   `With`. Properties expose `.name -> Path`.
3. **`tempfile.tempdir`** — module-level mutable default. Read/write.

**Type discipline:** `Path` for all filesystem paths, `Str` for
prefixes, `Int` for file descriptors.

**Out of scope (for v1):** `_RandomNameSequence` internal class.

## Expose `glob` as POOP messages

Python's `glob` does shell-style wildcard expansion (`*.py`,
`**/*.txt`). Largely covered by `Path.glob` already, but the
module-level functions are useful too.

**Proposal — `glob` (lowercase module) namespace:**

1. **Wildcard expansion:**
   `glob.glob(pathname, *, root_dir=None, dir_fd=None, recursive=False, include_hidden=False) -> List[Path]`,
   `glob.iglob(pathname, ...) -> Map[Path]`,
   `glob.escape(pathname) -> Str`,
   `glob.translate(pat, *, recursive=False, include_hidden=False, seps=None) -> Str`
   (3.13+).

**Type discipline:** `Path` returns, `Str` for patterns.

## Expose `fnmatch` as POOP messages

Python's `fnmatch` tests filenames against Unix shell-style
patterns. Tiny module.

**Proposal — `fnmatch` (lowercase module) namespace:**

1. **Pattern matching:**
   `fnmatch.fnmatch(filename, pattern) -> Boolean`,
   `fnmatch.fnmatchcase(filename, pattern) -> Boolean`,
   `fnmatch.filter(names, pattern) -> List[Str]`,
   `fnmatch.translate(pattern) -> Str` (compile to regex).

**Type discipline:** `Boolean` for matches, `List[Str]` for filter,
`Str` for the regex translation.

## Expose `shutil` as POOP messages

Python's `shutil` is high-level file operations: copy, move, remove
trees, archive create/extract, disk usage, terminal size.

**Proposal — `shutil` (lowercase module) namespace:**

1. **Copy:** `shutil.copy(src, dst, follow_symlinks=True) -> Path`,
   `copy2(src, dst, ...) -> Path`,
   `copyfile(src, dst, ...)`,
   `copytree(src, dst, symlinks=False, ignore=None, copy_function=copy2, ignore_dangling_symlinks=False, dirs_exist_ok=False) -> Path`,
   `copymode(src, dst)`, `copystat(src, dst)`, `copyfileobj(...)`.
2. **Move/remove:**
   `shutil.move(src, dst, copy_function=copy2) -> Path`,
   `shutil.rmtree(path, ignore_errors=False, onexc=None) -> NoneClass`,
   `shutil.which(cmd, mode=os.F_OK | os.X_OK, path=None) -> Path | NoneClass`.
3. **Archives:**
   `shutil.make_archive(base_name, format, root_dir=None, base_dir=None, ...) -> Path`,
   `shutil.unpack_archive(filename, extract_dir=None, format=None, ...) -> NoneClass`,
   `shutil.get_archive_formats() -> List[Tuple]`,
   `shutil.get_unpack_formats() -> List[Tuple]`,
   `shutil.register_archive_format(...)`, `register_unpack_format(...)`.
4. **Disk/terminal info:**
   `shutil.disk_usage(path) -> Tuple[Int, Int, Int]` (total/used/free),
   `shutil.get_terminal_size(fallback=(80, 24)) -> Tuple[Int, Int]`,
   `shutil.chown(path, user=None, group=None) -> NoneClass`.

**Type discipline:** `Path` end-to-end; `Bytes` for binary copy
helpers; `Int` for sizes.

**Out of scope (for v1):** `ignore_patterns` factory and the
`copy_function` callback argument plumbing — defer to a
followup proposal.

## Expose `pickle` as POOP messages

Python's `pickle` serialises arbitrary objects to bytes. Useful for
caches and inter-process state; comes with the standard security
warnings about loading untrusted pickles.

**Proposal — `pickle` (lowercase module) + `Pickler`/`Unpickler` classes:**

1. **Module-level shortcuts:**
   `pickle.dumps(obj, protocol=None, *, fix_imports=True) -> Bytes`,
   `pickle.loads(data, *, fix_imports=True, encoding='ASCII', errors='strict', buffers=None) -> Object`.
2. **`Path`-based read/write helpers** (POOP convention, not in
   Python proper):
   `pickle.dump(obj, path, ...)`, `pickle.load(path, ...)` —
   path-based instead of file-object-based.
3. **`Pickler` / `Unpickler` classes** for streaming and
   customising via `persistent_id`/`persistent_load` hooks.
4. **Constants:** `pickle.HIGHEST_PROTOCOL`, `DEFAULT_PROTOCOL`,
   `PROTOCOL_*` levels.
5. **`PickleError`, `PicklingError`, `UnpicklingError`** — POOP
   error hierarchy.

**Type discipline:** `Bytes` for serialised form, `Object` for
deserialised (true to Python's dynamic-typed `loads`).

**Out of scope (for v1):**

- `pickletools` (introspection of pickle streams) — pairs with the
  introspection ban.
- `__reduce__` protocol hook — POOP user classes can implement it,
  but the protocol isn't formally documented here.

## Expose `sqlite3` as POOP messages

Python's `sqlite3` ships with stdlib and is the right zero-config
relational store for POOP programs. Unreachable from POOP today.

**Proposal — `sqlite3` (lowercase module) + class set:**

1. **Module-level entry:**
   `sqlite3.connect(database, timeout=5.0, detect_types=0, isolation_level='', check_same_thread=True, factory=None, cached_statements=128, uri=False, *, autocommit=False) -> Connection`.
2. **`Connection` class:**
   `.cursor() -> Cursor`, `.commit()`, `.rollback()`, `.close()`,
   `.execute(sql, params=()) -> Cursor`,
   `.executemany(sql, seq) -> Cursor`,
   `.executescript(script) -> Cursor`,
   `.create_function(name, narg, func, *, deterministic=False)`,
   `.create_aggregate(name, narg, agg_class)`,
   `.create_collation(name, callable)`,
   `.interrupt()`, `.iterdump() -> Map[Str]`,
   `.backup(target, *, pages=-1, progress=None, name='main', sleep=0.250)`.
3. **`Cursor` class:**
   `.execute`, `.executemany`, `.executescript`, `.fetchone() -> Tuple | NoneClass`,
   `.fetchmany(size=None) -> List[Tuple]`,
   `.fetchall() -> List[Tuple]`, iteration as POOP iterable,
   `.rowcount -> Int`, `.lastrowid -> Int | NoneClass`,
   `.description -> Tuple`, `.arraysize -> Int`.
4. **`Row` class** — dict-like row access by column name.
5. **Constants:** `sqlite3.version`, `sqlite3.sqlite_version`,
   `sqlite3.PARSE_DECLTYPES`, `sqlite3.PARSE_COLNAMES`.
6. **Errors:** `Warning`, `Error`, `InterfaceError`,
   `DatabaseError`, `DataError`, `OperationalError`,
   `IntegrityError`, `InternalError`, `ProgrammingError`,
   `NotSupportedError` — POOP error hierarchy.
7. **Adapters/converters:** `sqlite3.register_adapter(type, func)`,
   `sqlite3.register_converter(typename, func)`.

**Type discipline:** `Connection`/`Cursor`/`Row` are POOP types;
SQL strings are `Str`; bound parameters are POOP collections.

**Out of scope (for v1):** `complete_statement` (SQLite-shell-style
helper), `enable_callback_tracebacks` (debug-only).

## Expose `zlib` as POOP messages

Python's `zlib` provides DEFLATE compression and CRC32/Adler32
checksums.

**Proposal — `zlib` (lowercase module) + `Compress`/`Decompress`
classes:**

1. **One-shot:** `zlib.compress(data, level=-1, wbits=15) -> Bytes`,
   `zlib.decompress(data, wbits=15, bufsize=16384) -> Bytes`.
2. **Streaming:** `zlib.compressobj(...) -> Compress`,
   `zlib.decompressobj(...) -> Decompress` with `.compress`,
   `.decompress`, `.flush`, `.copy` methods.
3. **Checksums:** `zlib.adler32(data, value=1) -> Int`,
   `zlib.crc32(data, value=0) -> Int`.
4. **Constants:** `zlib.MAX_WBITS`, `Z_BEST_COMPRESSION`,
   `Z_BEST_SPEED`, `Z_DEFAULT_COMPRESSION`, `Z_FILTERED`,
   `Z_HUFFMAN_ONLY`, etc.
5. **`zlib.error`** POOP error.

**Type discipline:** `Bytes` in/out, `Int` for checksums and levels.

## Expose `gzip` as POOP messages

Python's `gzip` reads/writes RFC 1952 gzip files; built on `zlib`.

**Proposal — `gzip` (lowercase module) + `GzipFile` class:**

1. **Shortcuts (path-based, POOP convention):**
   `gzip.compress(data, compresslevel=9) -> Bytes`,
   `gzip.decompress(data) -> Bytes`,
   `gzip.open(path, mode='rb', compresslevel=9, ...) -> GzipFile`.
2. **`GzipFile` class** with `.read`, `.write`, `.close`, `.flush`,
   `.seek`, `.tell`, used inside `With`.

**Type discipline:** `Bytes` in/out, `Path` for files.

## Expose `bz2` as POOP messages

Mirror of `gzip` for bzip2.

**Proposal — `bz2` (lowercase module) + class set:**

1. **Shortcuts:** `bz2.compress(data, compresslevel=9) -> Bytes`,
   `bz2.decompress(data) -> Bytes`,
   `bz2.open(path, mode='rb', compresslevel=9, ...) -> BZ2File`.
2. **Streaming:** `bz2.BZ2Compressor(compresslevel=9)`,
   `bz2.BZ2Decompressor()`.
3. **`BZ2File` class** mirroring `GzipFile`'s shape.

**Type discipline:** identical to `gzip`.

## Expose `lzma` as POOP messages

Mirror of `gzip`/`bz2` for LZMA/XZ.

**Proposal — `lzma` (lowercase module) + class set:**

1. **Shortcuts:** `lzma.compress(data, format=FORMAT_XZ, check=CHECK_NONE, preset=None, filters=None) -> Bytes`,
   `lzma.decompress(data, format=FORMAT_AUTO, memlimit=None, filters=None) -> Bytes`,
   `lzma.open(path, mode='rb', *, format=None, check=-1, preset=None, filters=None, encoding=None, errors=None, newline=None) -> LZMAFile`.
2. **Streaming:** `LZMACompressor`, `LZMADecompressor`.
3. **Constants:** `FORMAT_XZ`, `FORMAT_ALONE`, `FORMAT_RAW`,
   `FORMAT_AUTO`, `CHECK_NONE`/`CHECK_CRC32`/`CHECK_CRC64`/
   `CHECK_SHA256`, `PRESET_DEFAULT`, `PRESET_EXTREME`.

**Type discipline:** identical pattern to `gzip`/`bz2`.

## Expose `zipfile` as POOP messages

Python's `zipfile` reads/writes ZIP archives.

**Proposal — `zipfile` (lowercase module) + class set:**

1. **`ZipFile` class:**
   `ZipFile(file, mode='r', compression=ZIP_STORED, allowZip64=True, compresslevel=None, *, strict_timestamps=True, metadata_encoding=None)`,
   plus `.read(name) -> Bytes`, `.write(filename, arcname=None)`,
   `.writestr(zinfo_or_arcname, data)`, `.extract(member, path=None, pwd=None) -> Path`,
   `.extractall(path=None, members=None, pwd=None)`,
   `.namelist() -> List[Str]`, `.infolist() -> List[ZipInfo]`,
   `.getinfo(name) -> ZipInfo`, `.setpassword(pwd)`,
   `.testzip() -> Str | NoneClass`, `.close()`.
2. **`ZipInfo` class** for per-entry metadata.
3. **`Path` class** in `zipfile.Path` — a POSIX-like API over a
   ZipFile (already overlaps with POOP `Path`; namespace as
   `zipfile.Path`).
4. **Compression constants:** `ZIP_STORED`, `ZIP_DEFLATED`,
   `ZIP_BZIP2`, `ZIP_LZMA`.
5. **Errors:** `BadZipFile`, `LargeZipFile`.

**Type discipline:** `Bytes` for content, `Path` for filesystem,
`Str` for archive names.

## Expose `tarfile` as POOP messages

Python's `tarfile` reads/writes TAR archives (uncompressed +
gzip/bz2/lzma compressed).

**Proposal — `tarfile` (lowercase module) + class set:**

1. **`TarFile` class** with `.open(name, mode='r')`-style class
   methods (or POOP factory),
   `.add(name, arcname=None, recursive=True, *, filter=None)`,
   `.extract(member, path='', set_attrs=True, *, numeric_owner=False, filter=None)`,
   `.extractall(path='.', members=None, *, numeric_owner=False, filter='data')`,
   `.list(verbose=True, *, members=None)`,
   `.getnames() -> List[Str]`,
   `.getmember(name) -> TarInfo`,
   `.getmembers() -> List[TarInfo]`,
   `.close()`.
2. **`TarInfo` class** for per-entry metadata.
3. **Constants:** `tarfile.DEFAULT_FORMAT`, `USTAR_FORMAT`,
   `GNU_FORMAT`, `PAX_FORMAT`, `ENCODING`.
4. **Filters** (3.12+ security): `tarfile.data_filter`,
   `fully_trusted_filter`, `tar_filter` for safe extraction.
5. **Errors:** `TarError`, `ReadError`, `CompressionError`,
   `StreamError`, `ExtractError`, `HeaderError`, `FilterError`,
   `AbsolutePathError`, `OutsideDestinationError`,
   `SpecialFileError`, `AbsoluteLinkError`, `LinkOutsideDestinationError`.

**Type discipline:** `Bytes` content, `Path` filesystem, `Str`
archive names.

**Out of scope (for v1):** the historical `is_tarfile(path) -> Boolean`
module function — promoted to `TarFile.is_tarfile(path)` class
method per modern Python convention.

## Expose `compression` as POOP messages

Python 3.14 introduces `compression` as an umbrella package
exposing sub-modules `compression.gzip`, `compression.bz2`,
`compression.lzma`, `compression.zlib`, `compression.zstd`. POOP
mirrors the umbrella.

**Proposal — `compression` (lowercase namespace) attribute-access
to the underlying compression modules:**

1. **Attribute namespaces:** `compression.zlib`, `compression.gzip`,
   `compression.bz2`, `compression.lzma`, `compression.zstd` — each
   binds the same singleton as the individual lowercase namespace
   proposals (above).
2. **No new API surface** beyond the umbrella convenience.

**Type discipline:** inherits from the individual module proposals.

**Out of scope (for v1):** anything in `compression.zstd` until
Python 3.14's API stabilises.

## Expose `csv` as POOP messages

Python's `csv` reads/writes RFC 4180 CSV files with configurable
dialects.

**Proposal — `csv` (lowercase module) + reader/writer/dialect classes:**

1. **Module-level shortcuts:**
   `csv.reader(iterable, dialect='excel', **fmtparams) -> Reader`,
   `csv.writer(writable, dialect='excel', **fmtparams) -> Writer`,
   `csv.DictReader(file, fieldnames=None, restkey=None, restval=None, dialect='excel', *args, **kwds)`,
   `csv.DictWriter(file, fieldnames, restval='', extrasaction='raise', dialect='excel', *args, **kwds)`.
2. **Dialect API:**
   `csv.list_dialects() -> List[Str]`,
   `csv.get_dialect(name) -> Dialect`,
   `csv.register_dialect(name, dialect=None, **fmtparams)`,
   `csv.unregister_dialect(name)`,
   `csv.field_size_limit(new_limit=None) -> Int`.
3. **`Dialect` / `excel` / `excel_tab` / `unix_dialect`** as POOP
   classes.
4. **`Sniffer`** class for auto-detecting dialect from a sample.
5. **Quoting constants:** `csv.QUOTE_ALL`, `QUOTE_MINIMAL`,
   `QUOTE_NONNUMERIC`, `QUOTE_NONE`, `QUOTE_STRINGS` (3.12+),
   `QUOTE_NOTNULL` (3.12+).
6. **`csv.Error`** — POOP error wrapper.

**Type discipline:** `Str` for fields, `List[Str]` for rows,
`Dict[Str, Str]` for `DictReader`/`DictWriter`.

## Expose `configparser` as POOP messages

Python's `configparser` parses INI-style config files.

**Proposal — `configparser` (lowercase module) + class set:**

1. **`ConfigParser` class** with `BasicInterpolation` /
   `ExtendedInterpolation` / `RawConfigParser` siblings:
   `ConfigParser(defaults=None, dict_type=dict, allow_no_value=False, *, delimiters=('=', ':'), comment_prefixes=('#', ';'), inline_comment_prefixes=None, strict=True, empty_lines_in_values=True, default_section='DEFAULT', interpolation=None, converters=None)`.
2. **Reading:** `.read(filenames, encoding=None)`,
   `.read_string(string, source='<string>')`,
   `.read_dict(dictionary, source='<dict>')`,
   `.read_file(f, source=None)`.
3. **Querying:** `.sections() -> List[Str]`,
   `.has_section(section) -> Boolean`,
   `.options(section) -> List[Str]`,
   `.has_option(section, option) -> Boolean`,
   `.items(section=...) -> List[Tuple[Str, Str]]`,
   `.get(section, option, *, raw=False, vars=None, fallback=...) -> Str`,
   `.getint`/`getfloat`/`getboolean` typed accessors,
   `.defaults() -> Dict`.
4. **Mutating:** `.add_section(section)`, `.remove_section(section)`,
   `.set(section, option, value)`, `.remove_option(section, option)`,
   `.clear()`, `.update(...)`.
5. **Writing:** `.write(fp, space_around_delimiters=True)`.
6. **Errors:** `Error`, `NoSectionError`, `DuplicateSectionError`,
   `NoOptionError`, `DuplicateOptionError`, `InterpolationError`
   subtree, `ParsingError`, `MissingSectionHeaderError`.

**Type discipline:** `Str` for sections/options/values; `Boolean`/
`Int`/`Float` for typed getters.

## Expose `hmac` as POOP messages

Python's `hmac` implements RFC 2104 keyed-hash message
authentication. Pairs naturally with `hashlib`.

**Proposal — `hmac` (lowercase module) + `HMAC` class:**

1. **Module-level shortcuts:**
   `hmac.new(key, msg=None, digestmod=hashlib.sha256) -> HMAC`,
   `hmac.digest(key, msg, digest) -> Bytes` (one-shot, constant-
   time-friendly),
   `hmac.compare_digest(a, b, /) -> Boolean` (delegate of
   `secrets.compare_digest`).
2. **`HMAC` class** mirroring `Hash` from `hashlib`:
   `.update(msg) -> NoneClass`, `.digest() -> Bytes`,
   `.hexdigest() -> Str`, `.copy() -> HMAC`,
   `.digest_size -> Int`, `.block_size -> Int`, `.name -> Str`.

**Type discipline:** `Bytes` for keys/messages/digests, `Str` for
hex, `Boolean` for `compare_digest`.

**Out of scope (for v1):** the legacy `digestmod=None` default
(deprecated in Python).

## Expose `os` as POOP messages

Python's `os` is huge — process management, environment, file
descriptors, file system ops not covered by `pathlib`. POOP splits
it into focused namespaces rather than one monolithic mirror.

**Proposal — four POOP namespaces (`os`, `system`, `process`,
`env`) drawn from `os`:**

1. **`os` (lowercase)** binds the four sub-namespaces and a small
   set of file-system numerics that `Path` doesn't cover:
   `os.urandom(n) -> Bytes`, `os.cpu_count() -> Int`,
   `os.process_cpu_count() -> Int`, `os.getloadavg() -> Tuple[Float]`,
   plus path-mode constants (`F_OK`, `R_OK`, `W_OK`, `X_OK`,
   `O_RDONLY`, `O_WRONLY`, `O_RDWR`, `O_APPEND`, `O_CREAT`, …)
   when those are needed for low-level FD ops.
2. **`system`** namespace for process-level state:
   `system.exit(code=0)`, `system.argv -> Tuple[Str]` (replaces
   `sys.argv`), `system.executable -> Path`, `system.platform -> Str`.
3. **`process`** namespace for current-process operations:
   `process.pid -> Int`, `process.ppid -> Int`,
   `process.uid` / `process.gid` / `process.euid` / `process.egid` /
   `process.umask(mask) -> Int`, `process.chdir(path)`,
   `process.getcwd() -> Path`, `process.kill(pid, signal)`.
4. **`env`** namespace for environment variables:
   `env.get(key, default=None) -> Str | NoneClass`,
   `env.set(key, value) -> NoneClass`, `env.unset(key)`,
   `env.has(key) -> Boolean`, `env.keys() -> Set[Str]`,
   iteration via `.do(block)`, `Dict`-like API.

**Type discipline:** `Path` for filesystem, `Str` for env values,
`Int` for IDs/file-descriptors.

**Out of scope (for v1):**

- The `os.path` family — fully covered by `Path`.
- `os.spawn*` / `os.exec*` / `os.fork()` — `subprocess` proposal
  covers process creation; raw fork/exec is unsafe by default.
- The low-level FD API (`os.open`/`read`/`write`/`close`) — use
  `Path.read_bytes`/`write_bytes` or future streaming I/O instead.

## Expose `io` as POOP messages

Python's `io` covers in-memory and stream I/O. Most file I/O lives
in `Path`; this proposal exposes only the in-memory and streaming
extras.

**Proposal — `io` (lowercase module) + class set:**

1. **In-memory:**
   `io.StringIO(initial_value='', newline='\n')` — text buffer,
   `io.BytesIO(initial_bytes=b'')` — binary buffer.
   Both expose `.read`, `.write`, `.getvalue`, `.seek`, `.tell`,
   `.truncate`, `.close`, `With` context-manager friendly.
2. **Stream bases** (for advanced users implementing custom
   streams): `io.IOBase`, `io.RawIOBase`, `io.BufferedIOBase`,
   `io.TextIOBase`.
3. **Constants:** `io.SEEK_SET`, `io.SEEK_CUR`, `io.SEEK_END`,
   `io.DEFAULT_BUFFER_SIZE`.
4. **Errors:** `io.UnsupportedOperation`, `io.BlockingIOError`.

**Type discipline:** `Str` for `StringIO`, `Bytes` for `BytesIO`,
`Int` for sizes/positions.

**Out of scope (for v1):**

- `io.open` — `Path.read_text` / `write_text` is the POOP idiom.
- `io.IncrementalNewlineDecoder` — niche.

## Expose `time` as POOP messages

Python's `time` is the wall-clock/monotonic clock API. Pairs with
`datetime` but lower-level.

**Proposal — `time` (lowercase module) namespace:**

1. **Clocks:**
   `time.time() -> Float` (wall-clock seconds since epoch),
   `time.time_ns() -> Int`,
   `time.monotonic() -> Float`,
   `time.monotonic_ns() -> Int`,
   `time.perf_counter() -> Float`,
   `time.perf_counter_ns() -> Int`,
   `time.process_time() -> Float`,
   `time.process_time_ns() -> Int`,
   `time.thread_time() -> Float`,
   `time.thread_time_ns() -> Int`.
2. **Sleep:** `time.sleep(seconds) -> NoneClass`.
3. **Formatting / parsing:**
   `time.strftime(format, time_tuple=None) -> Str`,
   `time.strptime(string, format) -> StructTime`,
   `time.gmtime(secs=None) -> StructTime`,
   `time.localtime(secs=None) -> StructTime`,
   `time.mktime(struct_time) -> Float`,
   `time.asctime(struct_time=None) -> Str`,
   `time.ctime(secs=None) -> Str`.
4. **`StructTime` class** wrapping `time.struct_time`: nine-attr
   record (`tm_year`, `tm_mon`, `tm_mday`, `tm_hour`, `tm_min`,
   `tm_sec`, `tm_wday`, `tm_yday`, `tm_isdst`, `tm_zone`,
   `tm_gmtoff`).
5. **Timezone info:** `time.tzname`, `time.timezone`,
   `time.altzone`, `time.daylight`, `time.tzset()`.

**Type discipline:** `Float`/`Int` for clocks/durations, `Str` for
formatted output, `StructTime` for structured time.

## Expose `logging` as POOP messages

Python's `logging` is the canonical logging framework: loggers,
handlers, formatters, filters, levels.

**Proposal — `logging` (lowercase module) + class set:**

1. **Module-level convenience:**
   `logging.debug(msg, *args, **kwargs)`,
   `logging.info(...)`, `logging.warning(...)`,
   `logging.error(...)`, `logging.critical(...)`,
   `logging.exception(...)`, `logging.log(level, msg, *args, **kwargs)`,
   `logging.getLogger(name=None) -> Logger`,
   `logging.basicConfig(**kwargs) -> NoneClass`.
2. **`Logger` class** — `.debug/info/warning/error/critical/log`,
   `.setLevel(level)`, `.isEnabledFor(level) -> Boolean`,
   `.addHandler(h)`, `.removeHandler(h)`, `.handlers -> List[Handler]`,
   `.propagate -> Boolean`, `.getEffectiveLevel() -> Int`.
3. **`Handler` class + subclasses:** `StreamHandler`, `FileHandler`,
   `NullHandler`. Methods `.setLevel`, `.setFormatter(f)`,
   `.addFilter`, `.removeFilter`, `.emit(record)`.
4. **`Formatter` class:** `Formatter(fmt=None, datefmt=None, style='%', validate=True, *, defaults=None)`,
   `.format(record) -> Str`.
5. **`LogRecord` class** — emitted message + context (name, level,
   pathname, lineno, msg, args, exc_info, …).
6. **Filter** class + `Logger.addFilter`.
7. **Level constants:** `CRITICAL=50`, `ERROR=40`, `WARNING=30`,
   `INFO=20`, `DEBUG=10`, `NOTSET=0`. Plus
   `logging.getLevelName(level) -> Str`,
   `logging.addLevelName(level, name)`.

**Type discipline:** all POOP types — `Str` for messages/levels,
`Int` for level integers, `Dict` for `extra`/`defaults`.

**Out of scope (for v1):**

- `logging.config` (file + dict-based configuration) — niche, fold
  into a follow-up.
- `logging.handlers` (rotating, SMTP, syslog, …) — separate
  proposal.

## Expose `getpass` as POOP messages

Python's `getpass` reads a password from the user without echoing,
plus a `getuser()` helper.

**Proposal — `getpass` (lowercase module) namespace:**

1. **Reads:** `getpass.getpass(prompt='Password: ', stream=None) -> Str`,
   `getpass.getuser() -> Str`.
2. **Errors:** `getpass.GetPassWarning` (when echo can't be
   suppressed).

**Type discipline:** `Str` for prompts/values/users.

## Expose `platform` as POOP messages

Python's `platform` returns information about the runtime
environment: OS, architecture, Python build.

**Proposal — `platform` (lowercase module) namespace, all functions
return POOP `Str` or POOP `Tuple`:**

1. **OS info:** `platform.system()`, `platform.release()`,
   `platform.version()`, `platform.machine()`, `platform.processor()`,
   `platform.platform(aliased=False, terse=False)`,
   `platform.node()`, `platform.uname() -> Uname`.
2. **Architecture:** `platform.architecture(executable=sys.executable, bits='', linkage='') -> Tuple[Str, Str]`.
3. **Python build:** `platform.python_version()`,
   `platform.python_version_tuple() -> Tuple[Str]`,
   `platform.python_branch()`, `platform.python_build() -> Tuple[Str, Str]`,
   `platform.python_compiler()`, `platform.python_implementation()`,
   `platform.python_revision()`.
4. **Per-OS specifics:** `platform.mac_ver()`, `platform.win32_ver()`,
   `platform.libc_ver()`.
5. **`Uname` class** — named record with `.system`, `.node`,
   `.release`, `.version`, `.machine`, `.processor`.

**Type discipline:** `Str` for textual fields, `Tuple` for
multi-value, named record for `Uname`.

**Out of scope (for v1):** the deprecated `dist()` / `linux_distribution()`.

## Expose `errno` as POOP messages

Python's `errno` is a tiny module: integer constants for OS error
codes (`EACCES`, `ENOENT`, …) plus `errorcode` reverse map.

**Proposal — `errno` (lowercase module) namespace:**

1. **Error code constants** as POOP `Int` (full set Python exposes:
   `EPERM`, `ENOENT`, `ESRCH`, `EINTR`, `EIO`, `ENXIO`, `E2BIG`,
   …, and the Windows + Unix-specific subsets where defined).
2. **`errno.errorcode`** — `Dict[Int, Str]` mapping code → name.

**Type discipline:** `Int` for codes, `Str` for names, `Dict` for
the reverse lookup.

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
- **Class-with-class-methods (`math`-style namespace global)** — when
  the operation parses, creates, or combines values (`Random new`,
  `Date today`, `NeoJSONReader fromString:`, `math.atan2`). In POOP
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
| `string` | proposed | See proposal above |
| `re` | proposed | See proposal above |
| `difflib` | proposed | See proposal above |
| `textwrap` | proposed | See proposal above |
| `unicodedata` | proposed | See proposal above |
| `stringprep` | out | Internal IDNA helper |
| `readline` | out | REPL infrastructure — POOP doesn't expose a REPL |
| `rlcompleter` | out | REPL infrastructure |

### Binary Data Services

| Module | Status | Sketch |
|---|---|---|
| `struct` | proposed | See proposal above |
| `codecs` | proposed | See proposal above |

### Data Types

| Module | Status | Sketch |
|---|---|---|
| `datetime` | proposed | See proposal above |
| `zoneinfo` | proposed | See proposal above |
| `calendar` | proposed | See proposal above |
| `collections` | covered | `OrderedDict` / `Counter` / `deque` redundant — POOP collections carry the methods |
| `heapq` | proposed | See proposal above |
| `bisect` | proposed | See proposal above |
| `array` | proposed | See proposal above |
| `weakref` | proposed | See proposal above |
| `types` | out | Introspection — forbidden in POOP |
| `copy` | proposed | See proposal above |
| `pprint` | proposed | See proposal above |
| `reprlib` | out | POOP forbids `repr` |
| `enum` | proposed | See proposal above |
| `graphlib` | proposed | See proposal above |

### Numeric and Mathematical Modules

| Module | Status | Sketch |
|---|---|---|
| `numbers` | out | ABC hierarchy — POOP has its own type tree |
| `math` | covered | `Math` namespace (shipped in v0.6.0) |
| `cmath` | audit | Needs `Complex` POOP type story — see "Future work" |
| `decimal` | proposed | See proposal above |
| `fractions` | proposed | See proposal above |
| `random` | covered | `Random` namespace (shipped in v0.7.0) |
| `statistics` | proposed | See proposal above |

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
| `filecmp` | proposed | See proposal above |
| `tempfile` | proposed | See proposal above |
| `glob` | proposed | See proposal above |
| `fnmatch` | proposed | See proposal above |
| `linecache` | out | Internal traceback helper |
| `shutil` | proposed | See proposal above |

### Data Persistence

| Module | Status | Sketch |
|---|---|---|
| `pickle` | proposed | See proposal above |
| `copyreg` | out | Internal hook for `pickle` |
| `shelve` | out | Depends on `dbm` |
| `marshal` | out | CPython internal |
| `dbm` | out | Niche; prefer `sqlite3` |
| `sqlite3` | proposed | See proposal above |

### Data Compression and Archiving

| Module | Status | Sketch |
|---|---|---|
| `zlib` | proposed | See proposal above |
| `gzip` | proposed | See proposal above |
| `bz2` | proposed | See proposal above |
| `lzma` | proposed | See proposal above |
| `zipfile` | proposed | See proposal above |
| `tarfile` | proposed | See proposal above |
| `compression` | proposed | See proposal above |

### File Formats

| Module | Status | Sketch |
|---|---|---|
| `csv` | proposed | See proposal above |
| `configparser` | proposed | See proposal above |
| `tomllib` | proposed | See proposal above |
| `netrc` | out | Niche legacy format |
| `plistlib` | out | macOS-specific niche |

### Cryptographic Services

| Module | Status | Sketch |
|---|---|---|
| `hashlib` | proposed | See proposal above |
| `hmac` | proposed | See proposal above |
| `secrets` | proposed | See proposal above |

### Generic Operating System Services

| Module | Status | Sketch |
|---|---|---|
| `os` | proposed | See proposal above |
| `io` | proposed | See proposal above |
| `time` | proposed | See proposal above |
| `logging` | proposed | See proposal above |
| `argparse` | out | POOP programs don't expose a CLI surface (yet) |
| `getpass` | proposed | See proposal above |
| `curses` | out | Terminal UI — niche |
| `platform` | proposed | See proposal above |
| `errno` | proposed | See proposal above |
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

### `Random.getstate()` / `Random.setstate(state)` — from the `random` proposal (v0.7.0)

Python's `random.Random.getstate()` returns a tuple of the form
`(version, internal_state, gauss_next)` where `internal_state` is a
**625-element tuple of ints** carrying the Mersenne Twister state.
POOP's type discipline forbids leaking raw Python primitives across
the namespace boundary, but wrapping every state int into a POOP
`Int` is pure overhead — nobody inspects the state; it exists only
to round-trip into `setstate`. The cleanest path requires either an
opaque-state POOP type that pickles/unpickles via Bytes, or a
sanctioned divergence allowing the raw tuple through (the user never
sees what's inside).

For v1, `.seed(a, version)` covers the 95% case of determinism. The
state pair is deferred until a concrete user need surfaces — at
which point the trade-off (opaque-Bytes type vs. raw-tuple
divergence) can be decided with real requirements in hand.

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

