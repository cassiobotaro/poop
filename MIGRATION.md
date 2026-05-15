# Migration Recipes — Python → POOP

Quick translations of common Python idioms to POOP source code. For the full reference of which Python constructs are forbidden and why, see [`INFECTIONS.md`](INFECTIONS.md). For end-to-end programs, see [`examples/`](examples).

> Every snippet pair shows the Python form you would normally write and the POOP form the validators and transformers force you to write instead. Snippets are valid as POOP source — primitive literals like `0`, `"hi"`, `True` are wrapped to POOP types by transformers at parse time, so methods like `.at(0)` and `.print()` work directly on Python literals without any manual wrapping.

## Control flow

### `if` / `else`

```python
# Python
result = handle_admin() if user.is_admin() else handle_guest()
```

```python
# POOP
result = user.is_admin().if_true_if_false(
    lambda: handle_admin(),
    lambda: handle_guest(),
)
```

### Single-branch `if`

```python
# Python
if balance < 0:
    raise ValueError("overdraft")
```

```python
# POOP
(balance < 0).if_true(lambda: ValueError.raise_("overdraft"))
```

### `and` / `or` / `not`

```python
# Python
ok = is_admin and not is_locked or is_owner
```

```python
# POOP
ok = is_admin.and_(lambda: is_locked.not_()).or_(lambda: is_owner)
```

> The `lambda:` wrappers preserve short-circuit semantics — branches are only evaluated if reached.

## Iteration

### `for` loop

```python
# Python
for item in items:
    process(item)
```

```python
# POOP
items.do(lambda item: process(item))
```

### List / set / dict comprehension

```python
# Python
result = [x * 2 for x in xs if x > 0]
```

```python
# POOP
result = list(xs.filter(lambda x: x > 0).map(lambda x: x * 2))
```

> `map` and `filter` return lazy iterators. Materialize with `list(...)`, `tuple(...)`, `set(...)`, `bytes(...)`.

### `range` loop

```python
# Python
for i in range(1, 11):
    print(i)
```

```python
# POOP
range(1, 11).do(lambda i: i.print())
```

### `enumerate` / `zip`

```python
# Python
for i, name in enumerate(names):
    ...
for a, b in zip(xs, ys):
    ...
```

```python
# POOP
names.enumerate().do(lambda pair: ...)   # pair.at(0) is index, pair.at(1) is value
xs.zip(ys).do(lambda pair: ...)
```

## Free functions on objects

```python
# Python
n = len(xs)
y = abs(x)
print(x)
text = repr(x)
ok = isinstance(x, MyClass)
total = sum(xs)
biggest = max(xs)
```

```python
# POOP
n = xs.len()
y = x.abs()
x.print()
text = x.repr()
ok = x.is_instance(MyClass)
total = xs.sum()
biggest = xs.max()
```

> Same pattern for `getattr`/`setattr`/`hasattr`/`dir`/`format`/`hash`/`id`/`callable`/`ascii` → `x.get_attr(name)`, `x.set_attr(name, val)`, `x.has_attr(name)`, `x.dir()`, `x.format(spec)`, `x.hash()`, `x.id()`, `x.callable()`, `x.ascii()`.

## Operators that look procedural

```python
# Python
y = -x
y = ~x
q, r = divmod(a, b)
y = round(x, 2)
```

```python
# POOP
y = x.negated()
y = x.bit_invert()
q, r = a.divmod(b)
y = x.round(2)
```

> Binary operators (`+`, `-`, `*`, `/`, `**`, `==`, `<`, …) stay native — the asymmetry is intentional, see `INFECTIONS.md` § "Binary infix operators".

## Subscripting and slicing

```python
# Python
first = xs[0]
window = xs[1:4]
```

```python
# POOP
first = xs.at(0)
window = xs.slice(1, 4)
```

> For reuse across collections, build a value with `slice(start, stop, step=None)` — the transformer rewrites the lowercase builtin into POOP's `Slice`. Pass it to `xs.slice(s)` on any sequence type.

## Membership

```python
# Python
3 in xs
"foo" in s
"key" in d
```

```python
# POOP
xs.includes(3)
s.includes("foo")
d.includes("key")
```

> `d.includes(k)` mirrors Python's `key in d` — checks keys. The views also respond to `.includes(...)` for the other axes: `d.keys().includes(k)`, `d.values().includes(v)`, `d.items().includes((k, v))`.

## Raise / try / except

```python
# Python
try:
    risky()
except ValueError as e:
    handle(e)
```

```python
# POOP
Try(lambda: risky()).except_(ValueError, lambda e: handle(e)).run()
```

> Inside lambdas you cannot `raise` — write `ExcType.raise_("msg")`. The `RaiseTransformer` rewrites it to a callable so it composes inside blocks.

## Context managers (`with`)

```python
# Python
with lock:
    critical_section()
```

```python
# POOP
With(lambda: lock).do(lambda _: critical_section())
```

> `With` takes a *factory lambda*, not the cm directly — entry is deferred until `do()` runs.

## File I/O (`open`)

```python
# Python
with open("data.txt") as f:
    text = f.read()
open("out.txt", "w").write(text.upper())
```

```python
# POOP
text = Path("data.txt").read_text()
Path("out.txt").write_text(text.upper())
```

> `open()` is a definitive ban. `Path` covers `read_text` / `write_text` / `read_bytes` / `write_bytes` plus the rest of `pathlib`. There is no `Path.open(mode)` yet — file handles aren't exposed.

## Math (`math` module)

```python
# Python
import math

r = math.sqrt(x)
a = math.pi * r * r
ok = math.isclose(a, b)
h = math.hypot(3, 4, 12)
n = math.factorial(5)
```

```python
# POOP
r = math.sqrt(x)
a = math.pi * r * r
ok = math.isclose(a, b)
h = math.hypot(3, 4, 12)
n = math.factorial(5)
```

> `math` mirrors Python's `math` module exactly — same name (lowercase), same function names, parameter order, defaults, kw-only markers, return types. No `import math` needed in POOP — the namespace is injected globally.

## Random (`random` module + `Random` class)

```python
# Python
import random

x = random.random()
n = random.randint(1, 10)
pick = random.choice(xs)
random.shuffle(xs)
sample = random.sample(xs, 3)
r = random.Random(42)
```

```python
# POOP
x = random.random()
n = random.randint(1, 10)
pick = random.choice(xs)
random.shuffle(xs)
sample = random.sample(xs, 3)
r = Random(42)
```

> POOP exposes both `random` (lowercase, module-level singleton — `random.random()`, `random.choice(xs)`, …) and `Random` (PascalCase, the class — `Random(seed)` returns a fresh independently-seeded instance). The split mirrors Python exactly; the only shortcut is that `Random` is in scope without a `random.` prefix (no `import` needed). Cryptographic draws live in `secrets`, never `random`.

## OS error codes (`errno` module)

```python
# Python
import errno

if exc.errno == errno.ENOENT:
    handle_missing()
name = errno.errorcode[exc.errno]
```

```python
# POOP
exc.errno.equals(errno.ENOENT).if_true(lambda: handle_missing())
name = errno.errorcode.at(exc.errno)
```

> Every public integer constant in `errno.*` is reachable as `errno.<NAME>` (POOP `Int`). The reverse map `errno.errorcode` is a POOP `Dict[Int, Str]` — use `.at(code)` to look up a name.

## Password prompts (`getpass` module)

```python
# Python
import getpass

user = getpass.getuser()
pwd = getpass.getpass("Password: ")
```

```python
# POOP
user = getpass.getuser()
pwd = getpass.getpass("Password: ")
```

> Both `getpass.getuser()` and `getpass.getpass(prompt)` return POOP `Str`. `getpass.GetPassWarning` is not exposed in POOP — the underlying CPython call still emits it to stderr, but POOP has no warning model to catch it.

## Cryptographic randomness (`secrets` module)

```python
# Python
import secrets

token = secrets.token_hex(16)
n = secrets.randbelow(100)
ok = secrets.compare_digest(a, b)
```

```python
# POOP
token = secrets.token_hex(16)
n = secrets.randbelow(100)
ok = secrets.compare_digest(a, b)
```

> Anything cryptographic goes through `secrets`, not `random`. `secrets.token_bytes` returns `Bytes`; `token_hex`/`token_urlsafe` return `Str`. `secrets.compare_digest(a, b, /)` is constant-time and accepts either `Str` or `Bytes` — but both arguments must be the same type, exactly like CPython.

## Base64 (`base64` module)

```python
# Python
import base64

encoded = base64.b64encode(b"hello world")
decoded = base64.b64decode(encoded)
url_safe = base64.urlsafe_b64encode(b"\xfb\xff")
from_str = base64.b64decode("YWJj")
```

```python
# POOP
encoded = b"hello world".b64encode()
decoded = encoded.b64decode()
url_safe = b"\xfb\xff".urlsafe_b64encode()
from_str = "YWJj".b64decode()
```

> All `base64.*` functions are methods on the value. `Bytes` carries both encode and decode (9 variants each: b16/b32/b32hex/b64/standard_b64/urlsafe_b64/a85/b85/z85). `Str` carries decoders only (the encoders never accept `str` input in CPython either). Encoders return `Bytes` — call `.decode(Str("ascii"))` if you want a textual `Str`.

## Binary↔ASCII conversions and CRC (`binascii` module)

```python
# Python
import binascii

hex_bytes = binascii.b2a_hex(b"\xde\xad\xbe\xef")
raw = binascii.a2b_hex(hex_bytes)
checksum = binascii.crc32(b"hello")

try:
    binascii.a2b_hex(b"zz")
except binascii.Error as e:
    handle(e)
```

```python
# POOP
hex_bytes = binascii.b2a_hex(b"\xde\xad\xbe\xef")
raw = binascii.a2b_hex(hex_bytes)
checksum = binascii.crc32(b"hello")

Try(lambda: binascii.a2b_hex(b"zz")).except_(
    binascii.Error, lambda e: handle(e)
).run()
```

> `binascii.Error` and `binascii.Incomplete` are exposed as raw Python exception classes so user code can pass them to `Try.except_(...)`. The hex pair `b2a_hex`/`hexlify` are aliases, as are `a2b_hex`/`unhexlify`.

## MIME type lookups (`mimetypes` module + `MimeTypes` class)

```python
# Python
import mimetypes

mime, encoding = mimetypes.guess_type("page.html")
ext = mimetypes.guess_extension("text/html")
mimetypes.add_type("application/x-custom", ".custom")

# Isolated registry
registry = mimetypes.MimeTypes(filenames=["/etc/mime.types"])
```

```python
# POOP
mime, encoding = mimetypes.guess_type("page.html")
ext = mimetypes.guess_extension("text/html")
mimetypes.add_type("application/x-custom", ".custom")

# Isolated registry — Python: random.Random(seed) → POOP: Random(seed). Same idea here.
registry = MimeTypes(filenames=["/etc/mime.types"])
```

> POOP exposes both `mimetypes` (lowercase, module-level API + constant maps) and `MimeTypes` (the class — `MimeTypes(filenames=List, strict=Boolean)`). The split mirrors Python exactly. `mimetypes.suffix_map`/`encodings_map`/`types_map`/`common_types`/`knownfiles` are snapshotted from CPython's globals at import time and don't reflect later `add_type` mutations.

## Opening URLs (`webbrowser` module + `Browser` class)

```python
# Python
import webbrowser

webbrowser.open("https://example.com")
webbrowser.open_new_tab("https://example.com")
firefox = webbrowser.get("firefox")
firefox.open_new("https://example.com")
```

```python
# POOP
webbrowser.open("https://example.com")
webbrowser.open_new_tab("https://example.com")
firefox = webbrowser.get("firefox")
firefox.open_new("https://example.com")
```

> POOP exposes both `webbrowser` (lowercase, module-level API) and `Browser` (the controller wrapper, returned by `webbrowser.get(using=none)`). `webbrowser.Error` is a raw Python exception class for use with `Try.except_(...)`. `webbrowser.register(...)` is deferred to Future work — its `constructor` argument is a Python callable with no clean POOP mapping.

## Shell-style wildcard expansion (`glob` module)

```python
# Python
import glob

files = glob.glob("src/**/*.py", recursive=True)
for f in glob.iglob("*.txt"):
    process(f)
```

```python
# POOP
files = glob.glob("src/**/*.py", recursive=true)
glob.iglob("*.txt").do(lambda f: process(f))
```

> `glob.glob` returns `List[Path]`; `glob.iglob` returns `GlobIter` (iterable, with `.to_list()`). `Path.glob`/`Path.rglob` already cover most use; the namespace surfaces the module-level entry points for callers who want to glob from a string pattern without first constructing a `Path`.

## Pattern matching on filenames (`fnmatch` module)

```python
# Python
import fnmatch

if fnmatch.fnmatch(name, "*.py"):
    handle_python(name)
selected = fnmatch.filter(all_names, "test_*.py")
regex_src = fnmatch.translate("*.py")
```

```python
# POOP
fnmatch.fnmatch(name, "*.py").if_true(lambda: handle_python(name))
selected = fnmatch.filter(all_names, "test_*.py")
regex_src = fnmatch.translate("*.py")
```

> `fnmatch.fnmatch` follows the OS's case-sensitivity rules; `fnmatch.fnmatchcase` is always case-sensitive. `filter` returns `List[Str]`; `translate` returns a regex source `Str` for downstream compilation.

## Shallow / deep copy (`copy` module)

```python
# Python
import copy

shallow = copy.copy(obj)
deep = copy.deepcopy(obj)
```

```python
# POOP
shallow = copy.copy(obj)
deep = copy.deepcopy(obj)
```

> POOP types implement Python's `__copy__` / `__deepcopy__` protocol; the namespace routes calls. `copy.Error` is exposed as a Python exception class for use with `Try.except_(...)`. `deepcopy`'s `memo` parameter is not surfaced — implement `__deepcopy__` on your POOP class if you need custom memoization.

## Pretty-printing (`pprint` module + `PrettyPrinter` class)

```python
# Python
import pprint

pprint.pprint(data)
text = pprint.pformat(data, width=40)
printer = pprint.PrettyPrinter(indent=4)
```

```python
# POOP
pprint.pprint(data)
text = pprint.pformat(data, width=40)
printer = PrettyPrinter(indent=4)
```

> POOP types alias `__repr__` to `__str__`, so pretty-printed output reads exactly like POOP's regular `.print()`. `pprint.pp` differs from `pprint.pprint` only in defaulting `sort_dicts=false`. `PrettyPrinter` captures `sys.stdout` at construction time — to capture pretty-printed output, build the printer inside a stream redirect.

## Binary search and ordered insertion (`bisect` module)

```python
# Python
import bisect

idx = bisect.bisect_left(sorted_xs, target)
bisect.insort(sorted_xs, new_value)
```

```python
# POOP
idx = bisect.bisect_left(sorted_xs, target)
bisect.insort(sorted_xs, new_value)
```

> `bisect`/`insort` are aliases for `bisect_right`/`insort_right`, matching CPython. Index queries return POOP `Int`; insertion mutators return `none` and mutate the `List` in place. `key` is a Python callable.

## Heap queue (`heapq` module)

```python
# Python
import heapq

heapq.heappush(heap, item)
smallest = heapq.heappop(heap)
top3 = heapq.nlargest(3, data)
sorted_merge = list(heapq.merge(*iterables))
```

```python
# POOP
heapq.heappush(heap, item)
smallest = heapq.heappop(heap)
top3 = heapq.nlargest(3, data)
sorted_merge = heapq.merge(*iterables).to_list()
```

> `heapq` operates on POOP `List` in place — `heappush`/`heappop`/`heapify` are mutators that return `none` (`heappop` returns the popped element). `heapq.merge` returns a `HeapMerge` lazy iterator with `.to_list()` to materialize.

## Shell tokenization (`shlex` module + `Shlex` class)

```python
# Python
import shlex

args = shlex.split('echo "hello world"')
cmd = shlex.join(args)
safe = shlex.quote(user_input)

lexer = shlex.shlex(text)
for token in lexer:
    handle(token)
```

```python
# POOP
args = shlex.split('echo "hello world"')
cmd = shlex.join(args)
safe = shlex.quote(user_input)

lexer = Shlex(text)
lexer.do(lambda token: handle(token))
```

> `shlex.split` returns `List[Str]`. The `Shlex` class is the streaming lexer (mirrors `shlex.shlex`); v0.23.0 ships the common iterative surface (`.get_token()`, iteration, `.lineno`, `.whitespace_split`). Deeper lexer configuration (character classes, push sources, etc.) is deferred to Future work.

## UUIDs (`uuid` module + `UUID` class)

```python
# Python
import uuid

new_id = uuid.uuid4()
parsed = uuid.UUID("12345678-1234-5678-1234-567812345678")
name_id = uuid.uuid5(uuid.NAMESPACE_URL, "https://example.com")
hex_form = new_id.hex
```

```python
# POOP
new_id = uuid.uuid4()
parsed = UUID("12345678-1234-5678-1234-567812345678")
name_id = uuid.uuid5(uuid.NAMESPACE_URL, "https://example.com")
hex_form = new_id.hex
```

> `UUID` is in scope without a `uuid.` prefix (same pattern as `Random`). All seven generators (`uuid1`/`3`/`4`/`5`/`6`/`7`/`8`) plus `uuid.getnode()` and the standard constants (`NAMESPACE_DNS`/`URL`/`OID`/`X500`, `NIL`, `MAX`, four `RESERVED_*`/`RFC_4122` variant tokens) are surfaced. `is_safe` flattens CPython's `SafeUUID` enum to a lowercase `Str` token (sanctioned divergence).

## JSON (`json` module)

```python
# Python
import json

text = json.dumps({"name": "alice", "ages": [10, 20]})
obj = json.loads(text)
json.dump(obj, open("data.json", "w"))
loaded = json.load(open("data.json"))
```

```python
# POOP
text = json.dumps({"name": "alice", "ages": [10, 20]})
obj = json.loads(text)
json.dump(obj, Path("data.json"))
loaded = json.load(Path("data.json"))
```

> POOP's `json` is path-based — `dump`/`load` accept a `Path` instead of a file object (no `open` in POOP). The round-trip preserves POOP types: `json.loads(s)` returns a POOP value graph (`Dict`/`List`/`Str`/`Int`/`Float`/`Boolean`/`none`), and `json.dumps` accepts the same graph back. `json.JSONDecodeError` is exposed as a Python exception class for use with `Try.except_(...)`. Custom encoders/decoders and callback kwargs (`object_hook`, `default`, …) are deferred to Future work.

## TOML (`tomllib` module)

```python
# Python
import tomllib

cfg = tomllib.loads(text)
with open("pyproject.toml", "rb") as f:
    pyproject = tomllib.load(f)
```

```python
# POOP
cfg = tomllib.loads(text)
pyproject = tomllib.load(Path("pyproject.toml"))
```

> POOP's `tomllib.load` accepts a `Path` (POOP has no file-object abstraction). Round-trip returns POOP types — TOML date / time / datetime values currently flatten to ISO-8601 `Str` until the `datetime` proposal lands. `tomllib.TOMLDecodeError` is a Python exception class for use with `Try.except_(...)`. Write support stays out of scope (`tomllib` is read-only upstream).

## HMAC (`hmac` module + `HMAC` class)

```python
# Python
import hmac

mac = hmac.new(key, msg, digestmod="sha256")
hex_signature = mac.hexdigest()
ok = hmac.compare_digest(received, expected)
one_shot = hmac.digest(key, msg, "sha256")
```

```python
# POOP
mac = hmac.new(key, msg, "sha256")
hex_signature = mac.hexdigest()
ok = hmac.compare_digest(received, expected)
one_shot = hmac.digest(key, msg, "sha256")
```

> `digestmod` accepts a `Str` hash name (`"sha256"`, `"sha512"`, …) since `hashlib` is still proposed — CPython's `hmac.new` already supports the string form. When `hashlib` ships, the type widens.

## Topological sort (`graphlib` module + `TopologicalSorter` class)

```python
# Python
from graphlib import TopologicalSorter

sorter = TopologicalSorter({"b": ["a"], "c": ["b"]})
order = list(sorter.static_order())
```

```python
# POOP
sorter = TopologicalSorter({"b": ["a"], "c": ["b"]})
order = sorter.static_order()
```

> `TopologicalSorter` is in scope without a `graphlib.` prefix (same pattern as `Random`, `UUID`). `static_order()` returns a `Tuple`; the incremental `.add` / `.prepare` / `.get_ready` / `.done` surface is also exposed for streaming consumption. `graphlib.CycleError` is a Python exception class for use with `Try.except_(...)`.
