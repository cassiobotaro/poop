import pytest

from poop.interpreter import Interpreter
from poop.types.boolean import Boolean
from poop.types.csv import CSV, Dialect, DictReader, DictWriter, Reader, Sniffer, Writer
from poop.types.dict import Dict
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import none
from poop.types.string import Str
from poop.types.tuple import Tuple

# --- Reader ---


def test_reader_from_str() -> None:
    source = Str("a,b,c\n1,2,3\n")
    reader = Reader(source)
    rows = list(reader)
    assert rows == [
        List(Str("a"), Str("b"), Str("c")),
        List(Str("1"), Str("2"), Str("3")),
    ]


def test_reader_from_list_of_str() -> None:
    source = List(Str("x,y\n"), Str("1,2\n"))
    reader = Reader(source)
    rows = list(reader)
    assert rows[0] == List(Str("x"), Str("y"))


def test_reader_line_num_after_iter() -> None:
    reader = Reader(Str("a,b\n1,2\n"))
    list(reader)
    assert reader.line_num._value >= 2


def test_reader_dialect_property() -> None:
    reader = Reader(Str("a,b"), dialect=Str("excel"))
    assert reader.dialect == Str("excel")


def test_reader_with_tab_dialect() -> None:
    reader = Reader(Str("a\tb\n1\t2\n"), dialect=Str("excel-tab"))
    rows = list(reader)
    assert rows[0] == List(Str("a"), Str("b"))


# --- Writer ---


def test_writer_writerow() -> None:
    w = Writer()
    w.writerow(List(Str("a"), Str("b")))
    w.writerow(List(Str("1"), Str("2")))
    assert w.getvalue() == Str("a,b\r\n1,2\r\n")


def test_writer_writerows() -> None:
    w = Writer()
    w.writerows(List(List(Str("a"), Str("b")), List(Str("1"), Str("2"))))
    assert w.getvalue() == Str("a,b\r\n1,2\r\n")


def test_writer_unwraps_int_cells() -> None:
    w = Writer()
    w.writerow(List(Int(1), Int(2), Int(3)))
    assert w.getvalue() == Str("1,2,3\r\n")


def test_writer_none_cell_empties() -> None:
    w = Writer()
    w.writerow(List(Str("a"), none, Str("c")))
    assert w.getvalue() == Str("a,,c\r\n")


def test_writer_rejects_non_row() -> None:
    w = Writer()
    with pytest.raises(TypeError):
        w.writerows(List(Int(1)))


def test_writer_with_quote_all() -> None:
    w = Writer(quoting=CSV.QUOTE_ALL)
    w.writerow(List(Str("a"), Str("b")))
    assert '"a","b"' in w.getvalue()._value


# --- DictReader ---


def test_dict_reader_yields_dicts() -> None:
    source = Str("name,age\nAlice,30\nBob,42\n")
    reader = DictReader(source)
    rows = list(reader)
    assert rows[0] == Dict().at_put(Str("name"), Str("Alice")).at_put(
        Str("age"), Str("30")
    )


def test_dict_reader_fieldnames_property() -> None:
    source = Str("a,b\n1,2\n")
    reader = DictReader(source)
    list(reader)  # consume to populate fieldnames
    assert reader.fieldnames == List(Str("a"), Str("b"))


def test_dict_reader_explicit_fieldnames() -> None:
    source = Str("alice,30\nbob,42\n")
    reader = DictReader(source, fieldnames=List(Str("name"), Str("age")))
    rows = list(reader)
    assert rows[0].at(Str("name")) == Str("alice")
    assert rows[0].at(Str("age")) == Str("30")


def test_dict_reader_line_num() -> None:
    reader = DictReader(Str("a,b\n1,2\n"))
    list(reader)
    assert isinstance(reader.line_num, Int)


# --- DictWriter ---


def test_dict_writer_writeheader_and_writerow() -> None:
    w = DictWriter(List(Str("name"), Str("age")))
    w.writeheader()
    w.writerow(Dict().at_put(Str("name"), Str("Alice")).at_put(Str("age"), Int(30)))
    assert "name,age" in w.getvalue()._value
    assert "Alice,30" in w.getvalue()._value


def test_dict_writer_writerows() -> None:
    w = DictWriter(List(Str("k"), Str("v")))
    rows = List(
        Dict().at_put(Str("k"), Str("a")).at_put(Str("v"), Str("1")),
        Dict().at_put(Str("k"), Str("b")).at_put(Str("v"), Str("2")),
    )
    w.writerows(rows)
    out = w.getvalue()
    assert "a,1" in out._value
    assert "b,2" in out._value


def test_dict_writer_rejects_non_dict() -> None:
    w = DictWriter(List(Str("k")))
    with pytest.raises(TypeError):
        w.writerows(List(Str("not-a-dict")))


def test_dict_writer_none_value() -> None:
    w = DictWriter(List(Str("k")))
    w.writerow(Dict().at_put(Str("k"), none))
    # `none` is unwrapped to an empty string per POOP convention.
    # CPython quotes the empty value depending on the dialect.
    assert w.getvalue()._value in {"\r\n", '""\r\n'}


def test_dict_writer_restval_default() -> None:
    w = DictWriter(List(Str("a"), Str("b")), restval=Str("-"))
    w.writerow(Dict().at_put(Str("a"), Str("x")))
    assert "x,-" in w.getvalue()._value


# --- Module-level factories ---


def test_csv_reader_factory() -> None:
    r = CSV.reader(Str("a,b\n"))
    assert isinstance(r, Reader)


def test_csv_writer_factory() -> None:
    w = CSV.writer()
    assert isinstance(w, Writer)


# --- Dialect API ---


def test_list_dialects() -> None:
    result = CSV.list_dialects()
    assert isinstance(result, List)
    # CPython ships at least "excel", "excel-tab", "unix".
    names = [n._value for n in result if isinstance(n, Str)]
    assert "excel" in names


def test_register_and_unregister_dialect() -> None:
    CSV.register_dialect(Str("poop-dialect"), delimiter=Str("|"))
    try:
        names = CSV.list_dialects()
        assert any(isinstance(n, Str) and n._value == "poop-dialect" for n in names)
    finally:
        CSV.unregister_dialect(Str("poop-dialect"))


def test_get_dialect_existing() -> None:
    d = CSV.get_dialect(Str("excel"))
    assert isinstance(d, Dialect)
    assert d.delimiter == Str(",")


def test_field_size_limit_read_only() -> None:
    current = CSV.field_size_limit()
    assert isinstance(current, Int)


def test_field_size_limit_set_round_trip() -> None:
    original = CSV.field_size_limit()
    try:
        new = CSV.field_size_limit(Int(1024))
        assert new == original
        assert CSV.field_size_limit() == Int(1024)
    finally:
        CSV.field_size_limit(original)


# --- Sniffer ---


def test_sniffer_has_header() -> None:
    sample = Str("name,age\nalice,30\nbob,40\n")
    sniffer = Sniffer()
    from poop.types.boolean import Boolean

    result = sniffer.has_header(sample)
    assert isinstance(result, Boolean)


def test_sniffer_sniff_returns_dialect() -> None:
    sample = Str("a;b;c\n1;2;3\n")
    sniffer = Sniffer()
    d = sniffer.sniff(sample)
    assert isinstance(d, Dialect)
    assert d.delimiter == Str(";")
    assert isinstance(d.doublequote, Boolean)
    assert isinstance(d.skipinitialspace, Boolean)
    assert isinstance(d.quoting, Int)


def test_sniffer_sniff_with_delimiters() -> None:
    sample = Str("a|b|c\n1|2|3\n")
    sniffer = Sniffer()
    d = sniffer.sniff(sample, delimiters=Str("|"))
    assert d.delimiter == Str("|")


# --- Constants / errors ---


def test_quoting_constants_are_ints() -> None:
    assert isinstance(CSV.QUOTE_ALL, Int)
    assert isinstance(CSV.QUOTE_MINIMAL, Int)
    assert isinstance(CSV.QUOTE_NONNUMERIC, Int)
    assert isinstance(CSV.QUOTE_NONE, Int)
    assert isinstance(CSV.QUOTE_STRINGS, Int)
    assert isinstance(CSV.QUOTE_NOTNULL, Int)


def test_csv_error_class_exposed() -> None:
    assert issubclass(CSV.Error, Exception)


def test_dialect_class_refs_exposed() -> None:
    assert CSV.Dialect is not None
    assert CSV.excel is not None
    assert CSV.excel_tab is not None
    assert CSV.unix_dialect is not None


# --- Tuple rows ---


def test_writer_accepts_tuple_row() -> None:
    w = Writer()
    w.writerow(Tuple(Str("a"), Str("b")))
    assert w.getvalue() == Str("a,b\r\n")


# --- Interpreter integration ---


def test_csv_reader_via_interpreter() -> None:
    # Reader is a Python iterator; verify it constructs cleanly through
    # the interpreter — iteration is exercised on the Python side.
    Interpreter().run_source('csv.reader("a,b\\n1,2\\n")\n')


def test_csv_writer_via_interpreter() -> None:
    Interpreter().run_source(
        'w = csv.writer()\nw.writerow(["a", "b"])\nw.getvalue().print()'
    )
