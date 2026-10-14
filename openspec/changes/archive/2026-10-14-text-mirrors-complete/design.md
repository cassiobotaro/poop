# Design

## Context

See proposal.md - Why. What the approach rests on, verified on the current
tree and interpreter:

- `Str.format(*args, **kwargs)` already runs CPython's template engine with
  `to_python` on every argument, guards field access with
  `_reject_field_access`, and rewords the `KeyError` (`the template asks for
  'a', which no argument named...`) and `IndexError`. `format_map` is the same
  engine with one mapping argument.
- A POOP `Dict` holds `Int` keys, and `_num_value` refuses raw Python numbers
  by design, so `Int(97) != 97`. CPython's `str.translate` looks ordinals up
  as raw ints; a POOP table must therefore cross to Python (`to_python`,
  `_bridge.py`) before the native method sees it.
- `_BytesLikeMixin` holds the 51 messages `bytes` and `bytearray` answer
  alike, each concrete class supplying `_rewrap`; `fromhex` is per class
  because the answer's type differs. `maketrans` answers `bytes` on both
  (CPython), `translate` answers the receiver's kind.
- Guards in `_argument.py` word every argument refusal once per kind; none
  exists yet for "a mapping" or "a mapping or a sequence". `bytes_like`
  exists and already words `#<selector>` refusals for byte arguments.
- CPython's sentences for the value-level failures (`the first two maketrans
  arguments must have equal length`, `string keys in translatetable must be
  of length 1`, `translation table must be 256 characters long`, `maketrans
  arguments must have same length`, `character mapping must return integer,
  None or str`) name no banned construct; its type-level ones do (`'int'
  object is not subscriptable`, `a bytes-like object is required, not 'str'`,
  `if you give only one argument to maketrans it must be a dict`).
- `str.maketrans` and `bytes.maketrans` are static methods in CPython;
  `PoopMeta` already resolves `classmethod` and `staticmethod` on the class
  side (`float.fromhex`, `int.from_bytes`).

## Goals / Non-Goals

**Goals:**
- `Str`, `Bytes` and `ByteArray` answer every public method their builtin has.
- Every type-level refusal reads as POOP; every value-level one keeps
  CPython's sentence, by the rule `take_bytes` and `resize` already follow.
- The two declined surfaces are written down where the next audit will look.

**Non-Goals:**
- `MemoryView.tolist` / `readonly`, and the rest of the buffer attributes.
- `ExceptionGroup` and `except*`.
- Rewording `format`'s existing refusals, or widening what `format_map`
  accepts beyond POOP's mappings.

## Decisions

**1. `format_map` reuses `format`'s machinery through a shared private
helper.** The guard, the `to_python` crossing and the two rewordings are
factored out of `format` into a helper both call; `format_map` differs only in
taking one mapping and passing `to_python(mapping)` as the keyword source. A
positional field (`{0}`) in a `format_map` template keeps CPython's `Format
string contains positional fields`, which names nothing POOP forbids.
*Alternative*: implement `format_map` as `self.format(**to_python(mapping))`.
Rejected: a mapping with non-string keys would fail inside `**` with
CPython's wording, and the dependency on the spread is the thing the message
exists to avoid.

**2. Two new guards: `a_mapping` and `translation_table`.** `a_mapping(value,
selector)` admits `Dict`, `FrozenDict` and `MappingProxy` (the `_MappingMixin`
family) and refuses with `#<selector> expects a mapping, got an int`; it serves
`format_map` and the one-argument `maketrans`. `translation_table(value,
selector)` admits a mapping or a sequence (`List`, `Tuple`, `Str`) for
`Str.translate`, since CPython indexes a sequence by ordinal too, and refuses
with `#translate expects a mapping or a sequence, got an int`. Both answer the
`to_python` crossing so the caller hands CPython natives.
*Alternative*: `isinstance` checks inline. Rejected: the sweep found 47 leaks
precisely where refusals were written per receiver.

**3. `maketrans` is a `staticmethod` on `Str` and on `_BytesLikeMixin`.**
CPython's is static; the class side resolves it as it does `classmethod`, and
an instance may send it too (`"".maketrans(...)` works in Python). The text
form takes one to three arguments and answers a `Dict` built with `to_poop` on
CPython's result; the byte form takes two byte-like arguments through
`bytes_like` and answers a `Bytes` on both classes, as CPython does, so it
lives on the mixin rather than per class. Unequal lengths and multi-character
keys keep CPython's `ValueError`.

**4. `translate` on the mixin, answering through `_rewrap`.** `table` is
`none` or `bytes_like`; `delete` is `bytes_like` with `b""` as default. The
256-byte check stays CPython's. On `Str`, `translate` answers `Str` of the
native result.

**5. The two declined surfaces get one paragraph each in `INFECTIONS.md`.**
Under MemoryView: POOP has only one-dimensional byte views (no `struct`, no
`array`), so `shape`, `strides`, `itemsize`, `format`, `ndim`, `cast`,
`toreadonly`, `release`, `obj` and the contiguity flags would answer constants
in a vocabulary the catalogue already keeps out; `tolist` and `readonly` are
named as the two with content, left for their own change. Under the exception
budget: `ExceptionGroup` stays out because nothing in the language produces a
group and `except*` is refused, with Smalltalk's `ExceptionSet` noted as the
*catching* construct the `except_` tuple already is.

## Risks / Trade-offs

- [The wording sweep surfaces a CPython sentence from the new messages this
  design did not list] → routed through the guard it belongs to before the
  commit; the sweep runs in the ordinary test run.
- [`to_python` on a user-defined mapping-like class] → POOP programs cannot
  define `__getitem__` (dunder definitions are banned), so the only mappings
  are the three wrappers; the guard names exactly those.
- [`Str.translate` with a `Str` table indexes characters by ordinal, which
  reads oddly] → it is CPython's behavior for a sequence table and costs
  nothing to mirror; the spec scenario uses a mapping, the common case.
