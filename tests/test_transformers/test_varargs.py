import ast
import re

import pytest

from poop.errors import ExecutionError
from poop.interpreter import Interpreter
from poop.transformers.varargs import VarargsTransformer


def _transform(src: str) -> ast.Module:
    return VarargsTransformer().transform(ast.parse(src))


def test_vararg_gets_tuple_prologue() -> None:
    tree = _transform("def f(*args):\n    return args")
    func = tree.body[0]
    assert isinstance(func, ast.FunctionDef)
    first = func.body[0]
    assert isinstance(first, ast.Assign)
    assert isinstance(first.value, ast.Call)
    assert isinstance(first.value.func, ast.Name)
    assert first.value.func.id == "_poop_tuple_from"


def test_kwarg_gets_dict_prologue() -> None:
    tree = _transform("def f(**kw):\n    return kw")
    func = tree.body[0]
    assert isinstance(func, ast.FunctionDef)
    first = func.body[0]
    assert isinstance(first, ast.Assign)
    assert isinstance(first.value, ast.Call)
    assert isinstance(first.value.func, ast.Name)
    assert first.value.func.id == "_poop_dict_from_kwargs"


def test_no_variadic_params_unchanged() -> None:
    tree = _transform("def f(a, b):\n    return a")
    func = tree.body[0]
    assert isinstance(func, ast.FunctionDef)
    assert isinstance(func.body[0], ast.Return)


def test_vararg_is_poop_tuple_via_interpreter() -> None:
    Interpreter().run_source(
        "class C:\n"
        "    def total(self, *args):\n"
        "        return args.class_name()\n"
        "C().total(1, 2).print()"
    )


def test_kwarg_is_poop_dict_via_interpreter() -> None:
    Interpreter().run_source(
        "class C:\n"
        "    def opts(self, **kw):\n"
        "        return kw.at('x')\n"
        "C().opts(x=99).print()"
    )


def test_lambda_vararg_is_poop_tuple_via_interpreter() -> None:
    Interpreter().run_source("f = lambda *xs: xs.len()\nf(1, 2, 3).print()")


def test_lambda_kwarg_gets_dict_conversion() -> None:
    # `lambda **kw: ...` wraps kw so the body sees a POOP Dict, mirroring how a
    # `def`'s **kwargs are converted.
    tree = _transform("f = lambda **kw: kw")
    assert "_poop_dict_from_kwargs" in ast.unparse(tree)


# --- the call site: the other end of the variadic round trip ---


def _out(capsys: pytest.CaptureFixture[str], source: str) -> str:
    Interpreter().run_source(source)
    return capsys.readouterr().out.strip()


def test_kwargs_splat_reaches_a_kwargs_parameter(
    capsys: pytest.CaptureFixture[str],
) -> None:
    # `**` demands raw `str` keys and a POOP Dict carries `Str`, so this used
    # to answer Python's own `keywords must be strings` about a POOP object.
    # `.upper()` on the way out pins that the value is still a POOP Str.
    assert (
        _out(
            capsys,
            "class C:\n"
            "    def m(self, **kw):\n"
            "        return kw.at('a').upper()\n"
            "C().m(**{'a': 'x'}).print()",
        )
        == "X"
    )


def test_kwargs_splat_binds_named_parameters(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert (
        _out(
            capsys,
            "class C:\n"
            "    def m(self, a, b):\n"
            "        return a + b\n"
            "C().m(**{'a': 1, 'b': 2}).print()",
        )
        == "3"
    )


def test_kwargs_splat_merges_with_named_keywords(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert (
        _out(
            capsys,
            "class C:\n"
            "    def m(self, **kw):\n"
            "        return kw\n"
            "C().m(**{'z': 9}, y=8).print()",
        )
        == "{'z': 9, 'y': 8}"
    )


def test_a_mapping_proxy_splats_too(capsys: pytest.CaptureFixture[str]) -> None:
    assert (
        _out(
            capsys,
            "class C:\n"
            "    def m(self, **kw):\n"
            "        return kw\n"
            "C().m(**{'a': 1}.keys().mapping()).print()",
        )
        == "{'a': 1}"
    )


def test_raise_carries_a_kwargs_splat(capsys: pytest.CaptureFixture[str]) -> None:
    # `_poop_raise(Exc, **kw)` is a call like any other, and RaiseTransformer
    # runs before this one — so the splat is covered there too.
    assert (
        _out(
            capsys,
            "class MyError(Exception):\n"
            "    def __init__(self, msg, code):\n"
            "        super().__init__(msg)\n"
            "        self.code = code\n"
            "kw = {'code': 7}\n"
            "Try(lambda: MyError.raise_('b', **kw))"
            ".except_(MyError, lambda e: e.print()).run()",
        )
        == "MyError: b"
    )


@pytest.mark.parametrize(
    ("splat", "expected"),
    [
        ("{1: 2}", "keywords must be strings"),
        ("5", "argument after ** must be a mapping, not int"),
    ],
    ids=["non_str_key", "non_mapping"],
)
def test_a_bad_splat_keeps_cpythons_own_wording(splat: str, expected: str) -> None:
    # Both reach CPython raw — the faithful-unwrap idiom — so the message is
    # true and, for the key case, about a key the program actually wrote.
    with pytest.raises(ExecutionError, match=re.escape(expected)):
        Interpreter().run_source(
            f"class C:\n    def m(self, **kw):\n        return kw\nC().m(**{splat})"
        )
