from pathlib import Path as _PyPath

import pytest

from poop.interpreter import Interpreter
from poop.types.boolean import false, true
from poop.types.configparser import ConfigParser, Configparser, RawConfigParser
from poop.types.dict import Dict
from poop.types.float import Float
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import none
from poop.types.path import Path
from poop.types.string import Str
from poop.types.tuple import Tuple


def _make_loaded() -> ConfigParser:
    cp = ConfigParser()
    cp.read_string(
        Str(
            "[section]\nkey = value\nint_opt = 42\nfloat_opt = 3.14\n"
            "bool_opt = yes\n\n[other]\nname = poop\n"
        )
    )
    return cp


# --- read_string / read_dict / read_file ---


def test_read_string_loads_sections() -> None:
    cp = _make_loaded()
    assert cp.sections() == List(Str("section"), Str("other"))


def test_read_dict_loads_options() -> None:
    cp = ConfigParser()
    cp.read_dict(Dict().at_put(Str("s"), Dict().at_put(Str("k"), Str("v"))))
    assert cp.get(Str("s"), Str("k")) == Str("v")


def test_read_dict_with_typed_values() -> None:
    cp = ConfigParser()
    cp.read_dict(
        Dict().at_put(
            Str("s"),
            Dict()
            .at_put(Str("n"), Int(7))
            .at_put(Str("f"), Float(2.5))
            .at_put(Str("b"), true),
        )
    )
    assert cp.getint(Str("s"), Str("n")) == Int(7)


def test_read_file_from_str() -> None:
    cp = ConfigParser()
    cp.read_file(Str("[a]\nk=v\n"))
    assert cp.has_section(Str("a")) is true


def test_read_file_from_list() -> None:
    cp = ConfigParser()
    cp.read_file(List(Str("[a]\n"), Str("k=v\n")))
    assert cp.get(Str("a"), Str("k")) == Str("v")


def test_read_file_with_source_name() -> None:
    cp = ConfigParser()
    cp.read_file(Str("[a]\nk=v\n"), Str("inline"))
    assert cp.has_option(Str("a"), Str("k")) is true


def test_read_from_path(tmp_path: _PyPath) -> None:
    cfg = tmp_path / "x.ini"
    cfg.write_text("[s]\nkey = file-value\n")
    cp = ConfigParser()
    result = cp.read(Path(Str(str(cfg))))
    assert isinstance(result, List)
    assert cp.get(Str("s"), Str("key")) == Str("file-value")


def test_read_from_list_of_paths(tmp_path: _PyPath) -> None:
    cfg1 = tmp_path / "a.ini"
    cfg1.write_text("[a]\nx=1\n")
    cfg2 = tmp_path / "b.ini"
    cfg2.write_text("[b]\ny=2\n")
    cp = ConfigParser()
    cp.read(List(Path(Str(str(cfg1))), Path(Str(str(cfg2)))))
    assert cp.has_section(Str("a")) is true
    assert cp.has_section(Str("b")) is true


def test_read_with_encoding(tmp_path: _PyPath) -> None:
    cfg = tmp_path / "u.ini"
    cfg.write_text("[s]\nname=café\n", encoding="utf-8")
    cp = ConfigParser()
    cp.read(Path(Str(str(cfg))), encoding=Str("utf-8"))
    assert cp.get(Str("s"), Str("name")) == Str("café")


# --- Querying ---


def test_options() -> None:
    cp = _make_loaded()
    opts = cp.options(Str("section"))
    assert opts.includes(Str("key"))
    assert opts.includes(Str("int_opt"))


def test_has_section() -> None:
    cp = _make_loaded()
    assert cp.has_section(Str("section")) is true
    assert cp.has_section(Str("missing")) is false


def test_has_option() -> None:
    cp = _make_loaded()
    assert cp.has_option(Str("section"), Str("key")) is true
    assert cp.has_option(Str("section"), Str("nope")) is false


def test_items_for_section() -> None:
    cp = _make_loaded()
    items = cp.items(Str("section"))
    assert isinstance(items, List)
    # First item is Tuple[Str, Str].
    first = items.at(Int(0))
    assert isinstance(first, Tuple)
    assert isinstance(first.at(Int(0)), Str)


def test_items_no_args_returns_all_sections() -> None:
    cp = _make_loaded()
    items = cp.items()
    assert isinstance(items, List)
    pair = items.at(Int(0))
    assert isinstance(pair, Tuple)
    assert isinstance(pair.at(Int(1)), Dict)


def test_get() -> None:
    cp = _make_loaded()
    assert cp.get(Str("section"), Str("key")) == Str("value")


def test_get_with_fallback() -> None:
    cp = _make_loaded()
    assert cp.get(Str("section"), Str("missing"), fallback=Str("default")) == Str(
        "default"
    )


def test_getint() -> None:
    cp = _make_loaded()
    assert cp.getint(Str("section"), Str("int_opt")) == Int(42)


def test_getint_with_fallback() -> None:
    cp = _make_loaded()
    assert cp.getint(Str("section"), Str("missing"), fallback=Int(99)) == Int(99)


def test_getfloat() -> None:
    cp = _make_loaded()
    assert cp.getfloat(Str("section"), Str("float_opt")) == Float(3.14)


def test_getfloat_with_fallback() -> None:
    cp = _make_loaded()
    assert cp.getfloat(Str("section"), Str("missing"), fallback=Float(0.0)) == Float(
        0.0
    )


def test_getboolean() -> None:
    cp = _make_loaded()
    assert cp.getboolean(Str("section"), Str("bool_opt")) is true


def test_getboolean_with_fallback() -> None:
    cp = _make_loaded()
    assert cp.getboolean(Str("section"), Str("missing"), fallback=false) is false


def test_get_raw() -> None:
    cp = ConfigParser()
    cp.read_string(Str("[s]\nv = %(other)s\nother = x\n"))
    assert cp.get(Str("s"), Str("v"), raw=true) == Str("%(other)s")


def test_defaults_returns_dict() -> None:
    cp = ConfigParser(defaults=Dict().at_put(Str("default_key"), Str("dv")))
    defaults = cp.defaults()
    assert isinstance(defaults, Dict)
    assert defaults.at(Str("default_key")) == Str("dv")


# --- Mutating ---


def test_add_section() -> None:
    cp = ConfigParser()
    assert cp.add_section(Str("new")) is none
    assert cp.has_section(Str("new")) is true


def test_remove_section() -> None:
    cp = _make_loaded()
    assert cp.remove_section(Str("section")) is true
    assert cp.has_section(Str("section")) is false


def test_remove_section_missing() -> None:
    cp = ConfigParser()
    assert cp.remove_section(Str("nope")) is false


def test_set() -> None:
    cp = _make_loaded()
    cp.set(Str("section"), Str("key"), Str("new-value"))
    assert cp.get(Str("section"), Str("key")) == Str("new-value")


def test_remove_option() -> None:
    cp = _make_loaded()
    assert cp.remove_option(Str("section"), Str("key")) is true
    assert cp.has_option(Str("section"), Str("key")) is false


def test_clear() -> None:
    cp = _make_loaded()
    cp.clear()
    assert cp.sections() == List()


# --- Writing ---


def test_write_str() -> None:
    cp = _make_loaded()
    out = cp.write_str()
    assert isinstance(out, Str)
    assert "[section]" in out._value
    assert "key = value" in out._value


def test_write_to_path(tmp_path: _PyPath) -> None:
    cfg = tmp_path / "out.ini"
    cp = _make_loaded()
    cp.write_to(Path(Str(str(cfg))))
    contents = cfg.read_text()
    assert "[section]" in contents


def test_write_str_compact() -> None:
    cp = _make_loaded()
    out = cp.write_str(space_around_delimiters=false)
    assert "key=value" in out._value


# --- Construction kwargs ---


def test_constructor_with_defaults() -> None:
    cp = ConfigParser(defaults=Dict().at_put(Str("k"), Str("v")))
    cp.read_string(Str("[s]\n\n"))
    assert cp.get(Str("s"), Str("k")) == Str("v")


def test_constructor_allow_no_value() -> None:
    cp = ConfigParser(allow_no_value=true)
    cp.read_string(Str("[s]\nflag\n"))
    assert cp.has_option(Str("s"), Str("flag")) is true


def test_constructor_delimiters() -> None:
    cp = ConfigParser(delimiters=Tuple(Str("=")))
    cp.read_string(Str("[s]\nk = v\n"))
    assert cp.get(Str("s"), Str("k")) == Str("v")


def test_constructor_comment_prefixes() -> None:
    cp = ConfigParser(comment_prefixes=Tuple(Str("#")))
    cp.read_string(Str("[s]\n# this is a comment\nk = v\n"))
    assert cp.get(Str("s"), Str("k")) == Str("v")


def test_constructor_inline_comment_prefixes() -> None:
    cp = ConfigParser(inline_comment_prefixes=Tuple(Str(";")))
    cp.read_string(Str("[s]\nk = v ; trailing\n"))
    assert cp.get(Str("s"), Str("k")) == Str("v")


def test_constructor_strict_false_allows_duplicates() -> None:
    cp = ConfigParser(strict=false)
    cp.read_string(Str("[s]\nk = a\nk = b\n"))
    # In non-strict mode, the second value wins.
    assert cp.get(Str("s"), Str("k")) == Str("b")


def test_constructor_empty_lines_in_values_false() -> None:
    cp = ConfigParser(empty_lines_in_values=false)
    cp.read_string(Str("[s]\nk = first\n\nk2 = next\n"))
    assert cp.has_option(Str("s"), Str("k")) is true


def test_constructor_default_section() -> None:
    cp = ConfigParser(default_section=Str("GLOBAL"))
    cp.read_string(Str("[GLOBAL]\nshared = yes\n[a]\n"))
    assert cp.has_option(Str("a"), Str("shared")) is true


def test_constructor_with_interpolation() -> None:
    cp = ConfigParser(interpolation=Configparser.ExtendedInterpolation())
    cp.read_string(Str("[s]\nbase = root\nfull = ${base}/sub\n"))
    assert cp.get(Str("s"), Str("full")) == Str("root/sub")


# --- RawConfigParser ---


def test_raw_config_parser_no_interpolation() -> None:
    cp = RawConfigParser()
    cp.read_string(Str("[s]\nv = %(no_ref)s\n"))
    assert cp.get(Str("s"), Str("v")) == Str("%(no_ref)s")


# --- Error hierarchy ---


def test_error_classes_exposed() -> None:
    assert issubclass(Configparser.NoSectionError, Configparser.Error)
    assert issubclass(Configparser.NoOptionError, Configparser.Error)
    assert issubclass(Configparser.DuplicateSectionError, Configparser.Error)
    assert issubclass(Configparser.DuplicateOptionError, Configparser.Error)
    assert issubclass(Configparser.InterpolationError, Configparser.Error)
    assert issubclass(
        Configparser.InterpolationDepthError, Configparser.InterpolationError
    )
    assert issubclass(
        Configparser.InterpolationMissingOptionError, Configparser.InterpolationError
    )
    assert issubclass(
        Configparser.InterpolationSyntaxError, Configparser.InterpolationError
    )
    assert issubclass(Configparser.ParsingError, Configparser.Error)
    assert issubclass(Configparser.MissingSectionHeaderError, Configparser.ParsingError)


def test_no_section_error_raised() -> None:
    cp = ConfigParser()
    with pytest.raises(Configparser.NoSectionError):
        cp.options(Str("missing"))


def test_no_option_error_raised() -> None:
    cp = _make_loaded()
    with pytest.raises(Configparser.NoOptionError):
        cp.get(Str("section"), Str("missing"))


# --- Interpolation class refs ---


def test_interpolation_classes_exposed() -> None:
    assert Configparser.BasicInterpolation is not None
    assert Configparser.ExtendedInterpolation is not None


# --- Interpreter integration ---


def test_configparser_via_interpreter() -> None:
    Interpreter().run_source(
        'cp = ConfigParser()\ncp.read_string("[s]\\nk=v\\n")\ncp.get("s", "k").print()'
    )


def test_configparser_namespace_via_interpreter() -> None:
    Interpreter().run_source(
        'cp = configparser.ConfigParser()\ncp.read_string("[s]\\nk=v\\n")\n'
        "cp.sections().print()"
    )


def test_configparser_max_interpolation_depth_is_int() -> None:
    import configparser as _stdlib_cp

    from poop.types.int import Int

    assert isinstance(Configparser.MAX_INTERPOLATION_DEPTH, Int)
    assert Configparser.MAX_INTERPOLATION_DEPTH == Int(
        _stdlib_cp.MAX_INTERPOLATION_DEPTH
    )
