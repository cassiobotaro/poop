from __future__ import annotations

import tarfile as _tarfile
from types import TracebackType
from typing import Any, ClassVar, Self

from poop.types.bytes import Bytes
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import NoneClass, none
from poop.types.object import Object
from poop.types.path import Path
from poop.types.string import Str


def _path_str(value: Path | Str) -> str:
    if isinstance(value, Path):
        return str(value._path)
    return value._value


class TarInfo(Object):
    """Wraps Python's `tarfile.TarInfo` — metadata for one TAR entry."""

    __slots__ = ("_impl",)

    def __init__(self, impl: Any) -> None:
        self._impl = impl

    @property
    def name(self) -> Str:
        return Str(self._impl.name)

    @property
    def size(self) -> Int:
        return Int(self._impl.size)

    @property
    def mtime(self) -> Int:
        return Int(int(self._impl.mtime))

    @property
    def mode(self) -> Int:
        return Int(self._impl.mode)

    @property
    def type(self) -> Bytes:
        return Bytes(self._impl.type)

    @property
    def linkname(self) -> Str:
        return Str(self._impl.linkname)

    @property
    def uid(self) -> Int:
        return Int(self._impl.uid)

    @property
    def gid(self) -> Int:
        return Int(self._impl.gid)

    @property
    def uname(self) -> Str:
        return Str(self._impl.uname)

    @property
    def gname(self) -> Str:
        return Str(self._impl.gname)

    @property
    def is_file(self) -> bool:
        return self._impl.isfile()

    @property
    def is_dir(self) -> bool:
        return self._impl.isdir()

    @property
    def is_symlink(self) -> bool:
        return self._impl.issym()

    @property
    def is_link(self) -> bool:
        return self._impl.islnk()


class TarFile(Object):
    """Wraps Python's `tarfile.TarFile` for TAR archive access.

    Path-based construction (modes `"r"`, `"r:*"`, `"r:gz"`,
    `"r:bz2"`, `"r:xz"`, `"w"`, `"w:gz"`, `"w:bz2"`, `"w:xz"`,
    `"a"`); `With`-friendly.
    """

    __slots__ = ("_impl",)

    def __init__(self, impl: Any) -> None:
        self._impl = impl

    @classmethod
    def open(
        cls,
        name: Path | Str,
        mode: Str | None = None,
    ) -> TarFile:
        return cls(
            _tarfile.open(  # ty: ignore[no-matching-overload]
                _path_str(name), "r" if mode is None else mode._value
            )
        )

    @classmethod
    def is_tarfile(cls, name: Path | Str) -> bool:
        return _tarfile.is_tarfile(_path_str(name))

    # Adding ------------------------------------------------------------

    def add(
        self,
        name: Path | Str,
        arcname: Str | None = None,
        recursive: bool = True,
    ) -> NoneClass:
        kwargs: dict[str, Any] = {"recursive": recursive}
        if arcname is not None:
            kwargs["arcname"] = arcname._value
        self._impl.add(_path_str(name), **kwargs)
        return none

    # Extraction --------------------------------------------------------

    def extract(
        self,
        member: Str | TarInfo,
        path: Path | Str | None = None,
        *,
        numeric_owner: bool = False,
        filter: Str | None = None,
    ) -> NoneClass:
        kwargs: dict[str, Any] = {"numeric_owner": numeric_owner}
        if path is not None:
            kwargs["path"] = _path_str(path)
        if filter is not None:
            kwargs["filter"] = filter._value
        target: Any = member._impl if isinstance(member, TarInfo) else member._value
        self._impl.extract(target, **kwargs)
        return none

    def extractall(
        self,
        path: Path | Str | None = None,
        members: List | None = None,
        *,
        numeric_owner: bool = False,
        filter: Str | None = None,
    ) -> NoneClass:
        kwargs: dict[str, Any] = {"numeric_owner": numeric_owner}
        if path is not None:
            kwargs["path"] = _path_str(path)
        # `filter='data'` is the safe default upstream from 3.14.
        kwargs["filter"] = "data" if filter is None else filter._value
        if members is not None:
            unwrapped: list[Any] = []
            for m in members:
                if isinstance(m, TarInfo):
                    unwrapped.append(m._impl)
                else:
                    raise TypeError(
                        f"extractall members must be TarInfo, got {type(m).__name__}"
                    )
            kwargs["members"] = unwrapped
        # POOP's wrapper defaults to filter="data" (safe upstream as of
        # 3.14) — the S202 warning about extractall is mitigated by
        # that default. Callers who pass filter="fully_trusted" opt in
        # to the unsafe behavior explicitly.
        self._impl.extractall(**kwargs)  # noqa: S202
        return none

    # Inspection --------------------------------------------------------

    def getnames(self) -> List:
        return List(*(Str(n) for n in self._impl.getnames()))

    def getmembers(self) -> List:
        return List(*(TarInfo(m) for m in self._impl.getmembers()))

    def getmember(self, name: Str) -> TarInfo:
        return TarInfo(self._impl.getmember(name._value))

    def list(self, verbose: bool = True) -> NoneClass:
        self._impl.list(verbose=verbose)
        return none

    # Lifecycle ---------------------------------------------------------

    def close(self) -> NoneClass:
        self._impl.close()
        return none

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self._impl.__exit__(exc_type, exc_value, traceback)


class Tarfile:
    """Namespace mirroring Python's `tarfile` module — TAR archives
    plus optional gzip/bz2/lzma compression.

    `TarFile.open(name, mode)` is the canonical entry point; modes
    follow CPython (`"r:*"`, `"r:gz"`, `"w:bz2"`, `"w:xz"`, …).
    `extractall` defaults to the safe `"data"` filter (3.14+).
    """

    TarFile: ClassVar[type[TarFile]] = TarFile
    TarInfo: ClassVar[type[TarInfo]] = TarInfo

    # Format constants.
    DEFAULT_FORMAT: ClassVar[Int] = Int(_tarfile.DEFAULT_FORMAT)
    USTAR_FORMAT: ClassVar[Int] = Int(_tarfile.USTAR_FORMAT)
    GNU_FORMAT: ClassVar[Int] = Int(_tarfile.GNU_FORMAT)
    PAX_FORMAT: ClassVar[Int] = Int(_tarfile.PAX_FORMAT)
    ENCODING: ClassVar[Str] = Str(_tarfile.ENCODING)

    # Filter callables exposed as raw Python references; the safe
    # default ("data") is also bound under its name for `Try.except_`.
    data_filter: ClassVar[Any] = staticmethod(_tarfile.data_filter)
    tar_filter: ClassVar[Any] = staticmethod(_tarfile.tar_filter)
    fully_trusted_filter: ClassVar[Any] = staticmethod(_tarfile.fully_trusted_filter)

    # Errors.
    TarError: ClassVar[type[Exception]] = _tarfile.TarError
    ReadError: ClassVar[type[Exception]] = _tarfile.ReadError
    CompressionError: ClassVar[type[Exception]] = _tarfile.CompressionError
    StreamError: ClassVar[type[Exception]] = _tarfile.StreamError
    ExtractError: ClassVar[type[Exception]] = _tarfile.ExtractError
    HeaderError: ClassVar[type[Exception]] = _tarfile.HeaderError
    FilterError: ClassVar[type[Exception]] = _tarfile.FilterError
    AbsolutePathError: ClassVar[type[Exception]] = _tarfile.AbsolutePathError
    OutsideDestinationError: ClassVar[type[Exception]] = (
        _tarfile.OutsideDestinationError
    )
    SpecialFileError: ClassVar[type[Exception]] = _tarfile.SpecialFileError
    AbsoluteLinkError: ClassVar[type[Exception]] = _tarfile.AbsoluteLinkError
    LinkOutsideDestinationError: ClassVar[type[Exception]] = (
        _tarfile.LinkOutsideDestinationError
    )

    @staticmethod
    def open(
        name: Path | Str | None = None,
        mode: Str = Str("r"),
        fileobj: Any = None,
        bufsize: Int = Int(10240),
    ) -> TarFile:
        # `fileobj` and `bufsize` accept the CPython signature for parity;
        # POOP's TarFile is path-based, so `fileobj` must be `None`. Caller
        # passes the path via `name`.
        if fileobj is not None:
            raise TypeError("POOP TarFile is path-based; pass `name`, not `fileobj`")
        del bufsize  # accepted for signature parity, no-op for path-mode
        if name is None:
            raise TypeError("TarFile.open requires a `name` (Path or Str)")
        return TarFile.open(name, mode)
