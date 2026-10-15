import builtins
from typing import TYPE_CHECKING, Any, Self

from poop.types._attr_guard import _checked_name
from poop.types._cloak import cloak
from poop.types._message import cannot_be_hashed, holds_no_state, no_format_spec
from poop.types._raw import _faithful
from poop.types._selectors import explain, is_dunder, is_message
from poop.types._sentinel import MISSING
from poop.types.meta import PoopMeta

# circular: every module below imports `Object` (or `PoopMeta`, which this
# module imports eagerly) at class-definition time, so none can be imported
# eagerly here. A lazy import resolves on first use, inside a method body,
# when both sides exist; after that the name is a plain global.
lazy from poop.types import mirrors
lazy from poop.types._alias import unalias
lazy from poop.types._argument import a_block, a_class, text_like
lazy from poop.types._unwrap import _is_absent, _unwrap, _unwrap_bool
lazy from poop.types.block import _as_block
lazy from poop.types.boolean import false, to_boolean, true
lazy from poop.types.int import Int
lazy from poop.types.list import List
lazy from poop.types.none import none
lazy from poop.types.string import Str, _template_refusal

if TYPE_CHECKING:
    from collections.abc import Callable

    from poop.types.boolean import Boolean
    from poop.types.none import NoneClass


class MessageNotUnderstood(AttributeError):
    """Smalltalk's answer to an unknown selector.

    Inherits `AttributeError` on purpose, ironic as that is for the error that
    exists to stop speaking Python: `hasattr` and three-argument `getattr`
    swallow that and nothing else. A plainer base would break `Object.has_attr`
    and `get_attr(name, default)` — POOP's own sanctioned substitute for the
    banned `getattr` — turning a question into a crash.
    """


def _holds_no_state(receiver: object) -> Exception:
    """The refusal for attaching state to a value, for `set_attr` and `del_attr`.

    The plain assignment (`"abc".x = 5`) answers the same sentence through
    `poop_message`, which rewords the native `no __dict__` report where the
    executor and `Error.message()` read; a `__setattr__` on `Object` used to
    do it and ran on every object construction in the language.
    """
    return mirrors.AttributeError(holds_no_state(type(receiver).__name__))


class Object(metaclass=PoopMeta):
    __slots__ = ()

    def __init_subclass__(cls, *, name: str | None = None, **kwargs: object) -> None:
        """Cloak a wrapper under the builtin name it answers to.

        The cloak is part of a class's declaration — the name it answers to —
        so it is a class keyword: `class Int(_NumericCompareMixin, Object,
        name="int")`. It used to be a statement after the class, 43 times,
        which is also 43 chances to define a wrapper and forget the line. A
        class a program defines passes no keyword and keeps its own name.
        `cloak` stays a function for the classes built by hand —
        `builtin_alias` and the exception mirrors.
        """
        super().__init_subclass__(**kwargs)
        if name is not None:
            cloak(cls, name)

    def class_(self) -> type[Self]:
        """Smalltalk's `x class` — the class object itself, not its name."""
        return type(self)

    if not TYPE_CHECKING:
        # Hidden from the type checker deliberately. A visible __getattr__
        # answers Any for every name, so `xs.frobnicate()` would type-check on
        # every POOP object and `ty` would stop catching typos across the whole
        # codebase. Statically an unknown message is still an error; this hook
        # changes what happens when one is sent, not what is knowable before.
        def __getattr__(self, name: str) -> Any:  # noqa: ANN401 — hidden from ty, see above
            # Dunders never reach the hook. Python probes objects for
            # `__copy__`, `__getstate__`, `__deepcopy__` and friends, and a
            # proxy overriding does_not_understand would answer those probes
            # as if a user had sent them — the classic proxy bug.
            #
            # The native class stays here, against the MIRRORS rule: this is
            # Python's attribute protocol answering Python's own probe, never
            # a diagnostic a program reads. It also runs while `exceptions` is
            # still importing — the mirrors are built on `Object` — so the
            # table it would consult may not hold this name yet.
            if is_dunder(name):
                raise AttributeError(name)
            # A `Str`, not the raw name CPython handed over: the hook is the
            # one documented place a program receives a selector, and a hook
            # that answered the name it was asked answered `'str' object has
            # no attribute 'print'` — a native from the sanctioned override.
            return self.does_not_understand(Str(name))

    def does_not_understand(self, name: Str) -> object:
        """Smalltalk's `doesNotUnderstand:` — the hook for an unknown message.

        Override to answer the message rather than refuse it. A proxy answers a
        callable, which is also the only way to reach the arguments: attribute
        lookup runs before the call, so nothing here has seen them yet.
        """
        raw = str(name)
        raise MessageNotUnderstood(explain(self, raw), name=raw, obj=self)

    def if_none(self, block: Callable[[], object]) -> Object:
        # Guarded on the receiver that does *not* run it: `(5).if_none(5)` said
        # nothing while `None.if_none(5)` leaked, so whether a wrong argument
        # was reported depended on the value in hand.
        a_block(block, "if_none", param="")
        return self

    def if_not_none[T](self, block: Callable[[Object], T]) -> T:
        return a_block(block, "if_not_none")(self)

    def is_none(self) -> Boolean:
        return false

    def not_none(self) -> Boolean:
        return true

    def is_identical(self, other: Object) -> Boolean:
        return to_boolean(self is other)

    def not_identical(self, other: Object) -> Boolean:
        return to_boolean(self is not other)

    def not_(self) -> Boolean:
        return to_boolean(not bool(self))

    def assert_(self, message: Str | NoneClass | None = None) -> Self:
        if bool(self):
            return self
        if _is_absent(message):
            raise mirrors.AssertionError
        # `assert x, msg` takes any object as the message in CPython, so an
        # unwrappable one goes through raw rather than leaking #_value.
        raise mirrors.AssertionError(_faithful(message))

    def class_name(self) -> Str:
        # `x class name` in Smalltalk: the name is the class's to answer, not
        # a fact the instance knows about itself.
        return self.class_().name()

    def hash(self) -> Int:
        try:
            return Int(hash(self))
        except TypeError as exc:
            # The substitute `no_hash` names, answering CPython's bare sentence
            # on nine receivers while `{[1]}` and `{}.at_put([1], 2)` — the same
            # condition, one level in — answered one that says where the value
            # was going. Unmatched text passes through, on the rule `_message`'s
            # module docstring sets for every rewrite here.
            reworded = cannot_be_hashed(exc)
            if reworded is None:
                raise
            raise mirrors.TypeError(reworded) from None

    def callable(self) -> Boolean:
        return to_boolean(builtins.callable(self))

    def is_instance(self, type_: type) -> Boolean:
        # `unalias` because a bare `int` resolves to the alias that makes a
        # *call* mean conversion, and an `Int` is not an instance of it.
        return to_boolean(isinstance(self, a_class(unalias(type_), "is_instance")))

    @classmethod
    def is_subclass(cls, other: type) -> Boolean:
        return to_boolean(issubclass(cls, a_class(unalias(other), "is_subclass")))

    def repr(self) -> Str:
        return Str(builtins.repr(self))

    def ascii(self) -> Str:
        return Str(builtins.ascii(self))

    def dir(self) -> List:
        # Filter every `_`-prefixed name — dunders (banned by
        # no_dunder_attribute) and privates, including the mangled `_poop_*`
        # bindings — so the introspection substitute never surfaces what the
        # encapsulation rules hide. `is_message` is the one copy of that rule,
        # shared with `:methods`, the near-miss hint and the REPL's completer.
        return List(*(Str(name) for name in builtins.dir(self) if is_message(name)))

    def format(self, spec: Str | NoneClass | None = None) -> Str:
        # Two leaks in one method. A non-`Str` spec answered `format()
        # argument 2 must be str, not int` — the builtin `no_format` bans,
        # spelt as the call this message replaces...
        spec_value = (
            "" if _is_absent(spec) else text_like(spec, "format", "a str", (str,))
        )
        target = _faithful(self)
        try:
            return Str(builtins.format(target, spec_value))
        except ValueError as exc:
            # The third leak, and the one a validator pointed at. `no_format`
            # bans `format(x, spec)` and names `x.format(spec)`, and this method
            # already caught the `TypeError` beside this clause and composed
            # POOP's sentence for it — while the `ValueError` CPython raises
            # from the same call passed straight through. So the template
            # spelling answered `a float cannot be formatted with 'd'` and the
            # message spelling answered `Unknown format code 'd' for object of
            # type 'float'`: one failure, two vocabularies, chosen by which
            # spelling the reader used. `_template_refusal` is receiver-
            # independent — it reads the class name out of CPython's text — so
            # both spellings now compose the same sentence.
            raise _template_refusal(exc) from None
        except TypeError:
            # ...and a receiver with no `_value` fell through to
            # `object.__format__`, which refuses every non-empty spec by
            # naming the dunder: `unsupported format string passed to
            # list.__format__`. CPython refuses these too — only the sentence
            # is POOP's to write.
            raise mirrors.TypeError(no_format_spec(type(self).__name__)) from None

    def get_attr(self, name: Str, default: object = MISSING) -> object:
        # Guarded before the default is consulted: a forbidden name is refused,
        # not quietly answered with a fallback. One optional default, as
        # `getattr` takes one: `*default` forwarded a third argument to the
        # builtin, which refused it in its own words (`getattr expected at
        # most 3 arguments, got 4`), naming the call `no_getattr` bans.
        raw = _checked_name(name)
        if default is MISSING:
            return _as_block(builtins.getattr(self, raw))
        return _as_block(builtins.getattr(self, raw, default))

    def has_attr(self, symbol: Str) -> Boolean:
        return to_boolean(hasattr(self, _checked_name(symbol)))

    def set_attr(self, name: Str, value: object) -> NoneClass:
        # Outside the `try`: `_checked_name`'s own refusals are AttributeErrors
        # too, and each already carries the sentence it wants to be read by.
        raw = _checked_name(name)
        try:
            builtins.setattr(self, raw, value)
        except AttributeError:
            # A value declares `__slots__` and holds no attached state;
            # `set_attr` composes the sentence itself, as `del_attr` does,
            # since no `__setattr__` on `Object` rewords it any more.
            raise _holds_no_state(self) from None
        return none

    def del_attr(self, name: Str) -> NoneClass:
        # Outside the `try`, as in `set_attr`: `_checked_name`'s own refusals
        # are AttributeErrors too and already carry their sentence.
        raw = _checked_name(name)
        try:
            builtins.delattr(self, raw)
        except AttributeError:
            # Two failures, two sentences. An object that *can* hold state
            # simply does not hold this name; one that cannot is a value, and
            # CPython says so by naming `no __dict__ for setting new
            # attributes` — the dunder `_reject_dunder` will not even let a
            # program spell. `set_attr` needs only the second, since a
            # receiver with a `__dict__` never fails there.
            if builtins.hasattr(self, "__dict__"):
                raise mirrors.AttributeError(
                    f"{type(self).__name__} has no attribute {raw!r} to remove"
                ) from None
            raise _holds_no_state(self) from None
        return none

    def print(
        self,
        end: Str | NoneClass | None = None,
        flush: Boolean | NoneClass | None = None,
    ) -> NoneClass:
        end_value = _unwrap(end, "\n")
        flush_value = _unwrap_bool(flush, False)
        builtins.print(str(self), end=end_value, flush=flush_value)  # noqa: T201
        return none

    def __str__(self) -> str:
        return f"<{self.class_name()}>"

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other: object) -> Boolean:
        return to_boolean(self is other)

    def __ne__(self, other: object) -> Boolean:
        # The one `__ne__`: a POOP `==` answers a `Boolean`, so Python's
        # derived `__ne__` (a raw `bool`) cannot be used — but every rule for
        # equality lives in an `__eq__`, and restating each one here with the
        # answer flipped meant keeping two copies in step by hand.
        return to_boolean(not bool(self == other))

    def __hash__(self) -> int:
        # Python's own identity hash, not `id(self)`. Defining __eq__ clears
        # __hash__, so this has to exist for Dict and Set to key on a plain
        # object at all — but answering the address exactly made `x.hash()`
        # print the raw pointer POOP otherwise never admits exists, and made
        # it indistinguishable from the `id` message that used to sit here.
        return object.__hash__(self)


cloak(Object, "object")
