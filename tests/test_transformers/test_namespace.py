import pytest

from poop.transformers import DEFAULT_NAMESPACE, _merge_bindings


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
