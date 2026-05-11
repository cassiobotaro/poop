import pathlib as _pathlib
from typing import TYPE_CHECKING, ClassVar

from poop.types._value_eq import _ValueEqMixin
from poop.types.boolean import false, true
from poop.types.object import Object

if TYPE_CHECKING:
    from poop.types.boolean import Boolean
    from poop.types.bytes import Bytes
    from poop.types.int import Int
    from poop.types.map import Map
    from poop.types.none import NoneClass
    from poop.types.path_iterator import PathIterator
    from poop.types.string import Str
    from poop.types.tuple import Tuple


class Path(_ValueEqMixin, Object):
    __slots__ = ("_path",)
    _eq_attr: ClassVar[str] = "_path"

    def __init__(self, path: Str | Path) -> None:
        if isinstance(path, Path):
            self._path = path._path
        else:
            self._path = _pathlib.Path(path._value)

    @classmethod
    def _from_pathlib(cls, p: _pathlib.Path) -> Path:
        obj = cls.__new__(cls)
        obj._path = p
        return obj

    @classmethod
    def cwd(cls) -> Path:
        return cls._from_pathlib(_pathlib.Path.cwd())

    @classmethod
    def home(cls) -> Path:
        return cls._from_pathlib(_pathlib.Path.home())

    def read_text(self) -> Str:
        from poop.types.string import Str

        return Str(self._path.read_text(encoding="utf-8"))

    def write_text(self, content: Str) -> Int:
        from poop.types.int import Int

        return Int(self._path.write_text(content._value, encoding="utf-8"))

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
        self,
        mode: Int | NoneClass | None = None,
        parents: Boolean | NoneClass | None = None,
        exist_ok: Boolean | NoneClass | None = None,
    ) -> NoneClass:
        from poop.types._unwrap import _unwrap, _unwrap_bool
        from poop.types.none import none

        self._path.mkdir(
            mode=_unwrap(mode, 0o777),
            parents=_unwrap_bool(parents, False),
            exist_ok=_unwrap_bool(exist_ok, False),
        )
        return none

    def rmdir(self) -> NoneClass:
        from poop.types.none import none

        self._path.rmdir()
        return none

    def unlink(self, missing_ok: Boolean | NoneClass | None = None) -> NoneClass:
        from poop.types._unwrap import _unwrap_bool
        from poop.types.none import none

        self._path.unlink(missing_ok=_unwrap_bool(missing_ok, False))
        return none

    def touch(
        self,
        mode: Int | NoneClass | None = None,
        exist_ok: Boolean | NoneClass | None = None,
    ) -> NoneClass:
        from poop.types._unwrap import _unwrap, _unwrap_bool
        from poop.types.none import none

        self._path.touch(
            mode=_unwrap(mode, 0o666),
            exist_ok=_unwrap_bool(exist_ok, True),
        )
        return none

    def resolve(self) -> Path:
        return Path._from_pathlib(self._path.resolve())

    def absolute(self) -> Path:
        return Path._from_pathlib(self._path.absolute())

    def rename(self, target: Str | Path) -> Path:
        target_p = (
            target._path if isinstance(target, Path) else _pathlib.Path(target._value)
        )
        return Path._from_pathlib(self._path.rename(target_p))

    def replace(self, target: Str | Path) -> Path:
        target_p = (
            target._path if isinstance(target, Path) else _pathlib.Path(target._value)
        )
        return Path._from_pathlib(self._path.replace(target_p))

    def joinpath(self, *others: Str | Path) -> Path:
        parts = [o._path if isinstance(o, Path) else o._value for o in others]
        return Path._from_pathlib(self._path.joinpath(*parts))

    def with_name(self, name: Str) -> Path:
        return Path._from_pathlib(self._path.with_name(name._value))

    def with_suffix(self, suffix: Str) -> Path:
        return Path._from_pathlib(self._path.with_suffix(suffix._value))

    def with_stem(self, stem: Str) -> Path:
        return Path._from_pathlib(self._path.with_stem(stem._value))

    def relative_to(self, other: Str | Path) -> Path:
        target = other._path if isinstance(other, Path) else _pathlib.Path(other._value)
        return Path._from_pathlib(self._path.relative_to(target))

    def as_posix(self) -> Str:
        from poop.types.string import Str

        return Str(self._path.as_posix())

    def as_uri(self) -> Str:
        from poop.types.string import Str

        return Str(self._path.as_uri())

    def iterdir(self) -> PathIterator:
        from poop.types.path_iterator import PathIterator

        return PathIterator(self._path.iterdir())

    def glob(self, pattern: Str) -> Map:
        from poop.types.map import Map

        return Map(self._path.glob(pattern._value), Path._from_pathlib)

    def rglob(self, pattern: Str) -> Map:
        from poop.types.map import Map

        return Map(self._path.rglob(pattern._value), Path._from_pathlib)

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

        return Tuple(*[Str(p) for p in self._path.parts])

    @property
    def parent(self) -> Path:
        return Path._from_pathlib(self._path.parent)

    @property
    def parents(self) -> Tuple:
        from poop.types.tuple import Tuple

        return Tuple(*[Path._from_pathlib(p) for p in self._path.parents])

    def __truediv__(self, other: Str | Path) -> Path:
        target = other._path if isinstance(other, Path) else other._value
        return Path._from_pathlib(self._path / target)

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

    def __repr__(self) -> str:
        return f"Path({str(self._path)!r})"
