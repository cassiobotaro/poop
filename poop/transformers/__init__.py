from poop.transformers.base import Transformer
from poop.transformers.boolean import BooleanTransformer

DEFAULT_TRANSFORMERS: list[Transformer] = [BooleanTransformer()]
DEFAULT_NAMESPACE: dict[str, object] = {**BooleanTransformer.BINDINGS}

__all__ = ["DEFAULT_NAMESPACE", "DEFAULT_TRANSFORMERS", "Transformer"]
