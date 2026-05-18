from __future__ import annotations

import shutil as _shutil
from collections.abc import Callable
from typing import Any, ClassVar, cast

from poop.types._bridge import bridge
from poop.types._unwrap import _b, _kwargs_from
from poop.types.block import Block
from poop.types.boolean import Boolean, false, true
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

    `ignore` (on `copytree`) and `copy_function` (on `copytree` /
    `move`) accept POOP `Block`s routed through `block.bridge`.
    `Shutil.ignore_patterns(*patterns)` returns a passthrough callable
    suitable for `ignore=`.
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
        symlinks: Boolean = false,
        ignore: Callable[..., Any] | None = None,
        copy_function: Callable[..., Any] | None = None,
        ignore_dangling_symlinks: Boolean = false,
        dirs_exist_ok: Boolean = false,
    ) -> Path:
        kwargs: dict[str, Any] = {}
        if ignore is not None:
            kwargs["ignore"] = bridge(ignore)
        if copy_function is not None:
            kwargs["copy_function"] = bridge(copy_function)
        return Path(
            Str(
                _shutil.copytree(
                    _path_arg(src),
                    _path_arg(dst),
                    symlinks=bool(symlinks),
                    ignore_dangling_symlinks=bool(ignore_dangling_symlinks),
                    dirs_exist_ok=bool(dirs_exist_ok),
                    **kwargs,
                )
            )
        )

    @staticmethod
    def ignore_patterns(*patterns: Str) -> Block:
        """Mirror of `shutil.ignore_patterns`, returning a POOP `Block`.

        Pass the result directly to `copytree(ignore=...)`. The block
        receives (path: Str, names: List[Str]) and returns the names
        to skip; `copytree`'s bridge layer unwraps/wraps at the
        boundary.
        """
        impl = _shutil.ignore_patterns(*(p._value for p in patterns))

        def adapter(path: Str, names: List) -> List:
            raw_names = [cast(Str, n)._value for n in names._items]
            ignored = impl(path._value, raw_names)
            return List(*(Str(n) for n in ignored))

        return Block(adapter)

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
    def move(
        src: Path | Str,
        dst: Path | Str,
        copy_function: Callable[..., Any] | None = None,
    ) -> Path:
        kwargs: dict[str, Any] = {}
        if copy_function is not None:
            kwargs["copy_function"] = bridge(copy_function)
        return Path(Str(_shutil.move(_path_arg(src), _path_arg(dst), **kwargs)))

    @staticmethod
    def rmtree(
        path: Path | Str,
        ignore_errors: Boolean = false,
        onerror: Any = None,
        *,
        onexc: Any = None,
        dir_fd: Int | None = None,
    ) -> NoneClass:
        kwargs: dict[str, Any] = {}
        if onerror is not None:
            kwargs["onerror"] = onerror
        if onexc is not None:
            kwargs["onexc"] = onexc
        if dir_fd is not None:
            kwargs["dir_fd"] = dir_fd._value
        _shutil.rmtree(_path_arg(path), ignore_errors=bool(ignore_errors), **kwargs)
        return none

    @staticmethod
    def which(
        cmd: Str,
        mode: Int | None = None,
        path: Str | None = None,
    ) -> Path | NoneClass:
        kwargs = _kwargs_from(mode=mode, path=path)
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
        verbose: Int = Int(0),
        dry_run: Int = Int(0),
        owner: Str | None = None,
        group: Str | None = None,
        logger: Any = None,
    ) -> Path:
        return Path(
            Str(
                _shutil.make_archive(
                    _path_arg(base_name),
                    format._value,
                    root_dir=_opt_path_arg(root_dir),
                    base_dir=_opt_path_arg(base_dir),
                    verbose=bool(verbose._value),
                    dry_run=bool(dry_run._value),
                    owner=None if owner is None else owner._value,
                    group=None if group is None else group._value,
                    logger=logger,
                )
            )
        )

    @staticmethod
    def unpack_archive(
        filename: Path | Str,
        extract_dir: Path | Str | None = None,
        format: Str | None = None,
        *,
        filter: Str | None = None,
    ) -> NoneClass:
        kwargs: dict[str, Any] = {}
        if extract_dir is not None:
            kwargs["extract_dir"] = _path_arg(extract_dir)
        if format is not None:
            kwargs["format"] = format._value
        if filter is not None:
            kwargs["filter"] = filter._value
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
        *,
        dir_fd: Int | None = None,
        follow_symlinks: Boolean = true,
    ) -> NoneClass:
        kwargs = _kwargs_from(user=user, group=group)
        if dir_fd is not None:
            kwargs["dir_fd"] = dir_fd._value
        kwargs["follow_symlinks"] = bool(follow_symlinks)
        _shutil.chown(_path_arg(path), **kwargs)
        return none
