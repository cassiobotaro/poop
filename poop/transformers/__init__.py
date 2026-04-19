from poop.transformers.base import Transformer
from poop.transformers.boolean import BooleanTransformer
from poop.transformers.float import FloatTransformer
from poop.transformers.int import IntTransformer
from poop.transformers.none import NoneTransformer
from poop.types.transcript import transcript

DEFAULT_TRANSFORMERS: list[Transformer] = [
    BooleanTransformer(),
    NoneTransformer(),
    IntTransformer(),
    FloatTransformer(),
]
DEFAULT_NAMESPACE: dict[str, object] = {
    **BooleanTransformer.BINDINGS,
    **NoneTransformer.BINDINGS,
    **IntTransformer.BINDINGS,
    **FloatTransformer.BINDINGS,
    "Transcript": transcript,
}

__all__ = ["DEFAULT_NAMESPACE", "DEFAULT_TRANSFORMERS", "Transformer"]
