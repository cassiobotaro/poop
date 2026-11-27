import pytest

from poop.transformers.base import BaseTransformer


def test_a_transformer_without_a_rewriter_fails_at_definition() -> None:
    # As `CollectingValidator` does for its `visitor`: otherwise the mistake
    # surfaced on the first program the transformer was handed.
    with pytest.raises(TypeError, match="sets no `rewriter`"):

        class _Incomplete(BaseTransformer):
            pass
