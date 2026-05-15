"""End-to-end integration tests for parse → validate → transform → execute.

Two angles:
1. Every program in `examples/` runs cleanly through the full pipeline —
   real POOP code is the strongest regression net.
2. Every transformer with non-empty BINDINGS — and every namespace-only
   module (`math`, `random`, `path`, `try_`, `with_`) — contributes its
   bindings to DEFAULT_NAMESPACE, so user code can reach `Path`, `Try`,
   `With`, `Map`, `Filter`, etc. without needing to know which source
   exposed them. Catches the "I forgot to wire the binding into
   `transformers/__init__.py`" class of bug.
"""

from pathlib import Path

import pytest

from poop import Interpreter
from poop.transformers import DEFAULT_NAMESPACE
from poop.transformers.base import BaseTransformer
from poop.transformers.math import NAMESPACE as MATH_NAMESPACE
from poop.transformers.path import NAMESPACE as PATH_NAMESPACE
from poop.transformers.random import NAMESPACE as RANDOM_NAMESPACE
from poop.transformers.try_ import NAMESPACE as TRY_NAMESPACE
from poop.transformers.with_ import NAMESPACE as WITH_NAMESPACE

EXAMPLES_DIR = Path(__file__).parent.parent / "examples"
EXAMPLE_FILES = sorted(EXAMPLES_DIR.glob("*.py"))

TRANSFORMERS_WITH_BINDINGS = sorted(
    (cls for cls in BaseTransformer.__subclasses__() if cls.BINDINGS),
    key=lambda c: c.__name__,
)

NAMESPACE_ONLY_MODULES: list[tuple[str, dict[str, object]]] = [
    ("math", MATH_NAMESPACE),
    ("path", PATH_NAMESPACE),
    ("random", RANDOM_NAMESPACE),
    ("try_", TRY_NAMESPACE),
    ("with_", WITH_NAMESPACE),
]


@pytest.mark.parametrize("example", EXAMPLE_FILES, ids=lambda p: p.name)
def test_example_runs_through_full_pipeline(
    example: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("builtins.input", lambda *_args, **_kwargs: "Test")
    Interpreter().run_file(example)


def test_examples_directory_has_files() -> None:
    """Guard against the parametrize silently skipping all examples."""
    assert len(EXAMPLE_FILES) > 0


@pytest.mark.parametrize(
    "transformer_cls",
    TRANSFORMERS_WITH_BINDINGS,
    ids=lambda c: c.__name__,
)
def test_transformer_bindings_present_in_default_namespace(
    transformer_cls: type[BaseTransformer],
) -> None:
    for name, value in transformer_cls.BINDINGS.items():
        assert name in DEFAULT_NAMESPACE, (
            f"{transformer_cls.__name__} declares BINDING '{name}' "
            f"but it is missing from DEFAULT_NAMESPACE — likely not wired "
            f"into poop/transformers/__init__.py"
        )
        assert DEFAULT_NAMESPACE[name] is value, (
            f"{transformer_cls.__name__} BINDING '{name}' resolves to a "
            f"different object than what is in DEFAULT_NAMESPACE"
        )


@pytest.mark.parametrize(
    ("module_name", "namespace"),
    NAMESPACE_ONLY_MODULES,
    ids=[name for name, _ in NAMESPACE_ONLY_MODULES],
)
def test_namespace_module_bindings_present_in_default_namespace(
    module_name: str, namespace: dict[str, object]
) -> None:
    for name, value in namespace.items():
        assert name in DEFAULT_NAMESPACE, (
            f"poop/transformers/{module_name}.py NAMESPACE declares "
            f"'{name}' but it is missing from DEFAULT_NAMESPACE — likely "
            f"not merged in poop/transformers/__init__.py"
        )
        assert DEFAULT_NAMESPACE[name] is value, (
            f"poop/transformers/{module_name}.py NAMESPACE '{name}' "
            f"resolves to a different object than what is in DEFAULT_NAMESPACE"
        )


def test_transformers_with_bindings_discovered() -> None:
    """Guard against subclass discovery silently returning nothing."""
    assert len(TRANSFORMERS_WITH_BINDINGS) > 0
