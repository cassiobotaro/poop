from typing import ClassVar

from poop.transformers._forwarding import make_forwarding_rewriter
from poop.transformers.base import BaseTransformer
from poop.types.exceptions import MIRRORS
from poop.types.zip import Zip


def _poop_zip(*sources: object, strict: object = None) -> Zip:
    from poop.types._unwrap import _is_absent
    from poop.types.boolean import Boolean

    if _is_absent(strict):
        return Zip(*sources, strict=None)
    if isinstance(strict, Boolean):
        return Zip(*sources, strict=strict)
    raise MIRRORS["TypeError"](
        f"strict must be Boolean, got {type(strict).__qualname__}"
    )


class ZipTransformer(BaseTransformer):
    rewriter = make_forwarding_rewriter("zip", "_poop_zip", "_poop_zip_cls")
    BINDINGS: ClassVar[dict[str, object]] = {
        "_poop_zip": _poop_zip,
        "_poop_zip_cls": Zip,
    }
