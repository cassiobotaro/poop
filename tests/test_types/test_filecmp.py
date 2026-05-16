from pathlib import Path as _PyPath

import pytest

from poop.interpreter import Interpreter
from poop.types.boolean import false, true
from poop.types.dict import Dict
from poop.types.filecmp import Dircmp, Filecmp
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import none
from poop.types.path import Path
from poop.types.string import Str
from poop.types.tuple import Tuple

# --- cmp ---


def test_cmp_identical_files(tmp_path: _PyPath) -> None:
    a = tmp_path / "a.txt"
    b = tmp_path / "b.txt"
    a.write_text("hello")
    b.write_text("hello")
    assert Filecmp.cmp(Path(Str(str(a))), Path(Str(str(b)))) is true


def test_cmp_different_files(tmp_path: _PyPath) -> None:
    a = tmp_path / "a.txt"
    b = tmp_path / "b.txt"
    a.write_text("hello")
    b.write_text("world")
    assert Filecmp.cmp(Path(Str(str(a))), Path(Str(str(b)))) is false


def test_cmp_accepts_str_paths(tmp_path: _PyPath) -> None:
    a = tmp_path / "a.txt"
    b = tmp_path / "b.txt"
    a.write_text("x")
    b.write_text("x")
    assert Filecmp.cmp(Str(str(a)), Str(str(b))) is true


def test_cmp_shallow_off(tmp_path: _PyPath) -> None:
    a = tmp_path / "a.txt"
    b = tmp_path / "b.txt"
    a.write_text("same")
    b.write_text("same")
    assert Filecmp.cmp(Path(Str(str(a))), Path(Str(str(b))), shallow=false) is true


# --- cmpfiles ---


def test_cmpfiles_splits_match_mismatch_errors(tmp_path: _PyPath) -> None:
    d1 = tmp_path / "left"
    d2 = tmp_path / "right"
    d1.mkdir()
    d2.mkdir()
    (d1 / "same.txt").write_text("ok")
    (d2 / "same.txt").write_text("ok")
    (d1 / "diff.txt").write_text("a")
    (d2 / "diff.txt").write_text("b")
    (d1 / "missing.txt").write_text("only-on-left")

    result = Filecmp.cmpfiles(
        Path(Str(str(d1))),
        Path(Str(str(d2))),
        List(Str("same.txt"), Str("diff.txt"), Str("missing.txt")),
    )
    assert isinstance(result, Tuple)
    match = result.at(Int(0))
    mismatch = result.at(Int(1))
    errors = result.at(Int(2))
    assert match == List(Str("same.txt"))
    assert mismatch == List(Str("diff.txt"))
    assert errors == List(Str("missing.txt"))


# --- clear_cache ---


def test_clear_cache_returns_none() -> None:
    assert Filecmp.clear_cache() is none


# --- DEFAULT_IGNORES ---


def test_default_ignores_constant() -> None:
    assert isinstance(Filecmp.DEFAULT_IGNORES, List)
    assert Filecmp.DEFAULT_IGNORES.len()._value > 0


# --- Dircmp ---


def _populate_two_trees(tmp_path: _PyPath) -> tuple[_PyPath, _PyPath]:
    left = tmp_path / "left"
    right = tmp_path / "right"
    left.mkdir()
    right.mkdir()
    (left / "same.txt").write_text("identical")
    (right / "same.txt").write_text("identical")
    (left / "diff.txt").write_text("alpha")
    (right / "diff.txt").write_text("beta")
    (left / "left-only.txt").write_text("L")
    (right / "right-only.txt").write_text("R")
    return left, right


def test_dircmp_left_only(tmp_path: _PyPath) -> None:
    left, right = _populate_two_trees(tmp_path)
    cmp = Dircmp(Path(Str(str(left))), Path(Str(str(right))))
    assert isinstance(cmp.left_only, List)
    assert cmp.left_only == List(Str("left-only.txt"))


def test_dircmp_right_only(tmp_path: _PyPath) -> None:
    left, right = _populate_two_trees(tmp_path)
    cmp = Dircmp(Path(Str(str(left))), Path(Str(str(right))))
    assert cmp.right_only == List(Str("right-only.txt"))


def test_dircmp_same_and_diff(tmp_path: _PyPath) -> None:
    left, right = _populate_two_trees(tmp_path)
    cmp = Dircmp(Path(Str(str(left))), Path(Str(str(right))))
    assert cmp.same_files == List(Str("same.txt"))
    assert cmp.diff_files == List(Str("diff.txt"))


def test_dircmp_common(tmp_path: _PyPath) -> None:
    left, right = _populate_two_trees(tmp_path)
    cmp = Dircmp(Path(Str(str(left))), Path(Str(str(right))))
    common = cmp.common
    assert isinstance(common, List)
    assert common.includes(Str("same.txt"))
    assert common.includes(Str("diff.txt"))


def test_dircmp_subdirs_returns_dict(tmp_path: _PyPath) -> None:
    left = tmp_path / "L"
    right = tmp_path / "R"
    (left / "shared").mkdir(parents=True)
    (right / "shared").mkdir(parents=True)
    (left / "shared" / "x.txt").write_text("x")
    (right / "shared" / "x.txt").write_text("x")
    cmp = Dircmp(Path(Str(str(left))), Path(Str(str(right))))
    subs = cmp.subdirs
    assert isinstance(subs, Dict)
    nested = subs.at(Str("shared"))
    assert isinstance(nested, Dircmp)


def test_dircmp_left_and_right_properties(tmp_path: _PyPath) -> None:
    left, right = _populate_two_trees(tmp_path)
    cmp = Dircmp(Path(Str(str(left))), Path(Str(str(right))))
    assert cmp.left == Str(str(left))
    assert cmp.right == Str(str(right))


def test_dircmp_ignore_skips_names(tmp_path: _PyPath) -> None:
    left, right = _populate_two_trees(tmp_path)
    cmp = Dircmp(
        Path(Str(str(left))),
        Path(Str(str(right))),
        ignore=List(Str("diff.txt")),
    )
    assert not cmp.diff_files.includes(Str("diff.txt"))


def test_dircmp_report_returns_none(
    tmp_path: _PyPath, capsys: pytest.CaptureFixture[str]
) -> None:
    left, right = _populate_two_trees(tmp_path)
    cmp = Dircmp(Path(Str(str(left))), Path(Str(str(right))))
    assert cmp.report() is none
    captured = capsys.readouterr().out
    assert "Differing files" in captured


def test_dircmp_report_str_returns_str(tmp_path: _PyPath) -> None:
    left, right = _populate_two_trees(tmp_path)
    cmp = Dircmp(Path(Str(str(left))), Path(Str(str(right))))
    report = cmp.report_str()
    assert isinstance(report, Str)
    assert "Differing files" in report._value


def test_dircmp_common_dirs_and_funny(tmp_path: _PyPath) -> None:
    left, right = _populate_two_trees(tmp_path)
    cmp = Dircmp(Path(Str(str(left))), Path(Str(str(right))))
    assert isinstance(cmp.common_dirs, List)
    assert isinstance(cmp.common_funny, List)
    assert isinstance(cmp.common_files, List)
    assert isinstance(cmp.funny_files, List)


def test_dircmp_report_partial_and_full_closure(
    tmp_path: _PyPath, capsys: pytest.CaptureFixture[str]
) -> None:
    left, right = _populate_two_trees(tmp_path)
    cmp = Dircmp(Path(Str(str(left))), Path(Str(str(right))))
    assert cmp.report_partial_closure() is none
    assert cmp.report_full_closure() is none
    capsys.readouterr()  # drain output


# --- Interpreter integration ---


def test_filecmp_cmp_reachable_via_interpreter(tmp_path: _PyPath) -> None:
    a = tmp_path / "a.txt"
    b = tmp_path / "b.txt"
    a.write_text("ok")
    b.write_text("ok")
    Interpreter().run_source(f'filecmp.cmp(Path("{a}"), Path("{b}")).print()')


def test_dircmp_reachable_via_interpreter(tmp_path: _PyPath) -> None:
    left, right = _populate_two_trees(tmp_path)
    Interpreter().run_source(
        f'Dircmp(Path("{left}"), Path("{right}")).same_files.print()'
    )
