from __future__ import annotations

import configparser as _configparser
import io as _io
from typing import Any, ClassVar

from poop.types._unwrap import _b
from poop.types.boolean import Boolean, false, true
from poop.types.dict import Dict
from poop.types.float import Float
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import NoneClass, none
from poop.types.object import Object
from poop.types.path import Path
from poop.types.string import Str
from poop.types.tuple import Tuple


def _opt_str(value: Str | None, default: str | None) -> str | None:
    return default if value is None else value._value


def _path_str(value: Path | Str) -> str:
    if isinstance(value, Path):
        return str(value._path)
    return value._value


_DEFAULT = object()


class ConfigParser(Object):
    """Wraps Python's `configparser.ConfigParser` — INI-style config
    files.

    The `read*` family loads from files/strings/dicts; `get*` /
    `items` queries; `add_section` / `set` / `remove_*` mutates;
    `write` serializes back. Typed accessors (`getint` / `getfloat` /
    `getboolean`) return wrapped POOP types.
    """

    __slots__ = ("_impl",)

    def __init__(
        self,
        defaults: Dict | None = None,
        allow_no_value: Boolean | None = None,
        delimiters: Tuple | None = None,
        comment_prefixes: Tuple | None = None,
        inline_comment_prefixes: Tuple | None = None,
        strict: Boolean | None = None,
        empty_lines_in_values: Boolean | None = None,
        default_section: Str | None = None,
        interpolation: Any = None,
    ) -> None:
        kwargs: dict[str, Any] = {}
        if defaults is not None:
            kwargs["defaults"] = {
                (k._value if isinstance(k, Str) else k): (
                    v._value if isinstance(v, Str) else v
                )
                for k, v in defaults._data.items()
            }
        if allow_no_value is not None:
            kwargs["allow_no_value"] = bool(allow_no_value)
        if delimiters is not None:
            kwargs["delimiters"] = tuple(
                d._value if isinstance(d, Str) else d for d in delimiters
            )
        if comment_prefixes is not None:
            kwargs["comment_prefixes"] = tuple(
                p._value if isinstance(p, Str) else p for p in comment_prefixes
            )
        if inline_comment_prefixes is not None:
            kwargs["inline_comment_prefixes"] = tuple(
                p._value if isinstance(p, Str) else p for p in inline_comment_prefixes
            )
        if strict is not None:
            kwargs["strict"] = bool(strict)
        if empty_lines_in_values is not None:
            kwargs["empty_lines_in_values"] = bool(empty_lines_in_values)
        if default_section is not None:
            kwargs["default_section"] = default_section._value
        if interpolation is not None:
            kwargs["interpolation"] = interpolation
        self._impl = _configparser.ConfigParser(**kwargs)

    @classmethod
    def _from_impl(cls, impl: Any) -> ConfigParser:
        obj = cls.__new__(cls)
        obj._impl = impl
        return obj

    # Reading -----------------------------------------------------------

    def read(self, filenames: Path | Str | List, encoding: Str | None = None) -> List:
        kwargs: dict[str, Any] = {}
        if encoding is not None:
            kwargs["encoding"] = encoding._value
        paths: Any
        if isinstance(filenames, List):
            paths = []
            for f in filenames:
                if not isinstance(f, Path | Str):
                    raise TypeError(
                        f"read filenames must be Path or Str, got {type(f).__name__}"
                    )
                paths.append(_path_str(f))
        else:
            paths = _path_str(filenames)
        read_files = self._impl.read(paths, **kwargs)
        return List(*(Str(f if isinstance(f, str) else str(f)) for f in read_files))

    def read_string(self, string: Str, source: Str | None = None) -> NoneClass:
        self._impl.read_string(
            string._value, _opt_str(source, "<string>") or "<string>"
        )
        return none

    def read_dict(self, dictionary: Dict, source: Str | None = None) -> NoneClass:
        py_dict: dict[Any, Any] = {}
        for section, options in dictionary._data.items():
            section_name: Any = section._value if isinstance(section, Str) else section
            opts: dict[Any, Any] = {}
            if isinstance(options, Dict):
                for k, v in options._data.items():
                    key: Any = k._value if isinstance(k, Str) else k
                    val: Any
                    if isinstance(v, Str | Int | Float):
                        val = v._value
                    elif isinstance(v, Boolean):
                        val = bool(v)
                    else:
                        val = v
                    opts[key] = val
            py_dict[section_name] = opts
        self._impl.read_dict(py_dict, _opt_str(source, "<dict>") or "<dict>")
        return none

    def read_file(
        self, source: Str | List, source_name: Str | None = None
    ) -> NoneClass:
        if isinstance(source, Str):
            handle: Any = _io.StringIO(source._value)
        else:
            lines: list[str] = []
            for s in source:
                if not isinstance(s, Str):
                    raise TypeError(
                        f"read_file List entries must be Str, got {type(s).__name__}"
                    )
                lines.append(s._value)
            handle = iter(lines)
        if source_name is None:
            self._impl.read_file(handle)
        else:
            self._impl.read_file(handle, source_name._value)
        return none

    # Querying ----------------------------------------------------------

    def sections(self) -> List:
        return List(*(Str(s) for s in self._impl.sections()))

    def has_section(self, section: Str) -> Boolean:
        return true if self._impl.has_section(section._value) else false

    def options(self, section: Str) -> List:
        return List(*(Str(o) for o in self._impl.options(section._value)))

    def has_option(self, section: Str, option: Str) -> Boolean:
        return true if self._impl.has_option(section._value, option._value) else false

    def items(self, section: Str | None = None) -> List:
        if section is None:
            return List(
                *(
                    Tuple(Str(name), self._wrap_section_proxy(proxy))
                    for name, proxy in self._impl.items()
                )
            )
        return List(
            *(Tuple(Str(k), Str(v)) for k, v in self._impl.items(section._value))
        )

    @staticmethod
    def _wrap_section_proxy(proxy: Any) -> Dict:
        result = Dict()
        for k, v in proxy.items():
            result.at_put(Str(k), Str(v))
        return result

    def get(
        self,
        section: Str,
        option: Str,
        raw: Boolean | None = None,
        fallback: Any = _DEFAULT,
    ) -> Str:
        kwargs: dict[str, Any] = {"raw": _b(raw, False)}
        if fallback is not _DEFAULT:
            kwargs["fallback"] = (
                fallback._value if isinstance(fallback, Str) else fallback
            )
        return Str(self._impl.get(section._value, option._value, **kwargs))

    def getint(
        self,
        section: Str,
        option: Str,
        raw: Boolean | None = None,
        fallback: Any = _DEFAULT,
    ) -> Int:
        kwargs: dict[str, Any] = {"raw": _b(raw, False)}
        if fallback is not _DEFAULT:
            kwargs["fallback"] = (
                fallback._value if isinstance(fallback, Int) else fallback
            )
        return Int(self._impl.getint(section._value, option._value, **kwargs))

    def getfloat(
        self,
        section: Str,
        option: Str,
        raw: Boolean | None = None,
        fallback: Any = _DEFAULT,
    ) -> Float:
        kwargs: dict[str, Any] = {"raw": _b(raw, False)}
        if fallback is not _DEFAULT:
            kwargs["fallback"] = (
                fallback._value if isinstance(fallback, Float) else fallback
            )
        return Float(self._impl.getfloat(section._value, option._value, **kwargs))

    def getboolean(
        self,
        section: Str,
        option: Str,
        raw: Boolean | None = None,
        fallback: Any = _DEFAULT,
    ) -> Boolean:
        kwargs: dict[str, Any] = {"raw": _b(raw, False)}
        if fallback is not _DEFAULT:
            kwargs["fallback"] = (
                bool(fallback) if isinstance(fallback, Boolean) else fallback
            )
        result = self._impl.getboolean(section._value, option._value, **kwargs)
        return true if result else false

    def defaults(self) -> Dict:
        result = Dict()
        for k, v in self._impl.defaults().items():
            result.at_put(Str(k), Str(v))
        return result

    # Mutating ----------------------------------------------------------

    def add_section(self, section: Str) -> NoneClass:
        self._impl.add_section(section._value)
        return none

    def remove_section(self, section: Str) -> Boolean:
        return true if self._impl.remove_section(section._value) else false

    def set(self, section: Str, option: Str, value: Str) -> NoneClass:
        self._impl.set(section._value, option._value, value._value)
        return none

    def remove_option(self, section: Str, option: Str) -> Boolean:
        return (
            true if self._impl.remove_option(section._value, option._value) else false
        )

    def clear(self) -> NoneClass:
        self._impl.clear()
        return none

    # Writing -----------------------------------------------------------

    def write_to(
        self,
        path: Path | Str,
        space_around_delimiters: Boolean | None = None,
    ) -> NoneClass:
        kwargs: dict[str, Any] = {}
        kwargs["space_around_delimiters"] = _b(space_around_delimiters, True)
        with open(_path_str(path), "w", encoding="utf-8") as f:
            self._impl.write(f, **kwargs)
        return none

    def write_str(self, space_around_delimiters: Boolean | None = None) -> Str:
        buf = _io.StringIO()
        self._impl.write(buf, space_around_delimiters=_b(space_around_delimiters, True))
        return Str(buf.getvalue())


class RawConfigParser(ConfigParser):
    """Wraps Python's `configparser.RawConfigParser` — no interpolation."""

    def __init__(self) -> None:  # type: ignore[override]
        # Bypass the parent __init__ so we instantiate the Raw variant
        # directly with default settings. Advanced configuration of
        # RawConfigParser is deferred to a follow-up proposal.
        self._impl = _configparser.RawConfigParser()


class Configparser:
    """Namespace mirroring Python's `configparser` module.

    `ConfigParser` is the default parser; `RawConfigParser` skips
    interpolation. The two interpolation classes
    (`BasicInterpolation`, `ExtendedInterpolation`) are re-exported
    as raw Python class refs.
    """

    ConfigParser: ClassVar[type[ConfigParser]] = ConfigParser
    RawConfigParser: ClassVar[type[RawConfigParser]] = RawConfigParser

    BasicInterpolation: ClassVar[type[Any]] = _configparser.BasicInterpolation
    ExtendedInterpolation: ClassVar[type[Any]] = _configparser.ExtendedInterpolation

    # Error hierarchy.
    Error: ClassVar[type[Exception]] = _configparser.Error
    NoSectionError: ClassVar[type[Exception]] = _configparser.NoSectionError
    DuplicateSectionError: ClassVar[type[Exception]] = (
        _configparser.DuplicateSectionError
    )
    NoOptionError: ClassVar[type[Exception]] = _configparser.NoOptionError
    DuplicateOptionError: ClassVar[type[Exception]] = _configparser.DuplicateOptionError
    InterpolationError: ClassVar[type[Exception]] = _configparser.InterpolationError
    InterpolationDepthError: ClassVar[type[Exception]] = (
        _configparser.InterpolationDepthError
    )
    InterpolationMissingOptionError: ClassVar[type[Exception]] = (
        _configparser.InterpolationMissingOptionError
    )
    InterpolationSyntaxError: ClassVar[type[Exception]] = (
        _configparser.InterpolationSyntaxError
    )
    ParsingError: ClassVar[type[Exception]] = _configparser.ParsingError
    MissingSectionHeaderError: ClassVar[type[Exception]] = (
        _configparser.MissingSectionHeaderError
    )
