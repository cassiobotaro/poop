import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from poop.cli import main


def test_cli_runs_valid_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    f = tmp_path / "ok.py"
    f.write_text('"hi".print()\n', encoding="utf-8")
    with patch.object(sys, "argv", ["poop", str(f)]):
        main()
    assert capsys.readouterr().out == "hi\n"


def test_cli_exits_with_error_on_invalid_code(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    f = tmp_path / "bad.py"
    f.write_text("print('x')\n", encoding="utf-8")
    with patch.object(sys, "argv", ["poop", str(f)]):
        with pytest.raises(SystemExit) as exc_info:
            main()
    assert exc_info.value.code == 1
    assert "poop:" in capsys.readouterr().err
