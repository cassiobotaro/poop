from __future__ import annotations

import pathlib as _pathlib
from typing import TYPE_CHECKING

from poop.types.boolean import false, true
from poop.types.none import none
from poop.types.object import Object

if TYPE_CHECKING:
    from poop.types.boolean import Boolean
    from poop.types.bytes import Bytes
    from poop.types.int import Int
    from poop.types.list import List
    from poop.types.none import NoneClass
    from poop.types.string import Str
    from poop.types.tuple import Tuple


class Path(Object):
    __slots__ = ("_path",)

    def __init__(self, path: Str | Path) -> None:
        from poop.types.string import Str

        if isinstance(path, Path):
            self._path = path._path
            return
        if isinstance(path, Str):
            self._path = _pathlib.Path(path._value)
            return
        raise TypeError("Path expects Str or Path")

    @classmethod
    def _from_pathlib(cls, path: _pathlib.Path) -> Path:
        obj = cls.__new__(cls)
        obj._path = path
        return obj

    @staticmethod
    def _coerce_path(path: Str | Path) -> _pathlib.Path:
        from poop.types.string import Str

        if isinstance(path, Path):
            return path._path
        if isinstance(path, Str):
            return _pathlib.Path(path._value)
        raise TypeError("Path expects Str or Path")

    @classmethod
    def cwd(cls) -> Path:
        return cls._from_pathlib(_pathlib.Path.cwd())

    @classmethod
    def home(cls) -> Path:
        return cls._from_pathlib(_pathlib.Path.home())

    def read_text(self) -> Str:
        from poop.types.string import Str

        return Str(self._path.read_text())

    def write_text(self, content: Str) -> Int:
        from poop.types.int import Int

        return Int(self._path.write_text(content._value))

    def read_bytes(self) -> Bytes:
        from poop.types.bytes import Bytes

        return Bytes(self._path.read_bytes())

    def write_bytes(self, data: Bytes) -> Int:
        from poop.types.int import Int

        return Int(self._path.write_bytes(data._value))

    def exists(self) -> Boolean:
        return true if self._path.exists() else false

    def is_file(self) -> Boolean:
        return true if self._path.is_file() else false

    def is_dir(self) -> Boolean:
        return true if self._path.is_dir() else false

    def is_symlink(self) -> Boolean:
        return true if self._path.is_symlink() else false

    def is_absolute(self) -> Boolean:
        return true if self._path.is_absolute() else false

    def mkdir(
        self, parents: Boolean | None = None, exist_ok: Boolean | None = None
    ) -> NoneClass:
        parents_value = False if parents is None else bool(parents)
        exist_ok_value = False if exist_ok is None else bool(exist_ok)
        self._path.mkdir(parents=parents_value, exist_ok=exist_ok_value)
        return none

    def rmdir(self) -> NoneClass:
        self._path.rmdir()
        return none

    def unlink(self, missing_ok: Boolean | None = None) -> NoneClass:
        missing_ok_value = False if missing_ok is None else bool(missing_ok)
        self._path.unlink(missing_ok=missing_ok_value)
        return none

    def touch(self, exist_ok: Boolean | None = None) -> NoneClass:
        exist_ok_value = True if exist_ok is None else bool(exist_ok)
        self._path.touch(exist_ok=exist_ok_value)
        return none

    def resolve(self) -> Path:
        return Path._from_pathlib(self._path.resolve())

    def absolute(self) -> Path:
        return Path._from_pathlib(self._path.absolute())

    def rename(self, target: Str | Path) -> Path:
        return Path._from_pathlib(self._path.rename(Path._coerce_path(target)))

    def replace(self, target: Str | Path) -> Path:
        return Path._from_pathlib(self._path.replace(Path._coerce_path(target)))

    def joinpath(self, *others: Str | Path) -> Path:
        raw = [Path._coerce_path(other) for other in others]
        return Path._from_pathlib(self._path.joinpath(*raw))

    def with_name(self, name: Str) -> Path:
        return Path._from_pathlib(self._path.with_name(name._value))

    def with_suffix(self, suffix: Str) -> Path:
        return Path._from_pathlib(self._path.with_suffix(suffix._value))

    def with_stem(self, stem: Str) -> Path:
        return Path._from_pathlib(self._path.with_stem(stem._value))

    def relative_to(self, other: Str | Path) -> Path:
        return Path._from_pathlib(self._path.relative_to(Path._coerce_path(other)))

    def as_posix(self) -> Str:
        from poop.types.string import Str

        return Str(self._path.as_posix())

    def as_uri(self) -> Str:
        from poop.types.string import Str

        return Str(self._path.as_uri())

    def iterdir(self) -> List:
        from poop.types.list import List

        return List(*(Path._from_pathlib(p) for p in self._path.iterdir()))

    def glob(self, pattern: Str) -> List:
        from poop.types.list import List

        return List(*(Path._from_pathlib(p) for p in self._path.glob(pattern._value)))

    def rglob(self, pattern: Str) -> List:
        from poop.types.list import List

        return List(*(Path._from_pathlib(p) for p in self._path.rglob(pattern._value)))

    @property
    def name(self) -> Str:
        from poop.types.string import Str

        return Str(self._path.name)

    @property
    def stem(self) -> Str:
        from poop.types.string import Str

        return Str(self._path.stem)

    @property
    def suffix(self) -> Str:
        from poop.types.string import Str

        return Str(self._path.suffix)

    @property
    def parts(self) -> Tuple:
        from poop.types.string import Str
        from poop.types.tuple import Tuple

        return Tuple(*(Str(part) for part in self._path.parts))

    @property
    def parent(self) -> Path:
        return Path._from_pathlib(self._path.parent)

    @property
    def parents(self) -> Tuple:
        from poop.types.tuple import Tuple

        return Tuple(*(Path._from_pathlib(parent) for parent in self._path.parents))

    def __truediv__(self, other: Str | Path) -> Path:
        return Path._from_pathlib(self._path / Path._coerce_path(other))

    def __eq__(self, other: object) -> Boolean:
        if isinstance(other, Path):
            return true if self._path == other._path else false
        return false

    def __ne__(self, other: object) -> Boolean:
        if isinstance(other, Path):
            return false if self._path == other._path else true
        return true

    def __lt__(self, other: Path) -> Boolean:
        return true if self._path < other._path else false

    def __le__(self, other: Path) -> Boolean:
        return true if self._path <= other._path else false

    def __gt__(self, other: Path) -> Boolean:
        return true if self._path > other._path else false

    def __ge__(self, other: Path) -> Boolean:
        return true if self._path >= other._path else false

    def __hash__(self) -> int:
        return hash(self._path)

    def __str__(self) -> str:
        return str(self._path)

    __repr__ = __str__
