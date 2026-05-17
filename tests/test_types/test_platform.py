from poop.interpreter import Interpreter
from poop.types.int import Int
from poop.types.platform import Platform, Uname
from poop.types.string import Str
from poop.types.tuple import Tuple


def test_system_returns_str() -> None:
    assert isinstance(Platform.system(), Str)


def test_release_returns_str() -> None:
    assert isinstance(Platform.release(), Str)


def test_version_returns_str() -> None:
    assert isinstance(Platform.version(), Str)


def test_machine_returns_str() -> None:
    assert isinstance(Platform.machine(), Str)


def test_processor_returns_str() -> None:
    assert isinstance(Platform.processor(), Str)


def test_node_returns_str() -> None:
    assert isinstance(Platform.node(), Str)


def test_platform_no_args() -> None:
    assert isinstance(Platform.platform(), Str)


def test_platform_with_args() -> None:
    from poop.types.boolean import false, true

    assert isinstance(Platform.platform(true, false), Str)


def test_uname_returns_uname() -> None:
    u = Platform.uname()
    assert isinstance(u, Uname)


def test_uname_properties_are_str() -> None:
    u = Platform.uname()
    for attr in ("system", "node", "release", "version", "machine", "processor"):
        assert isinstance(getattr(u, attr), Str)


def test_architecture_returns_tuple() -> None:
    a = Platform.architecture()
    assert isinstance(a, Tuple)
    assert a.len() == Int(2)


def test_python_version_returns_str() -> None:
    assert isinstance(Platform.python_version(), Str)


def test_python_version_tuple_returns_tuple() -> None:
    t = Platform.python_version_tuple()
    assert isinstance(t, Tuple)
    assert t.len() == Int(3)


def test_python_branch_returns_str() -> None:
    assert isinstance(Platform.python_branch(), Str)


def test_python_build_returns_tuple_of_str() -> None:
    t = Platform.python_build()
    assert isinstance(t, Tuple)
    assert t.len() == Int(2)


def test_python_compiler_returns_str() -> None:
    assert isinstance(Platform.python_compiler(), Str)


def test_python_implementation_returns_str() -> None:
    assert isinstance(Platform.python_implementation(), Str)


def test_python_revision_returns_str() -> None:
    assert isinstance(Platform.python_revision(), Str)


def test_mac_ver_returns_tuple() -> None:
    t = Platform.mac_ver()
    assert isinstance(t, Tuple)
    assert t.len() == Int(3)


def test_win32_ver_returns_tuple() -> None:
    t = Platform.win32_ver()
    assert isinstance(t, Tuple)
    assert t.len() == Int(4)


def test_libc_ver_returns_tuple() -> None:
    t = Platform.libc_ver()
    assert isinstance(t, Tuple)
    assert t.len() == Int(2)


def test_platform_class_ref() -> None:
    assert Platform.Uname is Uname


# --- Interpreter integration ---


def test_platform_via_interpreter() -> None:
    Interpreter().run_source("platform.system().print()")
