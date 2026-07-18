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


def test_format_error_caret_lands_under_a_column_after_non_ascii() -> None:
    # ast reports col_offset as a UTF-8 byte offset; treating it as a character
    # index pushed the caret one column right per extra byte.
    source = 'y = ("ção", x)'
    out = format_error(
        ValidationError("nope", 1, source.encode("utf-8").index(b"x")), source
    )
    caret_line = out.splitlines()[-1]
    assert caret_line.index("^") == out.splitlines()[1].index("x")


def test_format_error_counts_lines_the_way_the_tokenizer_does() -> None:
    # str.splitlines() breaks on \f, which the tokenizer does not — every line
    # after a form feed would be numbered out of step with the parser.
    source = "x = 1\n\fy = 2\nz = 3"
    out = format_error(ValidationError("nope", 2, 0), source)
    assert "\fy = 2" in out


def test_render_error_without_source_is_a_plain_red_message() -> None:
    # No source to point at: render_error falls back to the bare `poop:` line,
    # coloured red, with neither gutter nor caret.
    from poop.errors import render_error

    text = render_error(ValidationError("nope", 4, 8), None)
    assert text.plain == "poop: nope (line 4, col 8)"
    assert text.style == "red"


def test_render_error_with_line_but_no_column_draws_no_caret() -> None:
    # ExecutionError carries a line but no col_offset: the highlighted gutter is
    # drawn, but there is nothing to point a caret at.
    from poop.errors import render_error

    text = render_error(ExecutionError("KeyError: 'zzz'", 1), "d.at('zzz')")
    assert "^" not in text.plain
    assert "d.at('zzz')" in text.plain
