import pytest

from poop.transformers.base import BaseTransformer


def test_a_transformer_without_a_rewriter_fails_at_definition() -> None:
    # As `CollectingValidator` does for its `visitor`: otherwise the mistake
    # surfaced on the first program the transformer was handed.
    with pytest.raises(TypeError, match="sets no `rewriter`") as excinfo:

        class _Incomplete(BaseTransformer):
            pass

    # The native class, not POOP's mirror: no program can define a transformer.
    assert excinfo.type is TypeError
