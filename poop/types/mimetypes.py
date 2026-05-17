import mimetypes as _mimetypes
from typing import TYPE_CHECKING, ClassVar

from poop.types._unwrap import _b
from poop.types.boolean import Boolean
from poop.types.dict import Dict
from poop.types.list import List
from poop.types.none import NoneClass, none
from poop.types.string import Str
from poop.types.tuple import Tuple

if TYPE_CHECKING:
    pass


def _str_dict(d: dict[str, str]) -> Dict:
    result = Dict()
    for k, v in d.items():
        result.at_put(Str(k), Str(v))
    return result


def _str_list(items: list[str]) -> List:
    return List(*(Str(s) for s in items))


def _str_value(value: object) -> str:
    # Pulls the underlying Python str from a POOP Str. Iterating over
    # a POOP List yields generic Object — this narrows for the type
    # checker and the operations that need a native str.
    if not isinstance(value, Str):
        raise TypeError(f"expected POOP Str, got {type(value).__name__}")
    return value._value


def _maybe_str(value: str | None) -> Str | NoneClass:
    return none if value is None else Str(value)


class MimeTypes:
    """Reusable registry mirroring Python's `mimetypes.MimeTypes`.

    Instance-level counterpart to the module-level namespace, useful
    when you need an isolated registry without touching global state.
    """

    __slots__ = ("_impl",)

    def __init__(
        self, filenames: List | None = None, strict: Boolean | None = None
    ) -> None:
        if filenames is None:
            self._impl = _mimetypes.MimeTypes(strict=_b(strict, True))
        else:
            python_paths = tuple(_str_value(s) for s in filenames)
            self._impl = _mimetypes.MimeTypes(
                filenames=python_paths, strict=_b(strict, True)
            )

    def guess_type(self, url: Str, strict: Boolean | None = None) -> Tuple:
        mime, encoding = self._impl.guess_type(url._value, strict=_b(strict, True))
        return Tuple(_maybe_str(mime), _maybe_str(encoding))

    def guess_extension(
        self, type: Str, strict: Boolean | None = None
    ) -> Str | NoneClass:
        return _maybe_str(
            self._impl.guess_extension(type._value, strict=_b(strict, True))
        )

    def guess_all_extensions(self, type: Str, strict: Boolean | None = None) -> List:
        exts = self._impl.guess_all_extensions(type._value, strict=_b(strict, True))
        return _str_list(exts)

    def add_type(self, type: Str, ext: Str, strict: Boolean | None = None) -> NoneClass:
        self._impl.add_type(type._value, ext._value, strict=_b(strict, True))
        return none

    def read(self, filename: Str, strict: Boolean | None = None) -> NoneClass:
        self._impl.read(filename._value, strict=_b(strict, True))
        return none


class Mimetypes:
    """Namespace mirroring Python's `mimetypes` module.

    Module-level shortcuts plus the standard registry constants
    (suffix_map / encodings_map / types_map / common_types /
    knownfiles). The `MimeTypes` class (PascalCase) is exposed
    separately for callers that need an isolated registry.
    """

    # Constants — snapshotted from CPython's module-level dicts at
    # import time. Mutations via `add_type` after this point only
    # update CPython's globals; the POOP snapshots are immutable
    # views by design.
    suffix_map: ClassVar[Dict] = _str_dict(_mimetypes.suffix_map)
    encodings_map: ClassVar[Dict] = _str_dict(_mimetypes.encodings_map)
    types_map: ClassVar[Dict] = _str_dict(_mimetypes.types_map)
    common_types: ClassVar[Dict] = _str_dict(_mimetypes.common_types)
    # _mimetypes.knownfiles is typed list[str | PathLike[str]] but
    # CPython's value is always a list of str literals — cast for ty.
    knownfiles: ClassVar[List] = _str_list([str(p) for p in _mimetypes.knownfiles])

    @staticmethod
    def guess_type(url: Str, strict: Boolean | None = None) -> Tuple:
        mime, encoding = _mimetypes.guess_type(url._value, strict=_b(strict, True))
        return Tuple(_maybe_str(mime), _maybe_str(encoding))

    @staticmethod
    def guess_extension(type: Str, strict: Boolean | None = None) -> Str | NoneClass:
        return _maybe_str(
            _mimetypes.guess_extension(type._value, strict=_b(strict, True))
        )

    @staticmethod
    def guess_all_extensions(type: Str, strict: Boolean | None = None) -> List:
        exts = _mimetypes.guess_all_extensions(type._value, strict=_b(strict, True))
        return _str_list(exts)

    @staticmethod
    def add_type(type: Str, ext: Str, strict: Boolean | None = None) -> NoneClass:
        _mimetypes.add_type(type._value, ext._value, strict=_b(strict, True))
        return none

    @staticmethod
    def init(files: List | None = None) -> NoneClass:
        if files is None:
            _mimetypes.init()
        else:
            _mimetypes.init([_str_value(s) for s in files])
        return none

    @staticmethod
    def read_mime_types(file: Str) -> Dict | NoneClass:
        result = _mimetypes.read_mime_types(file._value)
        if result is None:
            return none
        return _str_dict(result)
