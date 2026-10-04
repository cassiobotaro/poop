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

### 7. Ordering is written once; arithmetic is written 39 times

`_OrderedMixin` and `_NumericCompareMixin` each state their rule once and pass
the operator in: `return self._compare(other, operator.lt)`. The arithmetic
next to them was not given the same treatment:

```python
def __add__(self, other: object) -> Int | Float:
    from poop.types.float import Float

    if not isinstance(other, Int | Float):
        return NotImplemented
    if isinstance(other, Float):
        return Float(self._value + other._value)
    return Int(self._value + other._value)
```

`Int` repeats that body for `-`, `*`, `//` and `%` with one character changed,
then a four-line body ten times for `<<`, `>>`, `&`, `|`, `^` and their
reflections. `Float` has six identical bodies, `Complex` ten (five operators,
each forward and reflected), `_SetAlgebraMixin` eight. 39 methods in four
shapes.

In `Int`, each copy also runs `from poop.types.float import Float` on every
call: the `int ↔ float` cycle is paid once per operator rather than once.

**Fix.** One helper per shape, taking the operator from `operator`, with each
dunder a one-line call to it — exactly what `_OrderedMixin` does. The dunders
stay as named methods, so `cloak` and `ty` see what they see now.

---

### 8. `Map`, `Filter`, `Zip` and `Enumerate` each rebuild the same skeleton

Each of the four declares `_iter` and `_peeked`, defines a `_materialize` that
builds its generator on first use and drops the source, and then repeats

```python
def __iter__(self) -> Iterator[Any]:
    return self

def iter(self) -> Map:
    return self

def __str__(self) -> str:
    return "<map>"

__repr__ = __str__
```

and ends with `cloak(Map, "map")`. `Map` and `Filter` differ in two lines of
`_gen` and one string.

`_IteratorBase` already holds this for the concrete iterators: `__iter__`,
`iter`, the `<name>` repr, and the cloak, driven by a class keyword
(`class ListIterator(_IteratorBase[Object], name="list_iterator")`).

**Fix.** A `_LazyView` base beside `_IteratorBase` taking the same `name=`
keyword and owning `_materialize`'s build-once step; each view keeps its
`__init__` and its `_gen`.

---

### 9. The transformer base lags the validator base

`CollectingValidator` got three things that `BaseTransformer` did not.

- **One annotation.** `pyproject.toml` ignores `RUF012` because "the
  configuration ClassVars of a validator (`messages`, `forbidden`) are
  annotated once on the base class". The transformers re-annotate instead:
  `BINDINGS: ClassVar[dict[str, object]]` appears on all 26 subclasses, and 19
  modules import `ClassVar` for nothing else.
- **A default that is used.** `ReturnTransformer`, `VarargsTransformer` and
  `UnpackTransformer` each declare `BINDINGS = {}`, which the base already
  provides.
- **A check at import.** A validator that sets no `visitor` fails when its
  class is defined; a transformer that sets no `rewriter` fails on the first
  program. `rewriter` is also annotated as an instance attribute, where
  `visitor` is a `ClassVar`.

Two smaller things in the same package. `call_at` and `name_at` exist because
"every rewrite in this package replaces one node with a call to a binding, and
each spelt out `copy_location(Call(func=Name(...), ...), node)` by hand" —
`varargs.py`, `unpack.py` and `return_.py` still build theirs by hand. And
`varargs.py` states the `vararg → _poop_tuple_from`, `kwarg →
_poop_dict_from_kwargs` pairing twice, once for `def` and once for `lambda`.

**Fix.** Drop the 26 annotations and the three empty dicts, make `rewriter` a
`ClassVar` checked in `__init_subclass__`, and route the hand-built nodes
through `call_at` and `name_at`. The annotation half is trialled: 26 files
change, and ruff, `ty` and the suite all pass.

---

### 10. `poop.types` re-exports 19 names that nothing imports

`poop/types/__init__.py` imports 19 modules and lists 19 names in `__all__`.
Nothing uses them: there is no `from poop.types import …` anywhere in `poop/`
or `tests/` (two tests `import poop.types` only to walk the package). The
list is also not the package's surface — it has `Set` and `FrozenSet` and no
`List` or `Tuple`, `Slice` and no `MappingProxy`.

It is not free either. Importing any submodule runs the package `__init__`
first, so `import poop.types._selectors` — a module with no dependencies —
loads the whole type tree, in the order this file happens to list. That makes
the file a hidden input to every import cycle in the package.

**Fix.** Empty the file. Trialled: the suite passes, `poop.cli` imports, and
each of nine modules picked across the package (`int`, `block`, `_bridge`,
`exceptions`, `meta`, `_unwrap`, `string`, and the two pipeline packages)
imports cold on its own.

---

### 11. Three helpers that always raise are annotated `-> None`

`_refuse`, `_refuse_instance_side` and `_refuse_native` in `poop/types/meta.py`
end in an unconditional `raise` and are annotated `-> None`. Their twins in
`exceptions.py` (`_refuse_python_attribute`, `refuse`) say `-> Never`, and so
does `PoopMeta.raise_`, a few lines from the three.

The difference is visible to a reader and to the tools. `PoopMeta.mro` returns
a value on one branch and calls `_refuse_native` on the other, so it looks like
it can fall off the end and answer `None`; ruff's `RET503` reports exactly
that.

**Fix.** `-> Never` on the three. Trialled: `ty`, ruff and the suite pass, and
`RET503` goes quiet without a `noqa`.

---

### 12. 80 annotation-only imports are imported at runtime

`CONTRIBUTING.md`: "Imports needed exclusively for type annotations go inside
an `if TYPE_CHECKING:` block at the top of the module — never function-local,
never alongside runtime imports." Ruff's `TC` rules check that, and they are
not in `select`. Over `poop/` they report 80: 65 standard-library imports
(mostly `collections.abc.Callable` and `Iterator`), 11 first-party, 1
third-party and 3 `cast` targets.

Trialled with `ruff check --select TC --fix --unsafe-fixes`. One import must
stay: `poop/cli.py`'s `Path`, because typer reads `main`'s annotations at
runtime — moving it fails 19 tests in `tests/test_cli.py` with `NameError:
name 'Path' is not defined`. With that file exempt the suite and `ty` pass;
the 56 import blocks the move unsorts are fixed by `ruff check --fix`.

**Fix.** Add `TC` to `select`, apply the fix, and exempt `poop/cli.py` with
the reason stated, as the other per-file ignores are. This is what the closed
item about `PLC0415` did for the other half of the same paragraph.

---

### 13. Comments and docs that describe a language POOP no longer is

Each of these states something the code next to it contradicts.

- **`RaiseTransformer`** does not exist; `raise_` became a class-side message.
  It is still named as a live ordering constraint in `CONTRIBUTING.md`
  ("Registration order … is sometimes load-bearing (`ExceptionTransformer`
  after `RaiseTransformer`)"), in `varargs.py` ("has to run after … 
  `RaiseTransformer`, whose `_poop_raise(Exc, **kw)` this then covers") and in
  `ObjectTransformer`'s docstring.
- **`math`** is not a namespace binding; the namespace is `Try` and `With`.
  `no_namespace_shadow.py` explains its parameter check with `def m(self,
  math)` and `lambda math: math.sqrt(2)`.
- **Nested `def`s.** `no_namespace_shadow.py`: "nested defs are legal POOP
  (no_free_functions allows them inside a method)". `no_free_functions`
  refuses them, and says so in its own comment.
- **"lowercase stdlib mirrors"** in `_registry.py`'s comment on
  `_BINDING_SOURCES`, for `Try` and `With`, which are neither.
- **`ObjectTransformer`'s docstring**: "`ClassTransformer` already rewrites
  both in a base list". `ClassTransformer`'s own comment says the opposite:
  "Only the implicit base is this rewriter's".
- **`async`** is listed in `CONTRIBUTING.md` as something
  `examples/idiomatic/` teaches. `no_async` bans it and no example uses it.

**Fix.** Rewrite each to say what is true today. The `CONTRIBUTING.md`
example needs a real ordering constraint to cite; `_registry.py` names one
("SliceTransformer relies on NoneTransformer having run").

---

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
