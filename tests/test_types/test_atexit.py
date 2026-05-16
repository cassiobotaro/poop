from poop.interpreter import Interpreter
from poop.types.atexit import Atexit
from poop.types.none import none


def test_register_returns_func() -> None:
    fired: list[int] = []

    def callback() -> None:
        fired.append(1)

    result = Atexit.register(callback)
    assert result is callback
    Atexit.unregister(callback)


def test_unregister_returns_none() -> None:
    def callback() -> None:
        pass

    Atexit.register(callback)
    assert Atexit.unregister(callback) is none


def test_register_with_args() -> None:
    captured: list[tuple] = []

    def callback(*args, **kwargs) -> None:
        captured.append((args, kwargs))

    Atexit.register(callback, 1, 2, key="value")
    Atexit._run_exitfuncs()
    Atexit._clear()
    assert (1, 2) in (args for args, _ in captured)


def test_run_exitfuncs_returns_none() -> None:
    fired: list[bool] = []

    def callback() -> None:
        fired.append(True)

    Atexit.register(callback)
    assert Atexit._run_exitfuncs() is none
    Atexit._clear()
    assert fired == [True]


def test_clear_returns_none() -> None:
    def callback() -> None:
        pass

    Atexit.register(callback)
    assert Atexit._clear() is none


# --- Interpreter integration ---


def test_atexit_via_interpreter() -> None:
    # Lambdas are auto-wrapped as POOP Blocks by the BlockTransformer.
    Interpreter().run_source(
        "cb = lambda: 0\natexit.register(cb)\natexit.unregister(cb)"
    )
