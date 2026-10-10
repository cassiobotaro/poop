from poop.types._dict_view import _DictView


def test_subclass_without_a_name_keeps_its_own() -> None:
    # The `name=` class keyword cloaks the view; a subclass that omits the
    # keyword keeps the name and the module it was defined with.
    class _Anon(_DictView):
        __slots__ = ()

    assert _Anon.__name__ == "_Anon"
    assert _Anon.__module__ != "builtins"


def test_subclass_with_a_name_adopts_the_cpython_name() -> None:
    class _Named(_DictView, name="dict_thing"):
        __slots__ = ()

    assert _Named.__name__ == "dict_thing"
    assert _Named.__module__ == "builtins"
