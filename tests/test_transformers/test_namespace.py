import ast

import pytest

from poop.transformers import DEFAULT_NAMESPACE
from poop.transformers._registry import _merge_bindings


def test_merge_bindings_folds_sources_left_to_right() -> None:
    merged = _merge_bindings([{"a": 1}, {"b": 2}])
    assert merged == {"a": 1, "b": 2}


def test_merge_bindings_rejects_a_duplicate_key_across_sources() -> None:
    # A new transformer whose BINDINGS collide with an earlier source must fail
    # loudly at build time rather than silently shadowing the existing name.
    with pytest.raises(RuntimeError, match="duplicate bindings.*'a'"):
        _merge_bindings([{"a": 1}, {"a": 2}])


def test_default_namespace_exposes_only_try_and_with_to_user_code() -> None:
    user_facing = {k for k in DEFAULT_NAMESPACE if not k.startswith("_poop_")}
    assert user_facing == {"Try", "With"}


# Every mangled key is one some rewrite emits — a binding nothing reaches is
# dead weight in every program's namespace, and seven of them were. Rather
# than a hand-kept list of live keys (a second list to keep in step), the
# corpus below spells every literal and call the pipeline rewrites, and the
# rewriters' own targets cover the names a bare mention resolves to.

_CORPUS = """
class A(object):
    def m(self, *args, **kw):
        a, *rest = [1, 2.5, "s", b"b", 1j, True, False, None, ...]
        t = (1, *rest)
        s = {1, *rest}
        d = {"k": 1, **kw}
        return Try(lambda: ValueError.raise_("x")).except_(Exception, lambda e: e).run()
x = int("1") + float("1") + complex(1) + bool(1) + str(1)
w = With(lambda: A()).do(lambda a: a)
list(x); tuple(x); set(x); dict(x); bytes(x); bytearray(x); memoryview(x)
frozenset(x); frozendict(x); slice(x); range(x); zip(x); enumerate(x); sentinel(x)
A().m(*(1,), **{"a": 1})
"""


def test_every_mangled_binding_is_reached_by_a_rewrite() -> None:
    from poop.interpreter import Interpreter  # noqa: PLC0415 — a test's local
    from poop.transformers._registry import _TRANSFORMER_CLASSES  # noqa: PLC0415
    from poop.types.exceptions import MIRROR_NAMES  # noqa: PLC0415

    source = _CORPUS + "\n".join(MIRROR_NAMES) + "\n"
    tree = Interpreter(validators=[]).transform_source(source)
    emitted = {
        node.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Name) and node.id.startswith("_poop_")
    }
    declared = {
        target
        for cls in _TRANSFORMER_CLASSES
        for attr in ("call_target", "name_target", "literal_target")
        if isinstance(target := getattr(cls.rewriter, attr, None), str)
    }
    mangled = {key for key in DEFAULT_NAMESPACE if key.startswith("_poop_")}
    assert mangled - emitted - declared == set()
