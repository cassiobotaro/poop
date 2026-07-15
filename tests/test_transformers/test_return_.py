import ast

from poop.interpreter import Interpreter
from poop.transformers.return_ import ReturnTransformer


def _transform(src: str) -> ast.Module:
    return ReturnTransformer().transform(ast.parse(src))


def _last_stmt(func: ast.FunctionDef | ast.AsyncFunctionDef) -> ast.stmt:
    return func.body[-1]


def test_falloff_appends_poop_none_return() -> None:
    tree = _transform("def f():\n    x = 1")
    func = tree.body[0]
    assert isinstance(func, ast.FunctionDef)
    last = _last_stmt(func)
    assert isinstance(last, ast.Return)
    assert isinstance(last.value, ast.Name)
    assert last.value.id == "_poop_none"


def test_bare_return_becomes_poop_none() -> None:
    tree = _transform("def f():\n    return")
    func = tree.body[0]
    assert isinstance(func, ast.FunctionDef)
    ret = func.body[0]
    assert isinstance(ret, ast.Return)
    assert isinstance(ret.value, ast.Name)
    assert ret.value.id == "_poop_none"


def test_explicit_return_value_is_untouched() -> None:
    tree = _transform("def f():\n    return 5")
    func = tree.body[0]
    assert isinstance(func, ast.FunctionDef)
    assert len(func.body) == 1  # no trailing return appended
    ret = func.body[0]
    assert isinstance(ret, ast.Return)
    assert isinstance(ret.value, ast.Constant)


def test_init_is_skipped() -> None:
    tree = _transform("class C:\n    def __init__(self):\n        self.x = 1")
    cls = tree.body[0]
    assert isinstance(cls, ast.ClassDef)
    init = cls.body[0]
    assert isinstance(init, ast.FunctionDef)
    # No trailing `return _poop_none` (would make __init__ return non-None).
    assert not isinstance(_last_stmt(init), ast.Return)


def test_void_method_answers_none_via_interpreter() -> None:
    Interpreter().run_source(
        "class Greeter:\n"
        "    def greet(self):\n"
        "        'hi'.print()\n"
        "Greeter().greet().is_none().print()"
    )


def test_init_still_constructs_via_interpreter() -> None:
    Interpreter().run_source(
        "class Box:\n"
        "    def __init__(self, v):\n"
        "        self._v = v\n"
        "    def value(self):\n"
        "        return self._v\n"
        "Box(7).value().print()"
    )
