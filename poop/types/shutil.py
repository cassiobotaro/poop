from __future__ import annotations

import shutil as _shutil
from typing import Any, ClassVar

from poop.types._unwrap import _b
from poop.types.boolean import Boolean
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import NoneClass, none
from poop.types.path import Path
from poop.types.string import Str
from poop.types.tuple import Tuple


def _path_arg(value: Path | Str) -> str:
    if isinstance(value, Path):
        return str(value._path)
    return value._value


def _opt_path_arg(value: Path | Str | None) -> str | None:
    return None if value is None else _path_arg(value)


def _format_pairs(pairs: list[tuple[str, str]]) -> List:
    return List(*(Tuple(Str(name), Str(desc)) for name, desc in pairs))


class Shutil:
    """Namespace mirroring Python's `shutil` module.

    Covers the high-level file/directory surface: copy/move/remove
    trees, archive create/extract, disk and terminal info. Paths
    accept either `Path` or `Str` everywhere; return values are `Path`
    when CPython returns a path-like.

    The `ignore_patterns` factory and the `copy_function` callback
    argument plumbing are out of scope for v1 — defer until POOP has
    a Block↔callable bridge.
    """

    Error: ClassVar[type[Exception]] = _shutil.Error
    SameFileError: ClassVar[type[Exception]] = _shutil.SameFileError

    # Copy --------------------------------------------------------------

    @staticmethod
    def copy(
        src: Path | Str,
        dst: Path | Str,
        follow_symlinks: Boolean | None = None,
    ) -> Path:
        return Path(
            Str(
                _shutil.copy(
                    _path_arg(src),
                    _path_arg(dst),
                    follow_symlinks=_b(follow_symlinks, True),
                )
            )
        )

    @staticmethod
    def copy2(
        src: Path | Str,
        dst: Path | Str,
        follow_symlinks: Boolean | None = None,
    ) -> Path:
        return Path(
            Str(
                _shutil.copy2(
                    _path_arg(src),
                    _path_arg(dst),
                    follow_symlinks=_b(follow_symlinks, True),
                )
            )
        )

    @staticmethod
    def copyfile(
        src: Path | Str,
        dst: Path | Str,
        follow_symlinks: Boolean | None = None,
    ) -> Path:
        return Path(
            Str(
                _shutil.copyfile(
                    _path_arg(src),
                    _path_arg(dst),
                    follow_symlinks=_b(follow_symlinks, True),
                )
            )
        )

    @staticmethod
    def copytree(
        src: Path | Str,
        dst: Path | Str,
        symlinks: Boolean | None = None,
        ignore_dangling_symlinks: Boolean | None = None,
        dirs_exist_ok: Boolean | None = None,
    ) -> Path:
        return Path(
            Str(
                _shutil.copytree(
                    _path_arg(src),
                    _path_arg(dst),
                    symlinks=_b(symlinks, False),
                    ignore_dangling_symlinks=_b(ignore_dangling_symlinks, False),
                    dirs_exist_ok=_b(dirs_exist_ok, False),
                )
            )
        )

    @staticmethod
    def copymode(
        src: Path | Str,
        dst: Path | Str,
        follow_symlinks: Boolean | None = None,
    ) -> NoneClass:
        _shutil.copymode(
            _path_arg(src),
            _path_arg(dst),
            follow_symlinks=_b(follow_symlinks, True),
        )
        return none

    @staticmethod
    def copystat(
        src: Path | Str,
        dst: Path | Str,
        follow_symlinks: Boolean | None = None,
    ) -> NoneClass:
        _shutil.copystat(
            _path_arg(src),
            _path_arg(dst),
            follow_symlinks=_b(follow_symlinks, True),
        )
        return none

    # Move / remove -----------------------------------------------------

    @staticmethod
    def move(src: Path | Str, dst: Path | Str) -> Path:
        return Path(Str(_shutil.move(_path_arg(src), _path_arg(dst))))

    @staticmethod
    def rmtree(
        path: Path | Str,
        ignore_errors: Boolean | None = None,
    ) -> NoneClass:
        _shutil.rmtree(_path_arg(path), ignore_errors=_b(ignore_errors, False))
        return none

    @staticmethod
    def which(
        cmd: Str,
        mode: Int | None = None,
        path: Str | None = None,
    ) -> Path | NoneClass:
        kwargs: dict[str, Any] = {}
        if mode is not None:
            kwargs["mode"] = mode._value
        if path is not None:
            kwargs["path"] = path._value
        result = _shutil.which(cmd._value, **kwargs)
        if result is None:
            return none
        return Path(Str(result))

    # Archives ----------------------------------------------------------

    @staticmethod
    def make_archive(
        base_name: Path | Str,
        format: Str,
        root_dir: Path | Str | None = None,
        base_dir: Path | Str | None = None,
    ) -> Path:
        return Path(
            Str(
                _shutil.make_archive(
                    _path_arg(base_name),
                    format._value,
                    root_dir=_opt_path_arg(root_dir),
                    base_dir=_opt_path_arg(base_dir),
                )
            )
        )

    @staticmethod
    def unpack_archive(
        filename: Path | Str,
        extract_dir: Path | Str | None = None,
        format: Str | None = None,
    ) -> NoneClass:
        kwargs: dict[str, Any] = {}
        if extract_dir is not None:
            kwargs["extract_dir"] = _path_arg(extract_dir)
        if format is not None:
            kwargs["format"] = format._value
        _shutil.unpack_archive(_path_arg(filename), **kwargs)
        return none

    @staticmethod
    def get_archive_formats() -> List:
        return _format_pairs(_shutil.get_archive_formats())

    @staticmethod
    def get_unpack_formats() -> List:
        # `get_unpack_formats` returns 3-tuples (name, extensions, desc).
        return List(
            *(
                Tuple(
                    Str(name),
                    List(*(Str(e) for e in extensions)),
                    Str(desc),
                )
                for name, extensions, desc in _shutil.get_unpack_formats()
            )
        )

    # Disk / terminal --------------------------------------------------

    @staticmethod
    def disk_usage(path: Path | Str) -> Tuple:
        usage = _shutil.disk_usage(_path_arg(path))
        return Tuple(Int(usage.total), Int(usage.used), Int(usage.free))

    @staticmethod
    def get_terminal_size(fallback: Tuple | None = None) -> Tuple:
        kwargs: dict[str, Any] = {}
        if fallback is not None:
            cols: Any = fallback.at(Int(0))
            lines: Any = fallback.at(Int(1))
            kwargs["fallback"] = (cols._value, lines._value)
        size = _shutil.get_terminal_size(**kwargs)
        return Tuple(Int(size.columns), Int(size.lines))

    @staticmethod
    def chown(
        path: Path | Str,
        user: Str | Int | None = None,
        group: Str | Int | None = None,
    ) -> NoneClass:
        kwargs: dict[str, Any] = {}
        if user is not None:
            kwargs["user"] = user._value
        if group is not None:
            kwargs["group"] = group._value
        _shutil.chown(_path_arg(path), **kwargs)
        return none
