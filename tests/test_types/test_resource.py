import resource as _stdlib_resource

import pytest

from poop.interpreter import Interpreter
from poop.types.float import Float
from poop.types.int import Int
from poop.types.resource import Resource, RUsage
from poop.types.tuple import Tuple


def test_getrlimit_returns_tuple_of_ints() -> None:
    result = Resource.getrlimit(Resource.RLIMIT_NOFILE)
    assert isinstance(result, Tuple)
    soft = result.at(Int(0))
    hard = result.at(Int(1))
    assert isinstance(soft, Int)
    assert isinstance(hard, Int)


def test_setrlimit_round_trip() -> None:
    current = Resource.getrlimit(Resource.RLIMIT_CORE)
    try:
        # Set the same value back — no permission change required.
        Resource.setrlimit(Resource.RLIMIT_CORE, current)
        after = Resource.getrlimit(Resource.RLIMIT_CORE)
        assert after == current
    finally:
        Resource.setrlimit(Resource.RLIMIT_CORE, current)


def test_getrusage_returns_rusage() -> None:
    usage = Resource.getrusage(Resource.RUSAGE_SELF)
    assert isinstance(usage, RUsage)


def test_rusage_properties() -> None:
    usage = Resource.getrusage(Resource.RUSAGE_SELF)
    for name in (
        "ru_utime",
        "ru_stime",
    ):
        attr = getattr(usage, name)
        assert isinstance(attr, Float)
    for name in (
        "ru_maxrss",
        "ru_ixrss",
        "ru_idrss",
        "ru_isrss",
        "ru_minflt",
        "ru_majflt",
        "ru_nswap",
        "ru_inblock",
        "ru_oublock",
        "ru_msgsnd",
        "ru_msgrcv",
        "ru_nsignals",
        "ru_nvcsw",
        "ru_nivcsw",
    ):
        attr = getattr(usage, name)
        assert isinstance(attr, Int)


def test_rusage_repr() -> None:
    usage = Resource.getrusage(Resource.RUSAGE_SELF)
    assert "struct_rusage" in repr(usage)


def test_getpagesize_returns_int() -> None:
    size = Resource.getpagesize()
    assert isinstance(size, Int)
    assert size._value > 0


def test_rlim_infinity_is_int() -> None:
    assert isinstance(Resource.RLIM_INFINITY, Int)


def test_constants_are_ints_when_present() -> None:
    for name in (
        "RLIMIT_CPU",
        "RLIMIT_FSIZE",
        "RLIMIT_DATA",
        "RLIMIT_STACK",
        "RLIMIT_CORE",
        "RLIMIT_NOFILE",
        "RLIMIT_AS",
        "RUSAGE_SELF",
        "RUSAGE_CHILDREN",
    ):
        attr = getattr(Resource, name)
        assert attr is None or isinstance(attr, Int)


@pytest.mark.skipif(
    not hasattr(_stdlib_resource, "prlimit"),
    reason="prlimit is Linux-only",
)
def test_prlimit_read_only() -> None:
    import os

    pid = Int(os.getpid())
    result = Resource.prlimit(pid, Resource.RLIMIT_NOFILE)
    assert isinstance(result, Tuple)


def test_resource_class_refs() -> None:
    assert Resource.RUsage is RUsage


# --- Interpreter integration ---


def test_resource_via_interpreter() -> None:
    Interpreter().run_source("resource.getpagesize().print()")
