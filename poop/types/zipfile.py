from __future__ import annotations

import zipfile as _zipfile
from types import TracebackType
from typing import Any, ClassVar, Self

from poop.types._unwrap import _kwargs_from, _opt_int
from poop.types.bytes import Bytes
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import NoneClass, none
from poop.types.object import Object
from poop.types.path import Path
from poop.types.string import Str
from poop.types.tuple import Tuple


def _path_str(value: Path | Str) -> str:
    if isinstance(value, Path):
        return str(value._path)
    return value._value


class ZipInfo(Object):
    """Wraps Python's `zipfile.ZipInfo` — metadata for one ZIP entry.

    `.filename` is the archive name; `.file_size` / `.compress_size`
    are byte counts; `.date_time` is a `Tuple(Int, Int, Int, Int, Int, Int)`
    of `(year, month, day, hour, minute, second)`; `.compress_type`
    matches one of the `ZIP_*` constants.
    """

    __slots__ = ("_impl",)

    def __init__(self, impl: Any) -> None:
        self._impl = impl

    @property
    def filename(self) -> Str:
        return Str(self._impl.filename)

    @property
    def file_size(self) -> Int:
        return Int(self._impl.file_size)

    @property
    def compress_size(self) -> Int:
        return Int(self._impl.compress_size)

    @property
    def compress_type(self) -> Int:
        return Int(self._impl.compress_type)

    @property
    def date_time(self) -> Tuple:
        return Tuple(*(Int(part) for part in self._impl.date_time))

    @property
    def CRC(self) -> Int:
        return Int(self._impl.CRC)

    @property
    def is_dir(self) -> bool:
        return self._impl.is_dir()


class ZipFile(Object):
    """Wraps Python's `zipfile.ZipFile` for read/write archive access.

    Path-based construction; `With`-friendly. The `pwd` for encrypted
    archives is passed as `Bytes`. `extract` / `extractall` accept a
    `Path` extraction target.
    """

    __slots__ = ("_impl",)

    def __init__(
        self,
        file: Path | Str,
        mode: Str | None = None,
        compression: Int | None = None,
        allowZip64: bool = True,
        compresslevel: Int | None = None,
    ) -> None:
        kwargs: dict[str, Any] = {
            "allowZip64": allowZip64,
        }
        if compresslevel is not None:
            kwargs["compresslevel"] = compresslevel._value
        self._impl = _zipfile.ZipFile(  # ty: ignore[no-matching-overload]
            _path_str(file),
            "r" if mode is None else mode._value,
            compression=_opt_int(compression, _zipfile.ZIP_STORED),
            **kwargs,
        )

    # Reading -----------------------------------------------------------

    def read(self, name: Str, pwd: Bytes | None = None) -> Bytes:
        kwargs = _kwargs_from(pwd=pwd)
        return Bytes(self._impl.read(name._value, **kwargs))

    def namelist(self) -> List:
        return List(*(Str(n) for n in self._impl.namelist()))

    def infolist(self) -> List:
        return List(*(ZipInfo(info) for info in self._impl.infolist()))

    def getinfo(self, name: Str) -> ZipInfo:
        return ZipInfo(self._impl.getinfo(name._value))

    def testzip(self) -> Str | NoneClass:
        result = self._impl.testzip()
        if result is None:
            return none
        return Str(result)

    # Writing -----------------------------------------------------------

    def write(self, filename: Path | Str, arcname: Str | None = None) -> NoneClass:
        kwargs = _kwargs_from(arcname=arcname)
        self._impl.write(_path_str(filename), **kwargs)
        return none

    def writestr(self, name: Str, data: Bytes | Str) -> NoneClass:
        raw: Any = data._value
        self._impl.writestr(name._value, raw)
        return none

    # Extraction --------------------------------------------------------

    def extract(
        self,
        member: Str,
        path: Path | Str | None = None,
        pwd: Bytes | None = None,
    ) -> Path:
        kwargs: dict[str, Any] = {}
        if path is not None:
            kwargs["path"] = _path_str(path)
        if pwd is not None:
            kwargs["pwd"] = pwd._value
        return Path(Str(self._impl.extract(member._value, **kwargs)))

    def extractall(
        self,
        path: Path | Str | None = None,
        members: List | None = None,
        pwd: Bytes | None = None,
    ) -> NoneClass:
        kwargs: dict[str, Any] = {}
        if path is not None:
            kwargs["path"] = _path_str(path)
        if pwd is not None:
            kwargs["pwd"] = pwd._value
        if members is not None:
            names: list[str] = []
            for m in members:
                if not isinstance(m, Str):
                    raise TypeError(
                        f"extractall members must be Str, got {type(m).__name__}"
                    )
                names.append(m._value)
            kwargs["members"] = names
        self._impl.extractall(**kwargs)
        return none

    # Password / lifecycle ---------------------------------------------

    def setpassword(self, pwd: Bytes) -> NoneClass:
        self._impl.setpassword(pwd._value)
        return none

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


class Zipfile:
    """Namespace mirroring Python's `zipfile` module."""

    ZipFile: ClassVar[type[ZipFile]] = ZipFile
    ZipInfo: ClassVar[type[ZipInfo]] = ZipInfo

    # Compression constants.
    ZIP_STORED: ClassVar[Int] = Int(_zipfile.ZIP_STORED)
    ZIP_DEFLATED: ClassVar[Int] = Int(_zipfile.ZIP_DEFLATED)
    ZIP_BZIP2: ClassVar[Int] = Int(_zipfile.ZIP_BZIP2)
    ZIP_LZMA: ClassVar[Int] = Int(_zipfile.ZIP_LZMA)

    # Errors.
    BadZipFile: ClassVar[type[Exception]] = _zipfile.BadZipFile
    LargeZipFile: ClassVar[type[Exception]] = _zipfile.LargeZipFile

    @staticmethod
    def is_zipfile(filename: Path | Str) -> bool:
        return _zipfile.is_zipfile(_path_str(filename))
