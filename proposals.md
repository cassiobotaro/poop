# Proposals

Open design backlog. Closing convention: see [`CONTRIBUTING.md`](CONTRIBUTING.md#closing-a-proposal).

---

### 1. `get_attr` on a method name answers a raw Python callable

**Severity: medium (Python leak).**

`get_attr` guards *which* names may be read — `_attr_name` for the name itself,
then the dunder and private bans — but nothing guards what comes back. When the
attribute is a method, the answer is CPython's own bound method, a naked native
in user code:

```bash
printf 'm = "abc".get_attr("upper")\nm.print()\n' | poop /dev/stdin
# -> AttributeError: 'function' object has no attribute 'print'
```

It is callable (`m()` answers `Str("ABC")`, correctly), so the leak is not that
the value is broken — it is that the value understands no messages at all. The
failure is also Python's own `AttributeError`, not `does not understand #print`,
which is exactly the seam the wrappers exist to hide. Every other accessor is
clean: state answers a POOP object, `has_attr` a `Boolean`, `set_attr` /
`del_attr` `none`. The class side has the same hole (`Foo.get_attr("speak")`
answers the unbound function).

This is the last member of the `getattr`-substitute family still handing back a
native, and `no_getattr` points users straight at it.

**Solution.** POOP already has the type for a first-class callable — `Block`,
which every `lambda` is transparently wrapped in, and which even cloaks itself
as `function` for `class_name()`. Wrap on the way out, in both `Object.get_attr`
(`poop/types/object.py:208`) and `PoopMeta.get_attr` (`poop/types/meta.py:310`):

```python
def _as_poop(value: Any) -> Any:
    """A raw Python callable answered by `get_attr`, as a POOP `Block`.

    An attribute that holds state already answers a POOP object; one that
    holds a *method* answered CPython's bound method, which understands no
    message — `m.print()` raised Python's own AttributeError. `Block` is the
    type a lambda is already wrapped in, so a method reads back as the same
    kind of object a block literal does. A POOP class is left alone: it is
    callable, but it is already an object with its own protocol.
    """
    if callable(value) and not isinstance(value, (Object, type)):
        return Block(value)
    return value
```

Verified on a patched build: `"abc".get_attr("upper")` then answers a `Block`
that still calls (`m()` → `Str("ABC")`), prints as `<block>`, and answers
`class_name()` → `Str("function")`; a state attribute, a `default` fallback and
a POOP class all pass through untouched; and the class side works the same way,
the unbound function taking its receiver explicitly (`Foo.get_attr("speak")(d)`).

Tests under `tests/test_types/test_object.py` and `test_meta.py` (a method reads
back as a Block, still calls, and answers `print`; state is untouched), plus an
`INFECTIONS.md` note in the `Block` section — a method fetched by name is a
block, which is also what makes `get_attr` composable with the block-taking
messages.

**The alternative, if the wrap is unwanted:** refuse a callable attribute
outright — `get_attr("upper")` answering "send the message instead: `x.upper()`"
— on the grounds that reaching for a method by name is what `does_not_understand`
and polymorphism replace. That trades a leak for a smaller surface rather than a
larger one, and would make POOP's `get_attr` narrower than CPython's `getattr`;
the wrap keeps the substitute honest to the builtin it replaces. Worth deciding
before implementing, since the two answers are not compatible.
