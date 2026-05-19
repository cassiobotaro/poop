from __future__ import annotations

import tempfile as _tempfile
from types import TracebackType
from typing import Any, ClassVar, Self

from poop.types._unwrap import _b, _opt_str
from poop.types.boolean import Boolean
from poop.types.bytes import Bytes
from poop.types.int import Int
from poop.types.none import NoneClass, none
from poop.types.object import Object
from poop.types.path import Path
from poop.types.string import Str
from poop.types.tuple import Tuple


def _unwrap_dir(value: Path | Str | NoneClass | None) -> str | None:
    from poop.types._unwrap import _is_absent

    if _is_absent(value):
        return None
    if isinstance(value, Path):
        return str(value._path)
    return value._value  # ty: ignore[unresolved-attribute]


class TemporaryDirectory(Object):
    """Wraps Python's `tempfile.TemporaryDirectory` — a temp dir that
    deletes its tree on close.

    `with TemporaryDirectory() as path:` yields the directory `Path`.
    Outside the `With` form, `.name` exposes the dir path and
    `.cleanup()` triggers explicit removal.
    """

    __slots__ = ("_impl",)

    def __init__(
        self,
        suffix: Str | NoneClass | None = None,
        prefix: Str | NoneClass | None = None,
        dir: Path | Str | NoneClass | None = None,
        ignore_cleanup_errors: Boolean | NoneClass | None = None,
        *,
        delete: Boolean | NoneClass | None = None,
    ) -> None:
        self._impl = _tempfile.TemporaryDirectory(
            suffix=_opt_str(suffix),
            prefix=_opt_str(prefix),
            dir=_unwrap_dir(dir),
            ignore_cleanup_errors=_b(ignore_cleanup_errors, False),
            delete=_b(delete, True),
        )

    @property
    def name(self) -> Path:
        return Path._from_pathlib(__import__("pathlib").Path(self._impl.name))

    def cleanup(self) -> NoneClass:
        self._impl.cleanup()
        return none

    def __enter__(self) -> Path:
        return Path(Str(self._impl.__enter__()))

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self._impl.__exit__(exc_type, exc_value, traceback)


class _TempFileBase(Object):
    """Shared scaffolding for the TemporaryFile / NamedTemporaryFile /
    SpooledTemporaryFile wrappers — exposes the common close/context-
    manager surface plus minimal binary read/write so callers can
    populate or drain the file without a separate POOP I/O abstraction.
    """

    __slots__ = ("_impl",)
    _impl: Any

    def write(self, data: Bytes | Str) -> Int:
        if isinstance(data, Str):
            return Int(self._impl.write(data._value))
        return Int(self._impl.write(data._value))

    def read(self, size: Int | None = None) -> Bytes | Str:
        raw = self._impl.read() if size is None else self._impl.read(size._value)
        if isinstance(raw, str):
            return Str(raw)
        return Bytes(raw)

    def seek(self, offset: Int, whence: Int | None = None) -> Int:
        if whence is None:
            return Int(self._impl.seek(offset._value))
        return Int(self._impl.seek(offset._value, whence._value))

    def tell(self) -> Int:
        return Int(self._impl.tell())

    def flush(self) -> NoneClass:
        self._impl.flush()
        return none

    def close(self) -> NoneClass:
        self._impl.close()
        return none

    def __enter__(self) -> Self:
        self._impl.__enter__()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self._impl.__exit__(exc_type, exc_value, traceback)


class TemporaryFile(_TempFileBase):
    """Wraps Python's `tempfile.TemporaryFile` — an anonymous temp file.

    No `.name` (the file is unlinked on most platforms immediately
    after open). Use the `With` form to scope its lifetime; read/write
    via `.read` / `.write` while the handle is open.
    """

    __slots__ = ()

    def __init__(
        self,
        mode: Str | None = None,
        suffix: Str | None = None,
        prefix: Str | None = None,
        dir: Path | Str | None = None,
    ) -> None:
        self._impl = _tempfile.TemporaryFile(
            mode="w+b" if mode is None else mode._value,
            suffix=_opt_str(suffix),
            prefix=_opt_str(prefix),
            dir=_unwrap_dir(dir),
        )


class NamedTemporaryFile(_TempFileBase):
    """Wraps Python's `tempfile.NamedTemporaryFile` — a temp file with
    a visible path.

    `.name` exposes the on-disk `Path`; `delete=true` (CPython default)
    removes it on close. Inside `With`, the wrapper yields itself —
    use `.name` to obtain the path for downstream code.
    """

    __slots__ = ()

    def __init__(
        self,
        mode: Str | NoneClass | None = None,
        suffix: Str | NoneClass | None = None,
        prefix: Str | NoneClass | None = None,
        dir: Path | Str | NoneClass | None = None,
        delete: Boolean | NoneClass | None = None,
        *,
        delete_on_close: Boolean | NoneClass | None = None,
    ) -> None:
        self._impl = _tempfile.NamedTemporaryFile(
            mode="w+b" if mode is None or isinstance(mode, NoneClass) else mode._value,
            suffix=_opt_str(suffix),
            prefix=_opt_str(prefix),
            dir=_unwrap_dir(dir),
            delete=_b(delete, True),
            delete_on_close=_b(delete_on_close, True),
        )

    @property
    def name(self) -> Path:
        return Path(Str(self._impl.name))


class SpooledTemporaryFile(_TempFileBase):
    """Wraps Python's `tempfile.SpooledTemporaryFile` — held in memory
    until it exceeds `max_size`, then rolled to disk.

    `.rollover()` forces an immediate flush to disk regardless of size.
    """

    __slots__ = ()

    def __init__(
        self,
        max_size: Int | None = None,
        mode: Str | None = None,
        suffix: Str | None = None,
        prefix: Str | None = None,
        dir: Path | Str | None = None,
    ) -> None:
        self._impl = _tempfile.SpooledTemporaryFile(
            max_size=0 if max_size is None else max_size._value,
            mode="w+b" if mode is None else mode._value,
            suffix=_opt_str(suffix),
            prefix=_opt_str(prefix),
            dir=_unwrap_dir(dir),
        )

    def rollover(self) -> NoneClass:
        self._impl.rollover()
        return none


class _TempfileNamespace:
    """Singleton namespace mirroring Python's `tempfile` module.

    Python's `tempfile.tempdir` is exposed as a `@property` with a
    setter — assign to `tempfile.tempdir` to change the search
    default, just like in Python. The four context-manager classes
    are exposed as class attributes.
    """

    TemporaryFile: ClassVar[type[TemporaryFile]] = TemporaryFile
    NamedTemporaryFile: ClassVar[type[NamedTemporaryFile]] = NamedTemporaryFile
    SpooledTemporaryFile: ClassVar[type[SpooledTemporaryFile]] = SpooledTemporaryFile
    TemporaryDirectory: ClassVar[type[TemporaryDirectory]] = TemporaryDirectory

    def mkstemp(
        self,
        suffix: Str | None = None,
        prefix: Str | None = None,
        dir: Path | Str | None = None,
        text: Boolean | None = None,
    ) -> Tuple:
        fd, name = _tempfile.mkstemp(
            suffix=_opt_str(suffix),
            prefix=_opt_str(prefix),
            dir=_unwrap_dir(dir),
            text=_b(text, False),
        )
        return Tuple(Int(fd), Path(Str(name)))

    def mkdtemp(
        self,
        suffix: Str | None = None,
        prefix: Str | None = None,
        dir: Path | Str | None = None,
    ) -> Path:
        return Path(
            Str(
                _tempfile.mkdtemp(
                    suffix=_opt_str(suffix),
                    prefix=_opt_str(prefix),
                    dir=_unwrap_dir(dir),
                )
            )
        )

    def gettempdir(self) -> Path:
        return Path(Str(_tempfile.gettempdir()))

    def gettempprefix(self) -> Str:
        return Str(_tempfile.gettempprefix())

    def gettempdirb(self) -> Bytes:
        return Bytes(_tempfile.gettempdirb())

    def gettempprefixb(self) -> Bytes:
        return Bytes(_tempfile.gettempprefixb())

    @property
    def tempdir(self) -> Path | NoneClass:
        current = _tempfile.tempdir
        if current is None:
            return none
        return Path(Str(current))

    @tempdir.setter
    def tempdir(self, path: Path | Str | NoneClass | None) -> None:
        if path is None or isinstance(path, NoneClass):
            _tempfile.tempdir = None
        elif isinstance(path, Path):
            _tempfile.tempdir = str(path._path)
        else:
            _tempfile.tempdir = path._value


TempfileNamespace = _TempfileNamespace()
