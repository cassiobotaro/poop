# Proposals

Open design backlog. Closing convention: see [`CONTRIBUTING.md`](CONTRIBUTING.md#closing-a-proposal).

*Empty — nothing open.*

---

### ~~1. The exception mirrors and `Ellipsis` can be shadowed silently~~ — DONE

**Decision + implemented.** `no_builtin_shadow` reserved the 17 lowercase
builtins and both spellings of the root, and not the 16 `MIRRORS` names
`ExceptionTransformer` rewrites the same way, nor `Ellipsis`. Both sides of the
hazard its own docstring describes for `dict` were live: an assignment target
*is* an `ast.Name`, so `ValueError = 5` clobbered the mirror globally, while a
parameter (`ast.arg`) and a class name (`ClassDef.name`) are not — they kept
their spelling while every read of them in the body still resolved to the
mirror, so `def hold(self, ValueError): return ValueError` answered the class
and never saw its argument. `Ellipsis` was the sharpest, being the named
spelling of a *literal*: after `Ellipsis = 5`, `...` itself answered `5`.

The mirror half of the reserved set is derived from `MIRRORS` rather than
tabulated, for the reason `no_namespace_shadow` reads `DEFAULT_NAMESPACE` — a
seventeenth mirror cannot be added without the reservation following it. The
legal neighbours still run: `ValueError.raise_(…)`, `class MyErr(ValueError)`,
and a method named after a mirror (which binds as a class attribute).
`poop/validators/no_builtin_shadow.py`,
`tests/test_validators/test_no_builtin_shadow.py`, `INFECTIONS.md`.

---

### ~~2. The class side lets a program rewrite POOP's own builtin classes~~ — DONE

**Decision + implemented.** `__slots__` keeps state off the instance side and
`Object.set_attr` has a sentence for that refusal; the class side had no
equivalent, and `class_()` hands the class out — so
`"abc".class_().del_attr("upper")` removed `upper` from every string in the
program, and `(5).class_().set_attr("bit_length", block)` replaced a message on
`int`. The only names that happened to be safe were the `class_side`
descriptors, whose `__set__` refuses.

A new `_reject_builtin(cls)` in `poop/types/meta.py` refuses a write to a class
the program did not define, keyed on `__module__`: `cloak` puts every wrapper
and mirror in `builtins`, while a class a POOP program defines carries
`__poop__`. It cannot be forged — `__module__` is a dunder, so
`no_dunder_attribute` refuses the literal spelling and `_reject_dunder` the
computed one. The name is checked *before* the receiver, so a forbidden name
still answers the ban it broke. `tests/test_types/test_meta.py`, `INFECTIONS.md`.

---

### ~~3. `Object.del_attr` has no refusal of its own~~ — DONE

**Decision + implemented.** `set_attr` caught CPython's `AttributeError` and
composed POOP's sentence; `del_attr`, three lines below in the same
four-message family, did not — so `"abc".del_attr("zzz")` answered `'str'
object has no attribute 'zzz' and no __dict__ for setting new attributes`,
naming the dunder `_reject_dunder` will not even let a program spell.

Two branches rather than one, because the two failures are different facts: an
object that *can* hold state simply does not hold this name (`C has no
attribute 'b' to remove`), and telling a user class it "holds no state of its
own" would be false. `set_attr` needs only one, since a receiver with a
`__dict__` never fails there. Both programs joined `_FAILING`.
`poop/types/object.py`, `tests/test_types/test_object.py`,
`tests/test_no_python_wording.py`.

---

### ~~4. `Str.format` cannot apply a format spec to a `Complex`~~ — DONE

**Decision + implemented.** `_bridge.to_python` unwrapped every scalar rung
except `Complex`, so a complex reached `str.format` still wrapped and any real
spec hit `object.__format__`: `"{:.2f}".format(complex(1, 2))` failed where
CPython answers `1.00+2.00j`, and named `complex.__format__` on the way out.
`Complex` joined the scalar branch, and `to_poop` grew the mirror branch — the
two halves are documented as a pair, and a one-sided bridge is the next
reader's trap. `poop/types/_bridge.py`, `tests/test_types/test_bridge.py`.

---

### ~~5. `has_next` leaks CPython's `dictionary changed size during iteration`~~ — DONE

**Decision + implemented.** `next` and `__next__` reworded the mutation
refusal and `has_next` — the one message of the three that exists so a program
can *ask* instead of raising — read straight from CPython. It carries the same
`reword_if_native` guard now, and POOP's own `RuntimeError`s still pass through
untouched. The program joined `_FAILING`, which is what would have caught it:
the sweep was opt-in *by program* and none exercised `has_next`.
`poop/types/_peek.py`, `tests/test_types/test_peek.py`,
`tests/test_no_python_wording.py`.

---

### ~~6. `Str.rfind` / `Str.rindex` do not guard the needle~~ — DONE

**Decision + implemented.** `_needle` was wired into `find`, `index` and
`count` and not into their `r`-prefixed twins, which are the same message read
from the other end — so `"abc".find(block)` and `"abc".rfind(block)`, the same
mistake one letter apart, answered in two different vocabularies. Both route
through `_needle` now, and `_needle` itself grew the non-block case (item 10's
`find() argument 1 must be str, not int`). `poop/types/string.py`,
`tests/test_types/test_str.py`, `tests/test_no_python_wording.py`.

---

### ~~7. `Boolean` refuses every non-empty format spec~~ — DONE

**Decision + implemented.** A `Boolean` has no `_value` slot, so
`Object.format` fell through to `object.__format__`, which accepts only the
empty spec — `True.format(">6")` refused while `"{:>6}".format(True)`, routed
through `to_python`, answered `'     1'`. The override folds to the Python
`bool`, **not** through `_as_int`: `format(True, "")` is `'True'` and
`format(1, "")` is `'1'`, so folding first would have changed
`True.format()` — the one spelling that already worked. `poop/types/boolean.py`,
`tests/test_types/test_boolean.py`.

---

### ~~8. `pow`'s modulus is refused in two different vocabularies~~ — DONE

**Decision + implemented.** Two commits' worth of one concern. `Int.__pow__`
composed POOP's sentence for two of the three ways a modulus can be wrong and
left the third to CPython's `pow() 3rd argument cannot be 0` — the builtin
`no_pow` forbids, spelt as the call. And `Float.pow` had no `modulus`
parameter at all, so `(2.0).pow(3, 5)` answered CPython's *signature* error
while `(2).pow(3.0, 5)` one line away answered the operation.

`Float.pow` grew the third slot and refuses it as an operation, reusing `Int`'s
wording so the tower answers one thing; the guard lives in `pow`, not
`__pow__`, because the operator never carries a third operand. `Boolean.pow`
picked both up for free through `_as_int`. `poop/types/int.py`,
`poop/types/float.py`, `tests/test_types/test_int.py`,
`tests/test_types/test_float.py`, `tests/test_no_python_wording.py`.

---

### ~~9. An aliased constructor is a different constructor~~ — DONE

**Decision + implemented.** Every converter transformer has two rewrites —
`visit_Call` to the converter, `visit_Name` to the wrapper *class* — and the
two mean different things. `_arity.py` closed exactly that gap for the direct
call; binding the name first reopened it one indirection away, and mostly in
silence: `x = list; x([1, 2])` answered `[[1, 2]]`, `x = tuple; x([1, 2])`
answered `([1, 2],)`, and `x = int; x(4.9)` answered an `int` **holding 4.9**,
which then said `float does not understand #+ with an int`.

The metaclass-dispatch shape the proposal recommended needed one refinement:
the wrapper classes cannot dispatch, because `poop/types/` builds its values by
calling them directly and that is the other meaning. So each bare name binds a
`_poop_<name>_cls` **alias** instead (`poop/types/_alias.py`) — a subclass of
the wrapper whose metaclass answers a *call* with the converter, guarded on
`cls.__dict__` so `class Stack(list)` still constructs a `Stack`. It stays a
class because that is what a bare name is otherwise for:
`(5).is_instance(int)`, `class Stack(list)`, `int.name()`.

One thing worth recording, because it looks like the obvious move: an
`__instancecheck__` delegating to the wrapped class — the shape `PoopExcMeta`
uses for the mirrors — cannot work here. The alias *is* a subclass, so
`ABCMeta`'s subclass walk reaches it and asks the same question, recursing
until the stack gives out. The type-argument case is answered one level up
instead, by `unalias`, which both `is_instance`/`is_subclass` pairs call.
`slice` needs no alias: it has no converter, and `Slice(start, stop, step)`
already *is* the call.

All 17 aliased constructors now answer what their direct spelling answers, and
the mechanical test the proposal asked for pins every row.
`poop/types/_alias.py`, 16 transformer modules, `poop/types/object.py`,
`poop/types/meta.py`, `tests/test_transformers/test_type_names.py`,
`INFECTIONS.md`.

---

### ~~10. The wording sweep is opt-in by program, and 47 leaks are hiding behind that~~ — DONE

**Decision + implemented.** The structural half first: a third half of
`tests/test_no_python_wording.py` now sends every public message on every
wrapper with wrong-typed arguments and runs `_FORBIDDEN` over what comes back,
with CPython's wrong-arity shape exempt (`_cloak`'s docstring says out loud
that it only renames the callee). It reported 83 leaks on the tree as it stood
— more than the 47 the proposal measured, because the proposal had already
folded some into items 3, 6 and 7.

All of them are closed. The refusals live in a new `poop/types/_argument.py` —
`a_class`, `a_bound`, `text_like`, `byte_order` — one guard per argument
*kind* rather than one per receiver, which is what makes the same sentence read
the same on `Str`, `Bytes` and `ByteArray`:

- `isinstance() arg 2 must be a type` from `x.is_instance(…)` — the banned
  builtin spelt as the call replacing it, on all 15 receivers at once.
- `slice indices must be integers or None or have an __index__ method` from the
  `start`/`end` of `find`/`rfind`/`index`/`rindex`/`count`/`startswith`/
  `endswith` on the three text wrappers, plus `list`/`tuple`'s `index`.
- Both halves of `Object.format`: a non-`Str` spec (`format() argument 2 must
  be str`) and a receiver with no `_value` (`unsupported format string passed
  to list.__format__`).
- The `<msg>() argument N must be …` family across a dozen text arguments, the
  `to_bytes`/`from_bytes` byteorder, `fromhex`, `hex`'s separator, and
  `ByteArray.at_put`'s index.

Two behaviour changes fell out and are deliberate: `hex(<not text>)` is now a
`TypeError` rather than the `ValueError` CPython reaches by measuring the
length of a non-separator, and `byte_order` splits the two failures the way
CPython classes them — a non-string is a `TypeError` about the argument's kind,
a misspelt one a `ValueError` about its value. `poop/types/_argument.py`,
`poop/types/{object,meta,boolean,string,bytes,byte_array,int,list,tuple}.py`,
`tests/test_no_python_wording.py`, `INFECTIONS.md`.

---

### ~~11. Three counts in the docs have drifted past the code~~ — DONE

**Decision + implemented.** `CLAUDE.md` said 69 validators, `README.md` said
~69 and 41 example programs, against 70 and 43. All three corrected — and
because every one of them is derivable, a new `tests/test_doc_counts.py` reads
the numbers *out of the Markdown* and compares them against the live
registries. A test asserting `len(DEFAULT_VALIDATORS) == 70` would only have
moved the problem to a fourth place to keep in step; this makes the drift
unrepresentable, and it also pins the README's bullet list against the files on
disk — the list was right while the sentence above it was two behind, which is
what made the drift invisible to a reader skimming either one. `CLAUDE.md`,
`README.md`, `tests/test_doc_counts.py`.
