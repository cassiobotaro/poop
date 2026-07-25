import builtins
from builtins import print as _builtins_print
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Self

from poop.types.meta import PoopMeta

if TYPE_CHECKING:
    from poop.types.boolean import Boolean
    from poop.types.int import Int
    from poop.types.list import List
    from poop.types.none import NoneClass
    from poop.types.string import Str


class MessageNotUnderstood(AttributeError):
    """Smalltalk's answer to an unknown selector.

    Inherits `AttributeError` on purpose, ironic as that is for the error that
    exists to stop speaking Python: `hasattr` and three-argument `getattr`
    swallow that and nothing else. A plainer base would break `Object.has_attr`
    and `get_attr(name, default)` — POOP's own sanctioned substitute for the
    banned `getattr` — turning a question into a crash.
    """


class Object(metaclass=PoopMeta):
    __slots__ = ()

    def class_(self) -> Any:
        """Smalltalk's `x class` — the class object itself, not its name."""
        return type(self)

    if not TYPE_CHECKING:
        # Hidden from the type checker deliberately. A visible __getattr__
        # answers Any for every name, so `xs.frobnicate()` would type-check on
        # every POOP object and `ty` would stop catching typos across the whole
        # codebase. Statically an unknown message is still an error; this hook
        # changes what happens when one is sent, not what is knowable before.
        def __getattr__(self, name: str) -> Any:
            # Dunders never reach the hook. Python probes objects for
            # `__copy__`, `__getstate__`, `__deepcopy__` and friends, and a
            # proxy overriding does_not_understand would answer those probes
            # as if a user had sent them — the classic proxy bug.
            if name.startswith("__") and name.endswith("__"):
                raise AttributeError(name)
            return self.does_not_understand(name)

    def does_not_understand(self, name: str) -> Any:
        """Smalltalk's `doesNotUnderstand:` — the hook for an unknown message.

        Override to answer the message rather than refuse it. A proxy answers a
        callable, which is also the only way to reach the arguments: attribute
        lookup runs before the call, so nothing here has seen them yet.
        """
        from poop.types._selectors import explain

        raise MessageNotUnderstood(explain(self, name), name=name, obj=self)

    def if_none(self, block: Callable[[], Any]) -> Object:
        return self

    def if_not_none[T](self, block: Callable[[Object], T]) -> T:
        return block(self)

    def is_none(self) -> Boolean:
        from poop.types.boolean import false

        return false

    def not_none(self) -> Boolean:
        from poop.types.boolean import true

        return true

    def is_identical(self, other: Object) -> Boolean:
        from poop.types.boolean import to_boolean

        return to_boolean(self is other)

    def not_identical(self, other: Object) -> Boolean:
        from poop.types.boolean import false, true

        return false if self is other else true

    def not_(self) -> Boolean:
        from poop.types.boolean import false, true

        return false if bool(self) else true

    def assert_(self, message: Str | NoneClass | None = None) -> Self:
        from poop.types._unwrap import _faithful, _is_absent

        if bool(self):
            return self
        if _is_absent(message):
            raise AssertionError
        # `assert x, msg` takes any object as the message in CPython, so an
        # unwrappable one goes through raw rather than leaking #_value.
        raise AssertionError(_faithful(message))

    def class_name(self) -> Str:
        # `x class name` in Smalltalk: the name is the class's to answer, not
        # a fact the instance knows about itself.
        return self.class_().name()

    def hash(self) -> Int:
        from poop.types.int import Int

        return Int(hash(self))

    def id(self) -> Int:
        from poop.types.int import Int

        return Int(id(self))

    def callable(self) -> Boolean:
        from poop.types.boolean import to_boolean

        return to_boolean(builtins.callable(self))

    def is_instance(self, type_: type) -> Boolean:
        from poop.types.boolean import to_boolean

        return to_boolean(isinstance(self, type_))

    @classmethod
    def is_subclass(cls, other: type) -> Boolean:
        from poop.types.boolean import to_boolean

        return to_boolean(issubclass(cls, other))

    def repr(self) -> Str:
        from poop.types.string import Str

        return Str(builtins.repr(self))

    def ascii(self) -> Str:
        from poop.types.string import Str

        return Str(builtins.ascii(self))

    def dir(self) -> List:
        from poop.types.list import List
        from poop.types.string import Str

        # Filter every `_`-prefixed name — dunders (banned by
        # no_dunder_attribute) and privates, including the mangled `_poop_*`
        # bindings — so the introspection substitute never surfaces what the
        # encapsulation rules hide. Same predicate as the REPL's `:methods`.
        return List(
            *(Str(name) for name in builtins.dir(self) if not name.startswith("_"))
        )

    def format(self, spec: Str | NoneClass | None = None) -> Str:
        from poop.types._unwrap import _unwrap
        from poop.types.string import Str

        spec_value = _unwrap(spec, "")
        target = builtins.getattr(self, "_value", self)
        return Str(builtins.format(target, spec_value))

    def _reject_dunder(self, name: str) -> None:
        """The runtime half of `no_dunder_attribute`.

        `no_getattr` bans `getattr` and offers these four as the substitute, so
        without this `get_attr("__dict__")` reopens exactly what the validator
        closes. A computed name — `"__dict" + "__"` — puts that spelling beyond
        any static validator's reach, which is why the guard has to live here.
        """
        from poop.validators.no_dunder_attribute import dunder_message

        message = dunder_message(name)
        if message is not None:
            raise AttributeError(message.lstrip("."))

    def _reject_private(self, name: str) -> None:
        """POOP encapsulation: refuse `_`-prefixed private names.

        `get_attr("_value")` would hand back the raw Python primitive a POOP
        object wraps — a naked native in user code — and `_items`/`_data`/`_fn`
        expose the same internals; the mangled `_poop_*` bindings hide here too.
        A computed name — `"_val" + "ue"` — is invisible to any static
        validator, so the guard lives at runtime. Dunders are handled by
        `_reject_dunder`; this covers the single-underscore convention Python
        honours only by etiquette.
        """
        is_dunder = name.startswith("__") and name.endswith("__")
        if name.startswith("_") and not is_dunder:
            raise AttributeError(
                f"{name} is private — POOP objects do not expose their internals"
            )

    def _checked_name(self, name: Str) -> str:
        """The raw name behind `name`, both bans applied.

        Every accessor needs the same three steps, and `_attr_name` is what
        keeps a non-`Str` name from leaking `#_value` out of the substitute
        `no_getattr` points at.
        """
        from poop.types._unwrap import _attr_name

        raw = _attr_name(name)
        self._reject_dunder(raw)
        self._reject_private(raw)
        return raw

    def get_attr(self, name: Str, *default: Any) -> Any:
        # Guarded before the default is consulted: a forbidden name is refused,
        # not quietly answered with a fallback.
        return builtins.getattr(self, self._checked_name(name), *default)

    def has_attr(self, symbol: Str) -> Boolean:
        from poop.types.boolean import to_boolean

        return to_boolean(hasattr(self, self._checked_name(symbol)))

    def set_attr(self, name: Str, value: Any) -> NoneClass:
        from poop.types.none import none

        builtins.setattr(self, self._checked_name(name), value)
        return none

    def del_attr(self, name: Str) -> NoneClass:
        from poop.types.none import none

        builtins.delattr(self, self._checked_name(name))
        return none

    def print(
        self,
        end: Str | NoneClass | None = None,
        flush: Boolean | NoneClass | None = None,
    ) -> NoneClass:
        from poop.types._unwrap import _unwrap, _unwrap_bool
        from poop.types.none import none

        end_value = _unwrap(end, "\n")
        flush_value = _unwrap_bool(flush, False)
        _builtins_print(str(self), end=end_value, flush=flush_value)  # noqa: T201
        return none

    def __str__(self) -> str:
        return f"<{self.class_name()}>"

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other: object) -> Boolean:
        from poop.types.boolean import to_boolean

        return to_boolean(self is other)

    def __ne__(self, other: object) -> Boolean:
        from poop.types.boolean import false, true

        return false if self is other else true

    def __hash__(self) -> int:
        return id(self)


Object.__module__ = "builtins"
Object.__name__ = "object"
