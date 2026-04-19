from poop.transformers.base import Transformer
from poop.transformers.boolean import BooleanTransformer
from poop.transformers.int import IntTransformer
from poop.transformers.none import NoneTransformer
from poop.types.transcript import transcript

DEFAULT_TRANSFORMERS: list[Transformer] = [
    BooleanTransformer(),
    NoneTransformer(),
    IntTransformer(),
]
DEFAULT_NAMESPACE: dict[str, object] = {
    **BooleanTransformer.BINDINGS,
    **NoneTransformer.BINDINGS,
    **IntTransformer.BINDINGS,
    "Transcript": transcript,
}

__all__ = ["DEFAULT_NAMESPACE", "DEFAULT_TRANSFORMERS", "Transformer"]
