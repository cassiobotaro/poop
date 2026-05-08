# Improvement Proposals

Prioritized list of improvements verified against the code, with real `file:line` references. Categories: **bug**, **open decision**.

Guiding principle (`INFECTIONS.md:16`): *"Activate validator only when the substitute exists — blocking without offering an alternative only breaks code without teaching anything."*

---

## Open decisions — revisit "intentional"

Items currently classified as "no possible substitute" (`INFECTIONS.md:299-345`) but worth reassessing.

### 1. `open(path)` → POOP `Path` type inspired by `pathlib`?

**Today:** `INFECTIONS.md` declares "file I/O — no POOP equivalent".

**Important observation:** the stdlib's `pathlib` is already **object-oriented** — `Path("foo.txt").read_text()`, `Path("dir").iterdir()`, `Path("a").exists()`. The API matches POOP's message-passing model naturally, sparing us a "from-scratch subsystem".

**Possible models:**
- **(a) Wrapper around `pathlib.Path`** — a POOP `Path` wraps `pathlib.Path` and exposes methods like `read_text() -> Str`, `read_lines() -> List[Str]`, `write_text(content: Str) -> Path`, `exists() -> Boolean`, `iterdir() -> List[Path]`. Cheaper, leverages tested pathlib.
- **(b) `Str.open(mode)` returning a POOP `File`** — alternative originally proposed, closer to the builtin `open()` but requires designing the lifecycle from scratch (`close`, context manager via `With`).

**Recommendation:** (a). Pathlib has already done the work of "OO-ifying" filesystem I/O; POOP inherits it almost for free. For `open()` itself, `Path("foo").read_text()` / `write_text()` covers most uses without exposing open file handles.

**Suggested location:** `poop/types/path.py` (new) plus a namespace-only transformer at `poop/transformers/path.py` (no AST rewrite, just BINDINGS injection).

**Scope:** smaller than reimplementing I/O from scratch — wrapper over `pathlib` plus delegating methods.

**Decision:** adopt approach (a) with `pathlib` as the foundation, design `File` from scratch, or keep banned?

#### Implementation plan (assuming approach (a))

Exposure follows the **namespace-only** pattern of `With` / `Try` (see CLAUDE.md "Architecture"): the type contributes `BINDINGS` to `DEFAULT_NAMESPACE` but is **not** registered in `DEFAULT_TRANSFORMERS` because nothing is rewritten. One new public name (`Path`) appears in the user namespace. No literal syntax, no lowercase shadow.

**Files to add/touch:**

1. `poop/types/path.py` — new `Path(Object)` class. `__slots__ = ("_path",)` wrapping a `pathlib.Path`.
2. `poop/transformers/path.py` — new, mirrors `with_.py`:
   ```python
   class PathTransformer(BaseTransformer):
       BINDINGS: ClassVar[dict[str, object]] = {"Path": Path}
   ```
3. `poop/transformers/__init__.py` — import `PathTransformer`, splice `**PathTransformer.BINDINGS` into `DEFAULT_NAMESPACE`. **Not** added to `DEFAULT_TRANSFORMERS`.
4. `poop/validators/no_open.py` — keep `open` banned, update message: `"open() is forbidden — use Path('foo').read_text() / write_text() instead"`.
5. `INFECTIONS.md` — move `open()` out of "no POOP equivalent" into a new "Active infections" entry documenting `Path`.
6. `CLAUDE.md` — add `path.py` to the types list and the transformers list (note "namespace-only" alongside `try_`/`with_`).
7. `tests/test_types/test_path.py` — new.

**`Path` constructor (idempotent, mirroring the recent ctor cleanup):**

```python
def __init__(self, path: Str | Path) -> None:
    if isinstance(path, Path):
        self._path = path._path
    else:
        self._path = _pathlib.Path(path._value)
```

User writes `Path("foo.txt")`. The str transformer has already turned `"foo.txt"` into `Str("foo.txt")` by the time the ctor runs, so it always sees a POOP type. `Path(Path(x))` collapses to `Path(x)` — same idempotency contract as `Str`/`Int`/`Float`/etc.

**Internal helper for navigation methods** (avoids re-parsing the path string):

```python
@classmethod
def _from_pathlib(cls, p: _pathlib.Path) -> Path:
    obj = cls.__new__(cls)
    obj._path = p
    return obj
```

**API surface (minimum viable cut):**

| pathlib method | POOP signature | Notes |
|---|---|---|
| `read_text(encoding=None)` | `read_text() -> Str` | encoding param omitted v1; default UTF-8 |
| `write_text(content)` | `write_text(content: Str) -> Int` | returns bytes written |
| `read_bytes()` | `read_bytes() -> Bytes` | |
| `write_bytes(data)` | `write_bytes(data: Bytes) -> Int` | |
| `exists()`/`is_file()`/`is_dir()`/`is_symlink()`/`is_absolute()` | `-> Boolean` | direct delegation |
| `mkdir(...)`/`rmdir()`/`unlink()`/`touch()` | `-> NoneClass` | return `none` |
| `resolve()`/`absolute()`/`rename(target)`/`replace(target)` | `-> Path` | use `_from_pathlib` |
| `joinpath(*others)`/`with_name(n)`/`with_suffix(s)`/`with_stem(s)`/`relative_to(other)` | `-> Path` | use `_from_pathlib` |
| `as_posix()`/`as_uri()` | `-> Str` | |
| `iterdir()`/`glob(pattern)`/`rglob(pattern)` | `-> List[Path]` | **eager**, consistent with current `.map()` semantics. Becomes `PathIterator` if the lazy-map proposal lands. |
| `Path.cwd()`/`Path.home()` | classmethods `-> Path` | |
| **Properties** (mirror pathlib): `name`/`stem`/`suffix` | `-> Str` | `@property` |
| **Properties**: `parts` | `-> Tuple[Str]` | |
| **Properties**: `parent` | `-> Path` | |
| **Properties**: `parents` | `-> Tuple[Path]` | |
| `__truediv__(other: Str \| Path)` | `-> Path` | enables `Path("dir") / "file.txt"` (`"file.txt"` is rewritten to `Str` by str transformer, so `__truediv__` gets `Str`; accepts `Path` too) |
| `__eq__`/`__hash__`/`__lt__`/`__le__`/`__gt__`/`__ge__` | mirror `pathlib` | enables `is_instance(Path)` chaining and sorting |

**Out of scope for v1 (filed as follow-ups if demand appears):**

- `Path.open(mode)` — would require a new `File` POOP type with `__enter__`/`__exit__` integrating with the existing `With`. Most uses are covered by `read_text`/`write_text`/`read_bytes`/`write_bytes`.
- `stat()` / `lstat()` — would require a `StatResult` POOP type exposing `size()`/`mode()`/`mtime()`. Niche.
- `owner()` / `group()` — Unix-only, niche.
- Datetime conversion of `mtime` etc. — would warrant a `DateTime` POOP type, which is a project of its own (timezone, formatting, arithmetic).

**Risks / open questions:**

- **Properties vs methods:** pathlib uses `@property` for `name`/`stem`/`suffix`/`parts`/`parent`/`parents`. POOP precedent is mixed (`Float.real` is `@property`, most things are methods). Plan: mirror pathlib literally — Python users reading the docs already expect properties. Same call site (`p.name` not `p.name()`).
- **Encoding in `read_text`/`write_text`:** v1 uses default UTF-8. If users need other encodings, follow-up adds `encoding: Str | None = None`.
- **`PurePath` hierarchy:** pathlib has `PurePath`/`PurePosixPath`/`PureWindowsPath` as the parent class hierarchy. POOP collapses to a single `Path` (concrete, OS-aware). Loses platform-specific path manipulation; gains simplicity. Acceptable for a pet project.
- **`iterdir`/`glob` eager vs lazy:** tied to the lazy-map decision below. If lazy wins, `iterdir` returns `PathIterator`. If eager stays, `List[Path]` is the right answer.

