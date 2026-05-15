from poop.interpreter import Interpreter
from poop.types.boolean import false, true
from poop.types.dict import Dict
from poop.types.list import List
from poop.types.mimetypes import MimeTypes, Mimetypes
from poop.types.none import NoneClass, none
from poop.types.string import Str
from poop.types.tuple import Tuple

# --- guess_type ---


def test_guess_type_returns_tuple() -> None:
    result = Mimetypes.guess_type(Str("file.html"))
    assert isinstance(result, Tuple)
    assert result.len()._value == 2


def test_guess_type_known_html() -> None:
    mime, encoding = Mimetypes.guess_type(Str("file.html"))
    assert isinstance(mime, Str)
    assert mime._value == "text/html"
    assert isinstance(encoding, NoneClass)


def test_guess_type_unknown_returns_none_pair() -> None:
    mime, encoding = Mimetypes.guess_type(Str("file.zzz-no-such-extension"))
    assert mime is none
    assert encoding is none


# --- guess_extension ---


def test_guess_extension_known() -> None:
    ext = Mimetypes.guess_extension(Str("text/html"))
    assert isinstance(ext, Str)
    assert ext._value.startswith(".")


def test_guess_extension_unknown_returns_none() -> None:
    ext = Mimetypes.guess_extension(Str("application/x-bogus-poop-type"))
    assert ext is none


# --- guess_all_extensions ---


def test_guess_all_extensions_known() -> None:
    exts = Mimetypes.guess_all_extensions(Str("text/html"))
    assert isinstance(exts, List)
    assert exts.len()._value >= 1


def test_guess_all_extensions_unknown_returns_empty_list() -> None:
    exts = Mimetypes.guess_all_extensions(Str("application/x-bogus-poop-type"))
    assert isinstance(exts, List)
    assert exts.len()._value == 0


# --- add_type ---


def test_add_type_returns_none() -> None:
    result = Mimetypes.add_type(Str("application/x-poop-mt-test"), Str(".pmt"))
    assert result is none


def test_add_type_makes_extension_guessable() -> None:
    Mimetypes.add_type(Str("application/x-poop-test-after"), Str(".pmta"))
    mime, _ = Mimetypes.guess_type(Str("file.pmta"))
    assert mime == Str("application/x-poop-test-after")


# --- Constants ---


def test_suffix_map_is_dict_of_str() -> None:
    assert isinstance(Mimetypes.suffix_map, Dict)
    if Mimetypes.suffix_map.len()._value > 0:
        # Spot-check one entry's type.
        first_key = next(iter(Mimetypes.suffix_map))
        assert isinstance(first_key, Str)


def test_encodings_map_is_dict() -> None:
    assert isinstance(Mimetypes.encodings_map, Dict)


def test_types_map_is_dict() -> None:
    assert isinstance(Mimetypes.types_map, Dict)
    assert Mimetypes.types_map.len()._value > 50  # reasonable population


def test_common_types_is_dict() -> None:
    assert isinstance(Mimetypes.common_types, Dict)


def test_knownfiles_is_list_of_str() -> None:
    assert isinstance(Mimetypes.knownfiles, List)


# --- strict flag ---


def test_guess_type_strict_false_accepts_non_strict() -> None:
    # Non-strict mode resolves more types via common_types.
    mime_strict, _ = Mimetypes.guess_type(Str("file.midi"), false)
    assert isinstance(mime_strict, Str)


def test_guess_type_strict_true_matches_default() -> None:
    default_mime, _ = Mimetypes.guess_type(Str("file.html"))
    strict_mime, _ = Mimetypes.guess_type(Str("file.html"), true)
    assert default_mime == strict_mime


# --- init ---


def test_init_with_no_args_returns_none() -> None:
    result = Mimetypes.init()
    assert result is none


# --- MimeTypes class ---


def test_mime_types_class_instance() -> None:
    mt = MimeTypes()
    mime, _ = mt.guess_type(Str("file.html"))
    assert mime == Str("text/html")


def test_mime_types_class_add_type() -> None:
    mt = MimeTypes()
    mt.add_type(Str("application/x-instance-type"), Str(".inst"))
    mime, _ = mt.guess_type(Str("file.inst"))
    assert mime == Str("application/x-instance-type")


def test_mime_types_class_guess_extension() -> None:
    mt = MimeTypes()
    ext = mt.guess_extension(Str("text/html"))
    assert isinstance(ext, Str)


def test_mime_types_class_guess_all_extensions() -> None:
    mt = MimeTypes()
    exts = mt.guess_all_extensions(Str("text/html"))
    assert isinstance(exts, List)


# --- Interpreter integration ---


def test_mimetypes_reachable_via_interpreter() -> None:
    Interpreter().run_source('mimetypes.guess_type("file.html").at(0).print()')


def test_MimeTypes_class_reachable_via_interpreter() -> None:
    Interpreter().run_source(
        'mt = MimeTypes()\nmt.guess_type("file.html").at(0).print()'
    )
