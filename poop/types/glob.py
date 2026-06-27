import glob as _glob
from collections.abc import Iterator
from typing import TYPE_CHECKING

from poop.types._iterable_mixin import _IterableMixin
from poop.types._unwrap import _b
from poop.types.boolean import Boolean, false, to_boolean
from poop.types.list import List
from poop.types.path import Path
from poop.types.string import Str

if TYPE_CHECKING:
    pass


class GlobIter(_IterableMixin):
    """POOP iterator over a glob result.

    Wraps Python's `glob.iglob` generator and yields POOP `Path`
    objects on each `do(block)` call. Returned by `glob.iglob(...)`
    in POOP — matches the iterability of CPython's iglob without
    leaking the raw generator.
    """

    __slots__ = ("_gen",)

    def __init__(self, gen: Iterator[str]) -> None:
        self._gen = gen

    def __iter__(self) -> Iterator[Path]:
        for s in self._gen:
            yield Path(Str(s))

    def to_list(self) -> List:
        return List(*(Path(Str(s)) for s in self._gen))


class Glob:
    """Namespace mirroring Python's `glob` module.

    `Path.glob`/`Path.rglob` already cover most use; this namespace
    surfaces the module-level functions for callers who want to
    glob from a string pattern without first constructing a `Path`.
    """

    @staticmethod
    def glob(
        pathname: Str,
        *,
        root_dir: Path | Str | None = None,
        recursive: Boolean = false,
        include_hidden: Boolean = false,
    ) -> List:
        rd: str | None
        if root_dir is None:
            rd = None
        elif isinstance(root_dir, Path):
            rd = str(root_dir._path)
        else:
            rd = root_dir._value
        results = _glob.glob(
            pathname._value,
            root_dir=rd,
            recursive=bool(recursive),
            include_hidden=bool(include_hidden),
        )
        return List(*(Path(Str(s)) for s in results))

    @staticmethod
    def iglob(
        pathname: Str,
        *,
        root_dir: Path | Str | None = None,
        recursive: Boolean = false,
        include_hidden: Boolean = false,
    ) -> GlobIter:
        rd: str | None
        if root_dir is None:
            rd = None
        elif isinstance(root_dir, Path):
            rd = str(root_dir._path)
        else:
            rd = root_dir._value
        gen = _glob.iglob(
            pathname._value,
            root_dir=rd,
            recursive=bool(recursive),
            include_hidden=bool(include_hidden),
        )
        return GlobIter(iter(gen))

    @staticmethod
    def escape(pathname: Str) -> Str:
        return Str(_glob.escape(pathname._value))

    @staticmethod
    def translate(
        pat: Str,
        *,
        recursive: Boolean | None = None,
        include_hidden: Boolean | None = None,
        seps: Str | None = None,
    ) -> Str:
        seps_value = None if seps is None else seps._value
        return Str(
            _glob.translate(
                pat._value,
                recursive=_b(recursive, False),
                include_hidden=_b(include_hidden, False),
                seps=seps_value,
            )
        )

    @staticmethod
    def has_magic(s: Str) -> Boolean:
        """Return `true` when `s` contains glob metacharacters."""
        return to_boolean(_glob.has_magic(s._value))
