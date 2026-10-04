"""The reflective accessors' guard, shared by instances and classes.

`get_attr` / `has_attr` / `set_attr` / `del_attr` live on `Object` and again,
class-side, on `PoopMeta`, and both refuse the same names for the same reasons.
Each side used to carry its own copy of the guard, and the copies drifted: the
class side kept the `__init__` carve-out the instance side had closed.

Imported at the top of `object.py` and `meta.py`, which sit under everything
else in `poop.types` — so this module imports nothing from the package at load
time. `MIRRORS` is built on `Object`, `_unwrap` imports `MIRRORS`, and the
validators package builds `DEFAULT_VALIDATORS` at import, which reaches
`poop.transformers` and from there back into `poop.types`; each is read inside
the function that needs it.
"""

from poop.types._selectors import is_dunder


def _reject_dunder(name: str) -> None:
    """The runtime half of `no_dunder_attribute`, for instances and classes.

    `no_getattr` bans `getattr` and offers `get_attr` / `has_attr` /
    `set_attr` / `del_attr` as the substitute, so without this
    `get_attr("__dict__")` reopens exactly what the validator closes. A
    computed name — `"__dict" + "__"` — puts that spelling beyond any static
    validator's reach, which is why the guard has to live here.

    `allow_init=False`: the validator's `__init__` carve-out exists for
    `super().__init__(...)`, a *syntax*, and these messages are not it. With
    the exemption inherited, `get_attr("__init__")` answered a callable that
    re-initialized the receiver in place — `Str`, `Int` and `Tuple` all
    mutable, and a `Dict` keyed on one left holding an entry reachable under
    neither the old spelling nor the new. The class side kept its own copy of
    this guard and the exemption with it, so `str.get_attr("__init__")(s, "x")`
    did exactly that until both receivers shared this one.
    """
    # circular: exceptions -> meta -> _attr_guard
    from poop.types.exceptions import MIRRORS  # noqa: PLC0415

    # circular: no_dunder_attribute -> types -> object -> _attr_guard
    from poop.validators.no_dunder_attribute import dunder_message  # noqa: PLC0415

    message = dunder_message(name, allow_init=False)
    if message is not None:
        raise MIRRORS["AttributeError"](message.lstrip("."))


def _reject_private(name: str) -> None:
    """POOP encapsulation: refuse `_`-prefixed private names.

    `get_attr("_value")` would hand back the raw Python primitive a POOP
    object wraps — a naked native in user code — and `_items`/`_data`/`_fn`
    expose the same internals; the mangled `_poop_*` bindings hide here too.
    A computed name — `"_val" + "ue"` — is invisible to any static
    validator, so the guard lives at runtime. Dunders are handled by
    `_reject_dunder`; this covers the single-underscore convention Python
    honours only by etiquette.
    """
    # circular: exceptions -> meta -> _attr_guard
    from poop.types.exceptions import MIRRORS  # noqa: PLC0415

    if name.startswith("_") and not is_dunder(name):
        raise MIRRORS["AttributeError"](
            f"{name} is private — POOP objects do not expose their internals"
        )


def _checked_name(name: object) -> str:
    """The raw name behind `name`, both bans applied.

    Every reflective accessor — on an instance and on a class — needs the same
    three steps, and `_attr_name` is what keeps a non-`Str` name from leaking
    `#_value` out of the substitute `no_getattr` points at. One copy, because
    two had already drifted apart (see `_reject_dunder`).
    """
    # circular: _unwrap -> boolean -> object -> _attr_guard
    from poop.types._unwrap import _attr_name  # noqa: PLC0415

    raw = _attr_name(name)
    _reject_dunder(raw)
    _reject_private(raw)
    return raw
