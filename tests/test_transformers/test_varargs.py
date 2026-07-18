import ast

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
