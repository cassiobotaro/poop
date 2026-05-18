import copy as _copy
from typing import Any, ClassVar


class Copy:
    """Namespace mirroring Python's `copy` module — shallow and deep
    copying.

    POOP types implement `__copy__` / `__deepcopy__` via the standard
    Python protocol; the namespace just routes calls. The `Error`
    exception class is exposed as a raw Python type for use with
    `Try.except_(...)`.

    `deepcopy`'s `memo` parameter (an id-keyed dict CPython uses to
    track recursive identities during traversal) is exposed as an
    opaque passthrough; user code typically leaves it `None` and
    overrides `__deepcopy__` on the POOP class for custom memoization.

    `copy.replace(obj, **changes)` (3.13+) is exposed for POOP classes
    that implement `__replace__` (dataclass-style or hand-rolled).
    """

    Error: ClassVar[type[Exception]] = _copy.Error

    @staticmethod
    def copy(x: Any) -> Any:
        return _copy.copy(x)

    @staticmethod
    def deepcopy(x: Any, memo: Any = None) -> Any:
        return _copy.deepcopy(x, memo)

    @staticmethod
    def replace(obj: Any, /, **changes: Any) -> Any:
        return _copy.replace(obj, **changes)
