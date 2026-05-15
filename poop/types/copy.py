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
    track recursive identities during traversal) is **not** surfaced
    in POOP — it's a CPython implementation detail with no clean
    type-discipline mapping (the dict is keyed by `id(obj)`, an
    `int`, not a POOP key). Callers wanting custom memoization can
    implement `__deepcopy__` on their POOP class.

    `copy.replace` (3.13+) is out of scope for v1; deferred to
    Future work.
    """

    Error: ClassVar[type[Exception]] = _copy.Error

    @staticmethod
    def copy(obj: Any) -> Any:
        return _copy.copy(obj)

    @staticmethod
    def deepcopy(obj: Any) -> Any:
        return _copy.deepcopy(obj)
