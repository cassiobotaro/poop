from poop.errors import (
    ExecutionError,
    TransformError,
    ValidationError,
    format_error,
)


def test_format_error_draws_gutter_and_caret() -> None:
    out = format_error(ValidationError("print is forbidden", 1, 0), "print(x)")
    assert out == "poop: print is forbidden\n  1 | print(x)\n    | ^"


def test_format_error_caret_sits_under_the_column() -> None:
    out = format_error(ValidationError("nope", 1, 4), "    print(x)")
    assert out.splitlines()[-1] == "    |     ^"


def test_format_error_drops_the_position_the_gutter_already_shows() -> None:
    # The gutter carries the line and the caret the column; repeating them in
    # the message is the noise `:explain`-less REPL users read twice.
    out = format_error(ValidationError("nope", 1, 0), "print(x)")
    assert "(line 1, col 0)" not in out


def test_format_error_keeps_the_position_without_source() -> None:
    # Nothing to point at — the suffix is the only clue left.
    assert format_error(ValidationError("nope", 4, 8), None) == (
        "poop: nope (line 4, col 8)"
    )


def test_format_error_keeps_the_position_when_lineno_is_out_of_range() -> None:
    assert format_error(ValidationError("nope", 99, 8), "x = 1") == (
        "poop: nope (line 99, col 8)"
    )


def test_format_error_execution_error_draws_no_caret() -> None:
    # ExecutionError carries no col_offset: a line, but no column to point at.
    out = format_error(ExecutionError("KeyError: 'zzz'", 1), "d.at('zzz')")
    assert out == "poop: KeyError: 'zzz'\n  1 | d.at('zzz')"


def test_format_error_transform_error_keeps_its_own_suffix() -> None:
    # `(transformer X)` is not a position, so nothing else states it.
    assert format_error(TransformError("boom", "FooTransformer"), "x = 1") == (
        "poop: boom (transformer FooTransformer)"
    )


def test_format_error_multiline_source_points_at_the_reported_line() -> None:
    source = "x = 1\ny = 2\nprint(x)"
    out = format_error(ValidationError("print is forbidden", 3, 0), source)
    assert "  3 | print(x)" in out
    assert "x = 1" not in out
