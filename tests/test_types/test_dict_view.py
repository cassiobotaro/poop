from poop.types._dict_view import _DictView


def test_subclass_without_a_name_keeps_the_default_repr_name() -> None:
    # `__init_subclass__(name=...)` renames the view; a subclass that omits the
    # keyword inherits the base `dict_view` repr name unchanged.
    class _Anon(_DictView):
        __slots__ = ()

    assert _Anon._repr_name == "dict_view"
    assert _Anon.__name__ == "_Anon"


def test_subclass_with_a_name_adopts_the_cpython_name() -> None:
    class _Named(_DictView, name="dict_thing"):
        __slots__ = ()

    assert _Named._repr_name == "dict_thing"
    assert _Named.__name__ == "dict_thing"
    assert _Named.__module__ == "builtins"
